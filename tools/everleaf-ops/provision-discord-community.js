const fs = require("fs");

const envPath = process.argv[2];
if (!envPath) throw new Error("Environment path is required.");
const env = Object.fromEntries(fs.readFileSync(envPath, "utf8").split(/\r?\n/).filter((line) => line && !line.startsWith("#") && line.includes("=")).map((line) => [line.slice(0, line.indexOf("=")), line.slice(line.indexOf("=") + 1)]));
const token = env.DISCORD_BOT_TOKEN;
const guildId = env.DISCORD_GUILD_ID;
if (!token || !guildId) throw new Error("Discord production configuration is incomplete.");

const P = {
  KICK_MEMBERS: 1n << 1n,
  BAN_MEMBERS: 1n << 2n,
  VIEW_AUDIT_LOG: 1n << 7n,
  VIEW_CHANNEL: 1n << 10n,
  SEND_MESSAGES: 1n << 11n,
  MANAGE_MESSAGES: 1n << 13n,
  READ_MESSAGE_HISTORY: 1n << 16n,
  MANAGE_NICKNAMES: 1n << 27n,
  MANAGE_THREADS: 1n << 34n,
  MODERATE_MEMBERS: 1n << 40n,
};
const memberAccess = P.VIEW_CHANNEL | P.SEND_MESSAGES | P.READ_MESSAGE_HISTORY;
const moderatorPermissions = P.KICK_MEMBERS | P.VIEW_AUDIT_LOG | P.VIEW_CHANNEL | P.SEND_MESSAGES | P.MANAGE_MESSAGES | P.READ_MESSAGE_HISTORY | P.MANAGE_NICKNAMES | P.MANAGE_THREADS | P.MODERATE_MEMBERS;
const gmPermissions = moderatorPermissions | P.BAN_MEMBERS;

async function discord(path, options = {}) {
  for (let attempt = 0; attempt < 4; attempt += 1) {
    const response = await fetch(`https://discord.com/api/v10${path}`, {
      ...options,
      headers: { Authorization: `Bot ${token}`, "Content-Type": "application/json", ...(options.headers || {}) },
    });
    if (response.status === 429) {
      const limited = await response.json();
      await new Promise((resolve) => setTimeout(resolve, Math.ceil(Number(limited.retry_after || 1) * 1000)));
      continue;
    }
    if (!response.ok) {
      const detail = (await response.text()).replace(/[A-Za-z0-9_-]{40,}/g, "[redacted]").slice(0, 300);
      throw new Error(`Discord API returned ${response.status} for ${options.method || "GET"} ${path}: ${detail}`);
    }
    return response.status === 204 ? null : response.json();
  }
  throw new Error(`Discord rate limit did not clear for ${path}.`);
}

async function ensureRole(roles, spec) {
  let role = roles.find((item) => item.name === spec.name && !item.managed);
  if (!role) {
    role = await discord(`/guilds/${guildId}/roles`, { method: "POST", body: JSON.stringify(spec) });
    roles.push(role);
  }
  return role;
}

async function ensureCategory(channels, name, fallbackName, overwrites = undefined) {
  let channel = channels.find((item) => item.type === 4 && item.name === name);
  if (!channel && fallbackName) {
    channel = channels.find((item) => item.type === 4 && item.name === fallbackName);
    if (channel) channel = await discord(`/channels/${channel.id}`, { method: "PATCH", body: JSON.stringify({ name, permission_overwrites: overwrites }) });
  }
  if (!channel) {
    channel = await discord(`/guilds/${guildId}/channels`, { method: "POST", body: JSON.stringify({ name, type: 4, permission_overwrites: overwrites }) });
    channels.push(channel);
  }
  return channel;
}

async function ensureChannel(channels, spec) {
  let channel = channels.find((item) => item.type === spec.type && item.name === spec.name);
  let created = false;
  if (!channel) {
    channel = await discord(`/guilds/${guildId}/channels`, { method: "POST", body: JSON.stringify(spec) });
    channels.push(channel);
    created = true;
  } else if (channel.parent_id !== spec.parent_id || (spec.topic && channel.topic !== spec.topic)) {
    channel = await discord(`/channels/${channel.id}`, { method: "PATCH", body: JSON.stringify({ parent_id: spec.parent_id, topic: spec.topic }) });
  }
  return { channel, created };
}

