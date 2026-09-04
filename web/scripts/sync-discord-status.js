const fs = require("fs");

const envPath = process.argv[2] || ".env";
const statusUrl = process.argv[3] || "http://127.0.0.1:3000/api/status";

const env = Object.fromEntries(
  fs.readFileSync(envPath, "utf8")
    .split(/\r?\n/)
    .filter((line) => line && !line.startsWith("#") && line.includes("="))
    .map((line) => [line.slice(0, line.indexOf("=")), line.slice(line.indexOf("=") + 1)])
);

const token = env.DISCORD_BOT_TOKEN;
const guildId = env.DISCORD_GUILD_ID;
if (!token || !guildId) {
  console.log("discord_status_sync=skipped reason=missing_credentials");
  process.exit(0);
}

async function discord(path, options = {}) {
  const response = await fetch(`https://discord.com/api/v10${path}`, {
    ...options,
    headers: {
      Authorization: `Bot ${token}`,
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  if (!response.ok) {
    const detail = (await response.text()).slice(0, 300);
    throw new Error(`Discord API ${response.status} ${options.method || "GET"} ${path}: ${detail}`);
  }
  return response.status === 204 ? null : response.json();
}

(async () => {
  const statusResponse = await fetch(statusUrl);
  if (!statusResponse.ok) throw new Error(`EverLeaf status endpoint returned ${statusResponse.status}.`);
  const status = await statusResponse.json();
  const live = Number(status.channels || 0);
  const total = Number(status.totalChannels || 0);
  if (!Number.isInteger(total) || total < 1) throw new Error("Invalid totalChannels from EverLeaf status endpoint.");

  const bot = await discord("/users/@me");
  const channels = await discord(`/guilds/${guildId}/channels`);
  const serverStatus = channels.find((channel) => channel.type === 0 && channel.name === "server-status");
  if (!serverStatus) throw new Error("Discord #server-status channel was not found.");

  const state = live === total ? "Online" : live > 0 ? "Degraded" : "Offline";
  const marker = "# EverLeaf Server Status";
  const content = `${marker}\n**${state}** — **${live}/${total} channels online**\nLive status: https://everleafms.online`;
  const topic = `EverLeaf live status: ${live}/${total} channels online. Updated automatically from the production status API.`;

  if (serverStatus.topic !== topic) {
    await discord(`/channels/${serverStatus.id}`, {
      method: "PATCH",
      body: JSON.stringify({ topic }),
    });
  }

  const messages = await discord(`/channels/${serverStatus.id}/messages?limit=100`);
  const existing = messages.find((message) => message.author?.id === bot.id && message.content.includes(marker));
  const body = JSON.stringify({ content, allowed_mentions: { parse: [] } });
  if (existing) {
    if (existing.content !== content) {
      await discord(`/channels/${serverStatus.id}/messages/${existing.id}`, { method: "PATCH", body });
    }
  } else {
    await discord(`/channels/${serverStatus.id}/messages`, { method: "POST", body });
  }

  console.log(`discord_status_sync=ok live=${live} total=${total}`);
})().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
