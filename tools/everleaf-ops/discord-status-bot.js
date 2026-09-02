const net = require("net");

const DEFAULT_CHANNEL_ID = "1542847686716301404";
const DEFAULT_MESSAGE_ID = "1542847705485938750";
const DEFAULT_STATUS_API = "http://127.0.0.1:3000/api/status";
const DEFAULT_LOGIN_PORT = 8484;
const CHECK_INTERVAL_MS = 30_000;
const REQUIRED_CONSECUTIVE_CHECKS = 3;
const HEARTBEAT_EDIT_MS = 5 * 60_000;

function requireEnv(name) {
  const value = process.env[name];
  if (!value) throw new Error(`${name} is required.`);
  return value;
}

function portOnline(port) {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    let settled = false;
    const done = (result) => {
      if (settled) return;
      settled = true;
      socket.destroy();
      resolve(result);
    };

    socket.setTimeout(2_000);
    socket.once("connect", () => done(true));
    socket.once("timeout", () => done(false));
    socket.once("error", () => done(false));
    socket.connect(port, "127.0.0.1");
  });
}

async function request(url, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 5_000);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

function healthSignature(status) {
  return JSON.stringify({
    statusApiOnline: status.statusApiOnline,
    loginOnline: status.loginOnline,
    databaseOnline: status.databaseOnline,
    onlineChannels: status.onlineChannels,
    totalChannels: status.totalChannels,
  });
}

class StabilityGate {
  constructor(requiredChecks = REQUIRED_CONSECUTIVE_CHECKS) {
    this.requiredChecks = requiredChecks;
    this.accepted = null;
    this.candidateSignature = null;
    this.candidateCount = 0;
  }

  observe(status) {
    if (!this.accepted) {
      this.accepted = status;
      return status;
    }

    const acceptedSignature = healthSignature(this.accepted);
    const nextSignature = healthSignature(status);
    if (nextSignature === acceptedSignature) {
      this.candidateSignature = null;
      this.candidateCount = 0;
      this.accepted = { ...this.accepted, players: status.players };
      return this.accepted;
    }

    if (nextSignature !== this.candidateSignature) {
      this.candidateSignature = nextSignature;
      this.candidateCount = 1;
    } else {
      this.candidateCount += 1;
    }

    if (this.candidateCount >= this.requiredChecks) {
      this.accepted = status;
      this.candidateSignature = null;
      this.candidateCount = 0;
    } else if (status.statusApiOnline) {
      this.accepted = { ...this.accepted, players: status.players };
    }

    return this.accepted;
  }
}

function normalizeApiStatus(apiStatus, loginOnline) {
  const totalChannels = Number(apiStatus?.totalChannels);
  const onlineChannels = Number(apiStatus?.channels);
  if (!Number.isInteger(totalChannels) || totalChannels < 1) {
    throw new Error("Status API returned an invalid totalChannels value.");
  }
  if (!Number.isInteger(onlineChannels) || onlineChannels < 0 || onlineChannels > totalChannels) {
    throw new Error("Status API returned an invalid channels value.");
  }

  return {
    statusApiOnline: true,
    loginOnline,
    databaseOnline: apiStatus.databaseOnline === true,
    onlineChannels,
    totalChannels,
    players: Number.isFinite(Number(apiStatus.players)) ? Number(apiStatus.players) : 0,
  };
}

function offlineStatus(previous) {
  return {
    statusApiOnline: false,
    loginOnline: false,
    databaseOnline: false,
    onlineChannels: 0,
    totalChannels: previous?.totalChannels || 20,
    players: 0,
  };
}

