const fs = require("fs");

const envPath = process.argv[2];
if (!envPath) throw new Error("Environment path is required.");
const env = Object.fromEntries(fs.readFileSync(envPath, "utf8").split(/\r?\n/).filter((line) => line && !line.startsWith("#") && line.includes("=")).map((line) => [line.slice(0, line.indexOf("=")), line.slice(line.indexOf("=") + 1)]));
const token = env.DISCORD_BOT_TOKEN;
const guildId = env.DISCORD_GUILD_ID;
if (!token || !guildId) throw new Error("Discord production configuration is incomplete.");

const P = {
  MANAGE_CHANNELS: 1n << 4n,
  VIEW_CHANNEL: 1n << 10n,
  SEND_MESSAGES: 1n << 11n,
  READ_MESSAGE_HISTORY: 1n << 16n,
};
const memberAccess = P.VIEW_CHANNEL | P.SEND_MESSAGES | P.READ_MESSAGE_HISTORY;
const lockedLegacyNames = new Set(["known-issues", "class-overview", "warrior", "magician", "bowman", "thief", "pirate", "cygnus-knights", "aran", "skill-changelog"]);

async function discord(path, options = {}) {
  for (let attempt = 0; attempt < 5; attempt += 1) {
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
      const route = path.replace(/\d{10,}/g, ":id");
      throw new Error(`discord_request_failed status=${response.status} method=${options.method || "GET"} route=${route}`);
    }
    return response.status === 204 ? null : response.json();
  }
  throw new Error("Discord rate limit did not clear.");
}

function stable(value) {
  if (Array.isArray(value)) return value.map(stable).sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b)));
  if (value && typeof value === "object") return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stable(value[key])]));
  return value;
}
const same = (left, right) => JSON.stringify(stable(left)) === JSON.stringify(stable(right));

function mergeForumTags(existing, desired) {
  const pending = new Map(desired.map((tag) => [tag.name, tag]));
  const merged = existing.map((tag) => {
    const update = pending.get(tag.name);
    if (!update) return tag;
    pending.delete(tag.name);
    return { ...tag, moderated: update.moderated };
  });
  for (const tag of pending.values()) merged.push(tag);
  return merged;
}

async function ensureChannel(channels, spec) {
  if (lockedLegacyNames.has(spec.name)) throw new Error(`Refusing to mutate protected legacy channel ${spec.name}.`);
  let channel = channels.find((item) => item.name === spec.name);
  if (channel && channel.type !== spec.type) throw new Error(`Channel ${spec.name} exists as type ${channel.type}, expected ${spec.type}; refusing to create a duplicate.`);
  if (!channel) {
    channel = await discord(`/guilds/${guildId}/channels`, { method: "POST", body: JSON.stringify(spec) });
    channels.push(channel);
    return channel;
  }
  const body = {};
  for (const key of ["parent_id", "topic", "rate_limit_per_user", "nsfw"]) if (spec[key] !== undefined && channel[key] !== spec[key]) body[key] = spec[key];
  if (spec.flags !== undefined) {
    const flags = (channel.flags || 0) | spec.flags;
    if (channel.flags !== flags) body.flags = flags;
  }
  if (spec.permission_overwrites && !same(channel.permission_overwrites, spec.permission_overwrites)) body.permission_overwrites = spec.permission_overwrites;
  if (spec.available_tags) {
    const tags = mergeForumTags(channel.available_tags || [], spec.available_tags);
    if (!same(channel.available_tags || [], tags)) body.available_tags = tags;
  }
  if (spec.default_reaction_emoji) {
    const actual = channel.default_reaction_emoji || {};
    if (actual.emoji_name !== spec.default_reaction_emoji.emoji_name || actual.emoji_id !== (spec.default_reaction_emoji.emoji_id || null)) body.default_reaction_emoji = spec.default_reaction_emoji;
  }
  if (Object.keys(body).length) channel = await discord(`/channels/${channel.id}`, { method: "PATCH", body: JSON.stringify(body) });
  return channel;
}

async function ensureBotMessage(channelId, botId, marker, content) {
  const messages = await discord(`/channels/${channelId}/messages?limit=100`);
  const existing = messages.find((message) => message.author?.id === botId && message.content.includes(marker));
  const body = JSON.stringify({ content, allowed_mentions: { parse: [] } });
  if (!existing) await discord(`/channels/${channelId}/messages`, { method: "POST", body });
  else if (existing.content !== content) await discord(`/channels/${channelId}/messages/${existing.id}`, { method: "PATCH", body });
}

async function cleanupLegacyStatusMessages(channelId, botId) {
  const messages = await discord(`/channels/${channelId}/messages?limit=100`);
  const obsolete = messages.filter((message) => message.author?.id === botId && (message.content.startsWith("**EverLeaf Status Alert**") || message.content.includes("Server availability and planned maintenance notices will appear here")));
  for (const message of obsolete) await discord(`/channels/${channelId}/messages/${message.id}`, { method: "DELETE" });
  return obsolete.length;
}