async function post(channelId, content) {
  await discord(`/channels/${channelId}/messages`, { method: "POST", body: JSON.stringify({ content, allowed_mentions: { parse: [] } }) });
}

(async () => {
  const bot = await discord("/users/@me");
  const member = await discord(`/guilds/${guildId}/members/${bot.id}`);
  const roles = await discord(`/guilds/${guildId}/roles`);
  const botRole = roles.find((role) => role.managed && member.roles.includes(role.id));
  const supporter = roles.find((role) => role.id === env.DISCORD_SUPPORTER_ROLE_ID);
  if (!botRole || !supporter) throw new Error("Bot or Supporter role was not found.");
  const botPermissions = BigInt(botRole.permissions);
  const requiredBotPermissions = (1n << 4n) | P.VIEW_CHANNEL | P.SEND_MESSAGES | P.READ_MESSAGE_HISTORY | (1n << 28n);
  if ((botPermissions & requiredBotPermissions) !== requiredBotPermissions) throw new Error("Bot is missing required limited permissions.");

  const moderator = await ensureRole(roles, { name: "Moderator", color: 0x4aa3df, permissions: moderatorPermissions.toString(), hoist: true, mentionable: false });
  const gameMaster = await ensureRole(roles, { name: "Game Master", color: 0x2f9b43, permissions: gmPermissions.toString(), hoist: true, mentionable: false });
  await ensureRole(roles, { name: "Closed Beta Tester", color: 0xa4c639, permissions: "0", hoist: false, mentionable: true });

  const everyoneDeny = { id: guildId, type: 0, allow: "0", deny: P.VIEW_CHANNEL.toString() };
  const allow = (id) => ({ id, type: 0, allow: memberAccess.toString(), deny: "0" });
  const staffOverwrites = [everyoneDeny, allow(moderator.id), allow(gameMaster.id), allow(botRole.id)];
  const supporterOverwrites = [everyoneDeny, allow(supporter.id), allow(moderator.id), allow(gameMaster.id), allow(botRole.id)];
  const readOnlyOverwrites = [
    { id: guildId, type: 0, allow: (P.VIEW_CHANNEL | P.READ_MESSAGE_HISTORY).toString(), deny: P.SEND_MESSAGES.toString() },
    allow(botRole.id), allow(moderator.id), allow(gameMaster.id),
  ];

  const channels = await discord(`/guilds/${guildId}/channels`);
  const categories = {
    start: await ensureCategory(channels, "🍃 START HERE"),
    news: await ensureCategory(channels, "📢 NEWS & STATUS"),
    community: await ensureCategory(channels, "🌿 COMMUNITY", "Text Channels"),
    help: await ensureCategory(channels, "🛠 GAME HELP"),
    events: await ensureCategory(channels, "🎉 EVENTS & GROUPS"),
    supporters: await ensureCategory(channels, "💚 SUPPORTERS", null, supporterOverwrites),
    staff: await ensureCategory(channels, "🔒 STAFF", null, staffOverwrites),
    voice: await ensureCategory(channels, "🔊 VOICE LOUNGES", "Voice Channels"),
  };

  const textSpecs = [
    ["welcome", categories.start, "Start here for the EverLeaf overview and official links.", readOnlyOverwrites],
    ["rules", categories.start, "Community and game rules. Participation means accepting these rules.", readOnlyOverwrites],
    ["downloads-and-links", categories.start, "Official EverLeaf website, launcher, downloads, and account links.", readOnlyOverwrites],
    ["announcements", categories.news, "Official EverLeaf announcements.", readOnlyOverwrites],
    ["server-status", categories.news, "Server availability and maintenance notices.", readOnlyOverwrites],
    ["patch-notes", categories.news, "EverLeaf updates and patch notes.", readOnlyOverwrites],
    ["general", categories.community, "General EverLeaf community discussion."],
    ["introductions", categories.community, "Introduce yourself to the EverLeaf community."],
    ["screenshots-and-media", categories.community, "Share screenshots, clips, art, and community media."],
    ["suggestions", categories.community, "Constructive suggestions for EverLeaf."],
    ["help-and-support", categories.help, "Player help, launcher support, and account guidance."],
    ["bug-reports", categories.help, "Report reproducible gameplay, website, or launcher defects."],
    ["class-help", categories.help, "Build, skill, and class discussion for MapleStory v83."],
    ["events", categories.events, "Community and in-game event discussion."],
    ["party-finder", categories.events, "Find parties for bosses, quests, and party content."],
    ["guild-recruitment", categories.events, "Guild recruitment and guild-seeking posts."],
    ["supporter-lounge", categories.supporters, "Private community lounge for confirmed EverLeaf supporters."],
    ["staff-chat", categories.staff, "Private staff coordination."],
    ["staff-logs", categories.staff, "Private operational and moderation notes."],
  ];

  const created = new Map();
  for (const [name, parent, topic, overwrites] of textSpecs) {
    const result = await ensureChannel(channels, { name, type: 0, parent_id: parent.id, topic, permission_overwrites: overwrites });
    created.set(name, result);
  }

  const existingGeneralVoice = channels.find((item) => item.type === 2 && item.name === "General");
  if (existingGeneralVoice && existingGeneralVoice.parent_id !== categories.voice.id) await discord(`/channels/${existingGeneralVoice.id}`, { method: "PATCH", body: JSON.stringify({ parent_id: categories.voice.id }) });
  for (const name of ["Party 1", "Party 2", "Bossing", "AFK"]) await ensureChannel(channels, { name, type: 2, parent_id: categories.voice.id });

  if (created.get("welcome")?.created) await post(created.get("welcome").channel.id, "# Welcome to EverLeaf 🍃\nEnhanced Classic MapleStory v83 with thoughtful quality-of-life improvements, long-term progression, and a strict no-pay-to-win policy. Start with #rules, then visit #downloads-and-links.");
  if (created.get("rules")?.created) await post(created.get("rules").channel.id, "# EverLeaf Community Rules\n1. Be respectful; harassment, hate speech, threats, and targeted abuse are not allowed.\n2. No cheating, exploiting, botting, real-money trading, or distributing malicious files.\n3. Keep account credentials private. Staff will never ask for your password.\n4. Use the appropriate channels and avoid spam or disruptive advertising.\n5. Report exploits privately to staff; do not publish reproduction steps.\n6. Follow staff direction and the website Terms of Service. Enforcement may include message removal, timeout, removal, or an in-game sanction.");
  if (created.get("downloads-and-links")?.created) await post(created.get("downloads-and-links").channel.id, "# Official EverLeaf Links\nWebsite: https://everleafms.online\nDownloads and launcher: https://everleafms.online/downloads\nAccount and Discord linking: https://everleafms.online/account\nOnly use files published through the official website and launcher.");
  if (created.get("announcements")?.created) await post(created.get("announcements").channel.id, "Official EverLeaf announcements will be published here. Enable channel notifications if you want launch, maintenance, and event updates.");
  if (created.get("server-status")?.created) await post(created.get("server-status").channel.id, "Server availability and planned maintenance notices will appear here. Live status is also available at https://everleafms.online.");
  if (created.get("patch-notes")?.created) await post(created.get("patch-notes").channel.id, "EverLeaf gameplay, website, and launcher patch notes will be published here.");
  if (created.get("bug-reports")?.created) await post(created.get("bug-reports").channel.id, "When reporting a bug, include what happened, what you expected, the character/map involved, steps to reproduce, and a screenshot if safe. Never post passwords, tokens, private account data, or exploit instructions.");

  console.log(`discord_roles_ready=true`);
  console.log(`discord_categories_ready=${Object.keys(categories).length}`);
  console.log(`discord_text_channels_ready=${textSpecs.length}`);
  console.log(`discord_voice_channels_ready=5`);
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