function buildEmbed(status) {
  const gameOnline = status.loginOnline && status.onlineChannels > 0;
  const fullyOperational = gameOnline
    && status.onlineChannels === status.totalChannels
    && status.databaseOnline
    && status.statusApiOnline;
  const completelyOffline = !status.loginOnline && status.onlineChannels === 0;
  const label = fullyOperational
    ? "All Systems Operational"
    : completelyOffline
      ? "Server Offline"
      : "Partial Service";
  const color = completelyOffline ? 0xED4245 : fullyOperational ? 0x57F287 : 0xFEE75C;
  const state = (value) => value ? "Online" : "Offline";

  return {
    title: "EverLeaf Server Status",
    description: `**${label}**`,
    color,
    fields: [
      { name: "Game Server", value: state(gameOnline), inline: true },
      { name: "Login Server", value: state(status.loginOnline), inline: true },
      { name: "Players Online", value: `**${status.players}**`, inline: true },
      {
        name: "Channels",
        value: `**${status.onlineChannels}/${status.totalChannels} Online**`,
        inline: true,
      },
      { name: "Database", value: state(status.databaseOnline), inline: true },
      { name: "Status API", value: state(status.statusApiOnline), inline: true },
    ],
    footer: { text: "EverLeaf | Automatic live status" },
    timestamp: new Date().toISOString(),
  };
}

function buildComponents() {
  return [{
    type: 1,
    components: [
      { type: 2, style: 5, label: "Website", url: "https://everleafms.online" },
      { type: 2, style: 5, label: "Download", url: "https://everleafms.online/downloads" },
      { type: 2, style: 5, label: "Account", url: "https://everleafms.online/account" },
      { type: 2, style: 5, label: "Vote", url: "https://everleafms.online/vote" },
    ],
  }];
}

async function run() {
  const botToken = requireEnv("DISCORD_BOT_TOKEN");
  const channelId = process.env.DISCORD_STATUS_CHANNEL_ID || DEFAULT_CHANNEL_ID;
  const messageId = process.env.DISCORD_STATUS_MESSAGE_ID || DEFAULT_MESSAGE_ID;
  const statusApi = process.env.EVERLEAF_STATUS_API || DEFAULT_STATUS_API;
  const loginPort = Number(process.env.EVERLEAF_LOGIN_PORT || DEFAULT_LOGIN_PORT);
  const gate = new StabilityGate();
  let lastPayloadSignature = null;
  let lastEditAt = 0;
  let running = false;

  async function updateStatus() {
    if (running) return;
    running = true;
    try {
      let observed;
      try {
        const [response, loginOnline] = await Promise.all([
          request(statusApi),
          portOnline(loginPort),
        ]);
        if (!response.ok) throw new Error(`Status API returned ${response.status}.`);
        observed = normalizeApiStatus(await response.json(), loginOnline);
      } catch (error) {
        console.error(new Date().toISOString(), `status_check_failed=${error.message}`);
        observed = offlineStatus(gate.accepted);
      }

      const stable = gate.observe(observed);
      const embed = buildEmbed(stable);
      const payloadSignature = JSON.stringify({ ...embed, timestamp: undefined });
      const now = Date.now();
      if (payloadSignature === lastPayloadSignature && now - lastEditAt < HEARTBEAT_EDIT_MS) return;

      const response = await request(
        `https://discord.com/api/v10/channels/${channelId}/messages/${messageId}`,
        {
          method: "PATCH",
          headers: {
            Authorization: `Bot ${botToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            content: "",
            embeds: [embed],
            components: buildComponents(),
            allowed_mentions: { parse: [] },
          }),
        },
      );
      if (!response.ok) throw new Error(`Discord status update failed: ${response.status}.`);

      lastPayloadSignature = payloadSignature;
      lastEditAt = now;
      console.log(
        new Date().toISOString(),
        `status_updated players=${stable.players} channels=${stable.onlineChannels}/${stable.totalChannels}`,
      );
    } catch (error) {
      console.error(new Date().toISOString(), error.message);
    } finally {
      running = false;
    }
  }

  await updateStatus();
  setInterval(updateStatus, CHECK_INTERVAL_MS);
}

if (require.main === module) {
  run().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}

module.exports = { StabilityGate, buildComponents, buildEmbed, healthSignature, normalizeApiStatus, offlineStatus };