(async () => {
  const [bot, roles, channels] = await Promise.all([
    discord("/users/@me"),
    discord(`/guilds/${guildId}/roles`),
    discord(`/guilds/${guildId}/channels`),
  ]);
  const botMember = await discord(`/guilds/${guildId}/members/${bot.id}`);
  const botRole = roles.find((role) => role.managed && botMember.roles.includes(role.id));
  const moderator = roles.find((role) => role.name === "Moderator" && !role.managed);
  const gameMaster = roles.find((role) => role.name === "Game Master" && !role.managed);
  const supporter = roles.find((role) => role.id === env.DISCORD_SUPPORTER_ROLE_ID);
  if (!botRole || !moderator || !gameMaster || !supporter) throw new Error("Required EverLeaf Discord roles are missing.");
  if ((BigInt(botRole.permissions) & P.MANAGE_CHANNELS) === 0n) throw new Error("EverLeaf bot is missing Manage Channels.");

  const category = (name) => {
    const found = channels.find((item) => item.type === 4 && item.name === name);
    if (!found) throw new Error(`Required category ${name} is missing.`);
    return found;
  };
  const categories = {
    start: category("🍃 START HERE"), news: category("📢 NEWS & STATUS"), community: category("🌿 COMMUNITY"),
    help: category("🛠 GAME HELP"), guides: category("📚 CLASS GUIDES"), events: category("🎉 EVENTS & GROUPS"),
    voice: category("🔊 VOICE LOUNGES"), supporters: category("💚 SUPPORTERS"), staff: category("🔒 STAFF"),
  };

  const allow = (id) => ({ id, type: 0, allow: memberAccess.toString(), deny: "0" });
  const readOnly = [
    { id: guildId, type: 0, allow: (P.VIEW_CHANNEL | P.READ_MESSAGE_HISTORY).toString(), deny: P.SEND_MESSAGES.toString() },
    allow(botRole.id), allow(moderator.id), allow(gameMaster.id),
  ];
  const supporterOverwrites = [{ id: guildId, type: 0, allow: "0", deny: P.VIEW_CHANNEL.toString() }, allow(supporter.id), allow(moderator.id), allow(gameMaster.id), allow(botRole.id)];
  const staffOverwrites = [{ id: guildId, type: 0, allow: "0", deny: P.VIEW_CHANNEL.toString() }, allow(moderator.id), allow(gameMaster.id), allow(botRole.id)];
  const suggestionsTags = ["Gameplay", "QoL", "Content", "Classes", "Economy", "Events", "Website / Launcher", "Discord", "Other"].map((name) => ({ name, moderated: false })).concat(["Under Review", "Planned", "Accepted", "Implemented", "Declined", "Considering"].map((name) => ({ name, moderated: true })));
  const bugTags = ["New"].map((name) => ({ name, moderated: false })).concat(["Investigating", "Confirmed", "Fix In Progress", "Fixed", "Cannot Reproduce"].map((name) => ({ name, moderated: true })), ["Map / NPC", "Quest", "Gameplay", "Mob / Boss", "Item / Drop", "Client / Launcher", "Server / Connection", "Rooted Content"].map((name) => ({ name, moderated: false })));
  const spec = (name, type, parent, topic, options = {}) => ({ name, type, parent_id: parent.id, topic, ...options });
  const specs = [
    spec("welcome", 0, categories.start, "Start here for the EverLeaf overview, next steps, and official links.", { permission_overwrites: readOnly }),
    spec("rules", 0, categories.start, "Community and game rules. Participation means accepting these rules.", { permission_overwrites: readOnly }),
    spec("downloads-and-links", 0, categories.start, "Verified EverLeaf website, launcher, downloads, account, vote, and Discord links.", { permission_overwrites: readOnly }),
    spec("announcements", 0, categories.news, "Official EverLeaf announcements and maintenance notices.", { permission_overwrites: readOnly }),
    spec("server-status", 0, categories.news, "Live game, database, website, and 20-channel status.", { permission_overwrites: readOnly }),
    spec("patch-notes", 0, categories.news, "EverLeaf gameplay, website, launcher, and infrastructure updates.", { permission_overwrites: readOnly }),
    spec("general", 0, categories.community, "General EverLeaf community discussion.", { rate_limit_per_user: 2 }),
    spec("introductions", 0, categories.community, "Introduce yourself to the EverLeaf community."),
    spec("screenshots-and-media", 0, categories.community, "Share EverLeaf screenshots, clips, art, and community media."),
    spec("suggestions", 15, categories.community, "EverLeaf suggestions and feedback. Search first, use one idea per post, and select the closest category tag.", { rate_limit_per_user: 300, available_tags: suggestionsTags, default_reaction_emoji: { emoji_name: "👍" }, flags: 16 }),
    spec("help-and-support", 0, categories.help, "Player help, launcher support, account guidance, and common troubleshooting.", { rate_limit_per_user: 3 }),
    spec("bug-reports", 15, categories.help, "Closed beta bug reports. Search known issues and existing posts first. Include expected behavior, actual behavior, reproduction steps, character, CH1–CH20, map/NPC, and safe evidence.", { rate_limit_per_user: 300, available_tags: bugTags, default_reaction_emoji: { emoji_name: "👍" }, flags: 16 }),
    spec("class-help", 0, categories.help, "Build, skill, equipment, and class questions for MapleStory v83."),
    spec("events", 0, categories.events, "Official and community in-game event discussion."),
    spec("party-finder", 0, categories.events, "Find parties for bosses, quests, training, and party content.", { rate_limit_per_user: 3 }),
    spec("guild-recruitment", 0, categories.events, "Guild recruitment and guild-seeking posts.", { rate_limit_per_user: 10 }),
    spec("supporter-lounge", 0, categories.supporters, "Private community lounge for confirmed EverLeaf supporters.", { permission_overwrites: supporterOverwrites }),
    spec("staff-chat", 0, categories.staff, "Private staff coordination.", { permission_overwrites: staffOverwrites }),
    spec("staff-logs", 0, categories.staff, "Private operational and moderation notes.", { permission_overwrites: staffOverwrites }),
  ];

  const managed = new Map();
  for (const item of specs) managed.set(item.name, await ensureChannel(channels, item));
  const voice = [];
  for (const [position, name] of ["General", "Party 1", "Party 2", "Bossing", "AFK"].entries()) {
    const channel = await ensureChannel(channels, { name, type: 2, parent_id: categories.voice.id });
    voice.push({ id: channel.id, position, parent_id: categories.voice.id });
  }

  const categoryOrder = [categories.start, categories.news, categories.community, categories.help, categories.guides, categories.events, categories.voice, categories.supporters, categories.staff];
  await discord(`/guilds/${guildId}/channels`, { method: "PATCH", body: JSON.stringify([
    ...categoryOrder.map((item, position) => ({ id: item.id, position })),
    ...specs.map((item, position) => ({ id: managed.get(item.name).id, position, parent_id: item.parent_id })),
    ...voice,
  ]) });

  await ensureBotMessage(managed.get("welcome").id, bot.id, "# Welcome to EverLeaf", "# Welcome to EverLeaf\nEnhanced Classic MapleStory v83 with quality-of-life improvements, long-term progression, and no pay-to-win.\n\n1. Read #rules.\n2. Get the game and launcher from #downloads-and-links.\n3. Create and link your account on the website.\n4. Check #known-issues before reporting a problem.\n5. Use the matching help, suggestion, party, or class channel so answers stay easy to find.");
  await ensureBotMessage(managed.get("rules").id, bot.id, "# EverLeaf Community Rules", "# EverLeaf Community Rules\n1. Be respectful; harassment, hate speech, threats, and targeted abuse are not allowed.\n2. No cheating, exploiting, botting, real-money trading, or malicious files.\n3. Keep credentials private. Staff will never ask for your password.\n4. Use the appropriate channel and avoid spam, duplicate posts, and disruptive advertising.\n5. Report exploits privately to staff; never publish reproduction instructions.\n6. Follow staff direction and the website Terms of Service.");
  await ensureBotMessage(managed.get("downloads-and-links").id, bot.id, "# Official EverLeaf Links", "# Official EverLeaf Links\nWebsite: https://everleafms.online\nDownloads and launcher: https://everleafms.online/downloads\nAccount and Discord linking: https://everleafms.online/account\nVote and rewards: https://everleafms.online/vote\n\nOnly use files and links published through the official website, launcher, or this channel.");
  await ensureBotMessage(managed.get("announcements").id, bot.id, "Official EverLeaf announcements", "Official EverLeaf announcements, launch updates, events, and planned maintenance will be published here.");
  await ensureBotMessage(managed.get("patch-notes").id, bot.id, "EverLeaf gameplay, website, and launcher patch notes", "EverLeaf gameplay, website, launcher, infrastructure, and community-system patch notes will be published here.");
  await ensureBotMessage(managed.get("help-and-support").id, bot.id, "# Getting Help", "# Getting Help\nFor account or launcher help, describe the problem and any safe error message. For reproducible defects, use #bug-reports. For build and skill questions, use #class-help. Never post passwords, tokens, private account data, or sensitive logs.");
  const cleaned = await cleanupLegacyStatusMessages(managed.get("server-status").id, bot.id);

  console.log("discord_reconcile_unlocked_scope=ok");
  console.log(`discord_unlocked_channels_ready=${specs.length}`);
  console.log("discord_existing_channels_deleted=0");
  console.log(`discord_legacy_status_messages_deleted=${cleaned}`);
  console.log(`discord_locked_legacy_channels_preserved=${lockedLegacyNames.size}`);
  console.log("discord_locked_legacy_reason=explicit_everyone_manage_channels_and_manage_roles_denies");
})().catch((error) => {
  const safe = String(error.message).replace(/[A-Za-z0-9_-]{32,}/g, "[redacted]");
  console.error(`discord_reconcile_unlocked_scope_failed ${safe}`);
  process.exitCode = 1;
});
