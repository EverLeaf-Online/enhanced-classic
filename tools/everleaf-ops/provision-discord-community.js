const fs = require("fs");

function reportFailure(step, error) {
  const safeMessage = String(error.message).replace(/[A-Za-z0-9_-]{32,}/g, "[redacted]");
  const result = `discord_reconcile_failed step=${step} ${safeMessage}`;
  if (process.env.DISCORD_RECONCILE_RESULT_PATH) {
    fs.writeFileSync(process.env.DISCORD_RECONCILE_RESULT_PATH, `${result}\n`, { mode: 0o600 });
  }
  console.error(result);
}

const envPath = process.argv[2];
let env;
let token;
let guildId;
try {
  if (!envPath) throw new Error("Environment path is required.");
  env = Object.fromEntries(fs.readFileSync(envPath, "utf8").split(/\r?\n/).filter((line) => line && !line.startsWith("#") && line.includes("=")).map((line) => [line.slice(0, line.indexOf("=")), line.slice(line.indexOf("=") + 1)]));
  token = env.DISCORD_BOT_TOKEN;
  guildId = env.DISCORD_GUILD_ID;
  if (!token || !guildId) throw new Error("Discord production configuration is incomplete.");
} catch (error) {
  reportFailure("load_configuration", error);
  process.exit(1);
}

const P = {
  KICK_MEMBERS: 1n << 1n, BAN_MEMBERS: 1n << 2n, MANAGE_CHANNELS: 1n << 4n,
  MANAGE_GUILD: 1n << 5n, VIEW_AUDIT_LOG: 1n << 7n, VIEW_CHANNEL: 1n << 10n,
  SEND_MESSAGES: 1n << 11n, MANAGE_MESSAGES: 1n << 13n, READ_MESSAGE_HISTORY: 1n << 16n,
  MANAGE_NICKNAMES: 1n << 27n, MANAGE_ROLES: 1n << 28n, MANAGE_THREADS: 1n << 34n,
  MODERATE_MEMBERS: 1n << 40n,
};
const memberAccess = P.VIEW_CHANNEL | P.SEND_MESSAGES | P.READ_MESSAGE_HISTORY;
const moderatorPermissions = P.KICK_MEMBERS | P.VIEW_AUDIT_LOG | P.VIEW_CHANNEL | P.SEND_MESSAGES | P.MANAGE_MESSAGES | P.READ_MESSAGE_HISTORY | P.MANAGE_NICKNAMES | P.MANAGE_THREADS | P.MODERATE_MEMBERS;
const gmPermissions = moderatorPermissions | P.BAN_MEMBERS;

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
  throw new Error(`Discord rate limit did not clear for ${path}.`);
}

function stable(value) {
  if (Array.isArray(value)) return value.map(stable).sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b)));
  if (value && typeof value === "object") return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stable(value[key])]));
  return value;
}
const same = (left, right) => JSON.stringify(stable(left)) === JSON.stringify(stable(right));

async function ensureRole(roles, spec) {
  let role = roles.find((item) => item.name === spec.name && !item.managed);
  if (!role) {
    role = await discord(`/guilds/${guildId}/roles`, { method: "POST", body: JSON.stringify(spec) });
    roles.push(role);
    return role;
  }
  const desired = { color: spec.color, permissions: spec.permissions, hoist: spec.hoist, mentionable: spec.mentionable };
  const actual = { color: role.color, permissions: role.permissions, hoist: role.hoist, mentionable: role.mentionable };
  if (!same(actual, desired)) role = await discord(`/guilds/${guildId}/roles/${role.id}`, { method: "PATCH", body: JSON.stringify(desired) });
  return role;
}

async function ensureCategory(channels, spec) {
  let category = channels.find((item) => item.type === 4 && item.name === spec.name);
  if (!category && spec.fallbackName) category = channels.find((item) => item.type === 4 && item.name === spec.fallbackName);
  if (!category) {
    try {
      category = await discord(`/guilds/${guildId}/channels`, { method: "POST", body: JSON.stringify({ name: spec.name, type: 4, permission_overwrites: spec.permission_overwrites }) });
    } catch (error) {
      throw new Error(`category=${spec.name} ${error.message}`);
    }
    channels.push(category);
    return category;
  }
  const body = {};
  if (category.name !== spec.name) body.name = spec.name;
  if (spec.permission_overwrites && !same(category.permission_overwrites, spec.permission_overwrites)) body.permission_overwrites = spec.permission_overwrites;
  if (Object.keys(body).length) {
    try {
      category = await discord(`/channels/${category.id}`, { method: "PATCH", body: JSON.stringify(body) });
    } catch (error) {
      throw new Error(`category=${spec.name} ${error.message}`);
    }
  }
  return category;
}

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
  let channel = channels.find((item) => item.name === spec.name);
  let created = false;
  if (channel && channel.type !== spec.type) throw new Error(`Channel ${spec.name} exists as type ${channel.type}, expected ${spec.type}; refusing to create a duplicate.`);
  if (!channel) {
    try {
      channel = await discord(`/guilds/${guildId}/channels`, { method: "POST", body: JSON.stringify(spec) });
    } catch (error) {
      throw new Error(`channel=${spec.name} ${error.message}`);
    }
    channels.push(channel);
    return { channel, created: true };
  }
  const body = {};
  for (const key of ["parent_id", "topic", "rate_limit_per_user", "nsfw"]) {
    if (spec[key] !== undefined && channel[key] !== spec[key]) body[key] = spec[key];
  }
  if (spec.flags !== undefined) {
    const desiredFlags = (channel.flags || 0) | spec.flags;
    if (channel.flags !== desiredFlags) body.flags = desiredFlags;
  }
  if (spec.permission_overwrites && !same(channel.permission_overwrites, spec.permission_overwrites)) body.permission_overwrites = spec.permission_overwrites;
  if (spec.available_tags) {
    const tags = mergeForumTags(channel.available_tags || [], spec.available_tags);
    if (!same(channel.available_tags || [], tags)) body.available_tags = tags;
  }
  if (spec.default_reaction_emoji) {
    const actualEmoji = channel.default_reaction_emoji || {};
    if (actualEmoji.emoji_name !== spec.default_reaction_emoji.emoji_name || actualEmoji.emoji_id !== (spec.default_reaction_emoji.emoji_id || null)) {
      body.default_reaction_emoji = spec.default_reaction_emoji;
    }
  }
  if (Object.keys(body).length) {
    try {
      channel = await discord(`/channels/${channel.id}`, { method: "PATCH", body: JSON.stringify(body) });
    } catch (error) {
      throw new Error(`channel=${spec.name} ${error.message}`);
    }
  }
  return { channel, created };
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
  const obsolete = messages.filter((message) => message.author?.id === botId && (
    message.content.startsWith("**EverLeaf Status Alert**")
    || message.content.includes("Server availability and planned maintenance notices will appear here")
  ));
  for (const message of obsolete) {
    await discord(`/channels/${channelId}/messages/${message.id}`, { method: "DELETE" });
  }
  return obsolete.length;
}

const channelSpec = (name, type, parent, topic, options = {}) => ({ name, type, parent_id: parent.id, topic, ...options });
let currentStep = "startup";

(async () => {
  currentStep = "load_bot_and_roles";
  const bot = await discord("/users/@me");
  const member = await discord(`/guilds/${guildId}/members/${bot.id}`);
  const roles = await discord(`/guilds/${guildId}/roles`);
  const botRole = roles.find((role) => role.managed && member.roles.includes(role.id));
  const supporter = roles.find((role) => role.id === env.DISCORD_SUPPORTER_ROLE_ID);
  if (!botRole || !supporter) throw new Error("Bot or Supporter role was not found.");
  const botPermissions = BigInt(botRole.permissions);
  const required = P.MANAGE_CHANNELS | P.VIEW_CHANNEL | P.SEND_MESSAGES | P.READ_MESSAGE_HISTORY | P.MANAGE_ROLES;
  if ((botPermissions & required) !== required) throw new Error("Bot is missing required limited permissions.");

  currentStep = "ensure_staff_roles";
  const moderator = await ensureRole(roles, { name: "Moderator", color: 0x4aa3df, permissions: moderatorPermissions.toString(), hoist: true, mentionable: false });
  const gameMaster = await ensureRole(roles, { name: "Game Master", color: 0x2f9b43, permissions: gmPermissions.toString(), hoist: true, mentionable: false });
  const betaTester = await ensureRole(roles, { name: "Closed Beta Tester", color: 0xa4c639, permissions: "0", hoist: false, mentionable: false });
  currentStep = "reorder_roles";
  await discord(`/guilds/${guildId}/roles`, { method: "PATCH", body: JSON.stringify([
    { id: gameMaster.id, position: 4 }, { id: moderator.id, position: 3 },
    { id: supporter.id, position: 2 }, { id: betaTester.id, position: 1 },
  ]) });

  const everyoneDeny = { id: guildId, type: 0, allow: "0", deny: P.VIEW_CHANNEL.toString() };
  const allow = (id) => ({ id, type: 0, allow: memberAccess.toString(), deny: "0" });
  const staffOverwrites = [everyoneDeny, allow(moderator.id), allow(gameMaster.id), allow(botRole.id)];
  const supporterOverwrites = [everyoneDeny, allow(supporter.id), allow(moderator.id), allow(gameMaster.id), allow(botRole.id)];
  const readOnlyOverwrites = [
    { id: guildId, type: 0, allow: (P.VIEW_CHANNEL | P.READ_MESSAGE_HISTORY).toString(), deny: P.SEND_MESSAGES.toString() },
    allow(botRole.id), allow(moderator.id), allow(gameMaster.id),
  ];

  currentStep = "guild_safety_settings";
  if ((botPermissions & P.MANAGE_GUILD) !== 0n) {
    await discord(`/guilds/${guildId}`, { method: "PATCH", body: JSON.stringify({ verification_level: 1, default_message_notifications: 1, explicit_content_filter: 2 }) });
    console.log("discord_guild_safety_settings=updated");
  } else console.log("discord_guild_safety_settings=skipped_missing_manage_guild");

  currentStep = "ensure_categories";
  const channels = await discord(`/guilds/${guildId}/channels`);
  const categories = {
    start: await ensureCategory(channels, { name: "🍃 START HERE" }),
    news: await ensureCategory(channels, { name: "📢 NEWS & STATUS" }),
    community: await ensureCategory(channels, { name: "🌿 COMMUNITY", fallbackName: "Text Channels" }),
    help: await ensureCategory(channels, { name: "🛠 GAME HELP" }),
    guides: await ensureCategory(channels, { name: "📚 CLASS GUIDES", fallbackName: "Wiki" }),
    events: await ensureCategory(channels, { name: "🎉 EVENTS & GROUPS" }),
    voice: await ensureCategory(channels, { name: "🔊 VOICE LOUNGES", fallbackName: "Voice Channels" }),
    supporters: await ensureCategory(channels, { name: "💚 SUPPORTERS", permission_overwrites: supporterOverwrites }),
    staff: await ensureCategory(channels, { name: "🔒 STAFF", permission_overwrites: staffOverwrites }),
  };

  const tags = {
    suggestions: ["Gameplay", "QoL", "Content", "Classes", "Economy", "Events", "Website / Launcher", "Discord", "Other"].map((name) => ({ name, moderated: false })).concat(["Under Review", "Planned", "Accepted", "Implemented", "Declined", "Considering"].map((name) => ({ name, moderated: true }))),
    bugs: ["New"].map((name) => ({ name, moderated: false })).concat(["Investigating", "Confirmed", "Fix In Progress", "Fixed", "Cannot Reproduce"].map((name) => ({ name, moderated: true })), ["Map / NPC", "Quest", "Gameplay", "Mob / Boss", "Item / Drop", "Client / Launcher", "Server / Connection", "Rooted Content"].map((name) => ({ name, moderated: false }))),
  };

  const specs = [
    channelSpec("welcome", 0, categories.start, "Start here for the EverLeaf overview, next steps, and official links.", { permission_overwrites: readOnlyOverwrites }),
    channelSpec("rules", 0, categories.start, "Community and game rules. Participation means accepting these rules.", { permission_overwrites: readOnlyOverwrites }),
    channelSpec("downloads-and-links", 0, categories.start, "Verified EverLeaf website, launcher, downloads, account, vote, and Discord links.", { permission_overwrites: readOnlyOverwrites }),
    channelSpec("announcements", 0, categories.news, "Official EverLeaf announcements and maintenance notices.", { permission_overwrites: readOnlyOverwrites }),
    channelSpec("server-status", 0, categories.news, "Live game, database, website, and 20-channel status.", { permission_overwrites: readOnlyOverwrites }),
    channelSpec("patch-notes", 0, categories.news, "EverLeaf gameplay, website, launcher, and infrastructure updates.", { permission_overwrites: readOnlyOverwrites }),
    channelSpec("known-issues", 0, categories.news, "Confirmed issues, workarounds, and resolved-problem references.", { permission_overwrites: readOnlyOverwrites }),
    channelSpec("general", 0, categories.community, "General EverLeaf community discussion.", { rate_limit_per_user: 2 }),
    channelSpec("introductions", 0, categories.community, "Introduce yourself to the EverLeaf community."),
    channelSpec("screenshots-and-media", 0, categories.community, "Share EverLeaf screenshots, clips, art, and community media."),
    channelSpec("suggestions", 15, categories.community, "EverLeaf suggestions and feedback. Search first, use one idea per post, and select the closest category tag.", { rate_limit_per_user: 300, available_tags: tags.suggestions, default_reaction_emoji: { emoji_name: "👍" }, flags: 16 }),
    channelSpec("help-and-support", 0, categories.help, "Player help, launcher support, account guidance, and common troubleshooting.", { rate_limit_per_user: 3 }),
    channelSpec("bug-reports", 15, categories.help, "Closed beta bug reports. Search known issues and existing posts first. Include expected behavior, actual behavior, reproduction steps, character, CH1–CH20, map/NPC, and safe evidence.", { rate_limit_per_user: 300, available_tags: tags.bugs, default_reaction_emoji: { emoji_name: "👍" }, flags: 16 }),
    channelSpec("class-help", 0, categories.help, "Build, skill, equipment, and class questions for MapleStory v83."),
    channelSpec("class-overview", 0, categories.guides, "Start here for EverLeaf class availability, progression, and guide navigation.", { permission_overwrites: readOnlyOverwrites }),
    ...[["warrior", "Warrior"], ["magician", "Magician"], ["bowman", "Bowman"], ["thief", "Thief"], ["pirate", "Pirate"], ["cygnus-knights", "Cygnus Knights"], ["aran", "Aran"]].map(([name, label]) => channelSpec(name, 0, categories.guides, `${label} availability, builds, skills, equipment, and EverLeaf balance notes.`, { permission_overwrites: readOnlyOverwrites })),
    channelSpec("skill-changelog", 0, categories.guides, "Authoritative EverLeaf class and skill balance changes.", { permission_overwrites: readOnlyOverwrites }),
    channelSpec("events", 0, categories.events, "Official and community in-game event discussion."),
    channelSpec("party-finder", 0, categories.events, "Find parties for bosses, quests, training, and party content.", { rate_limit_per_user: 3 }),
    channelSpec("guild-recruitment", 0, categories.events, "Guild recruitment and guild-seeking posts.", { rate_limit_per_user: 10 }),
    channelSpec("supporter-lounge", 0, categories.supporters, "Private community lounge for confirmed EverLeaf supporters.", { permission_overwrites: supporterOverwrites }),
    channelSpec("staff-chat", 0, categories.staff, "Private staff coordination.", { permission_overwrites: staffOverwrites }),
    channelSpec("staff-logs", 0, categories.staff, "Private operational and moderation notes.", { permission_overwrites: staffOverwrites }),
  ];

  currentStep = "ensure_channels";
  const managed = new Map();
  for (const spec of specs) managed.set(spec.name, (await ensureChannel(channels, spec)).channel);
  const voice = [];
  for (const [position, name] of ["General", "Party 1", "Party 2", "Bossing", "AFK"].entries()) {
    const channel = (await ensureChannel(channels, { name, type: 2, parent_id: categories.voice.id })).channel;
    voice.push({ id: channel.id, position, parent_id: categories.voice.id });
  }
  const categoryOrder = [categories.start, categories.news, categories.community, categories.help, categories.guides, categories.events, categories.voice, categories.supporters, categories.staff];
  currentStep = "reorder_channels";
  await discord(`/guilds/${guildId}/channels`, { method: "PATCH", body: JSON.stringify([
    ...categoryOrder.map((category, position) => ({ id: category.id, position })),
    ...specs.map((spec, position) => ({ id: managed.get(spec.name).id, position, parent_id: spec.parent_id })),
    ...voice,
  ]) });

  currentStep = "update_official_messages";
  await ensureBotMessage(managed.get("welcome").id, bot.id, "# Welcome to EverLeaf", "# Welcome to EverLeaf\nEnhanced Classic MapleStory v83 with quality-of-life improvements, long-term progression, and no pay-to-win.\n\n1. Read #rules.\n2. Get the game and launcher from #downloads-and-links.\n3. Create and link your account on the website.\n4. Check #known-issues before reporting a problem.\n5. Use the matching help, suggestion, party, or class channel so answers stay easy to find.");
  await ensureBotMessage(managed.get("rules").id, bot.id, "# EverLeaf Community Rules", "# EverLeaf Community Rules\n1. Be respectful; harassment, hate speech, threats, and targeted abuse are not allowed.\n2. No cheating, exploiting, botting, real-money trading, or malicious files.\n3. Keep credentials private. Staff will never ask for your password.\n4. Use the appropriate channel and avoid spam, duplicate posts, and disruptive advertising.\n5. Report exploits privately to staff; never publish reproduction instructions.\n6. Follow staff direction and the website Terms of Service.");
  await ensureBotMessage(managed.get("downloads-and-links").id, bot.id, "# Official EverLeaf Links", "# Official EverLeaf Links\nWebsite: https://everleafms.online\nDownloads and launcher: https://everleafms.online/downloads\nAccount and Discord linking: https://everleafms.online/account\nVote and rewards: https://everleafms.online/vote\n\nOnly use files and links published through the official website, launcher, or this channel.");
  await ensureBotMessage(managed.get("announcements").id, bot.id, "Official EverLeaf announcements", "Official EverLeaf announcements, launch updates, events, and planned maintenance will be published here.");
  await ensureBotMessage(managed.get("patch-notes").id, bot.id, "EverLeaf gameplay, website, and launcher patch notes", "EverLeaf gameplay, website, launcher, infrastructure, and community-system patch notes will be published here.");
  await ensureBotMessage(managed.get("known-issues").id, bot.id, "# EverLeaf Known Issues", "# EverLeaf Known Issues\nConfirmed issues and safe workarounds are maintained here. Check this channel before opening a post in #bug-reports. Fixed reports remain available in the forum with the Fixed tag for reference.");
  await ensureBotMessage(managed.get("help-and-support").id, bot.id, "# Getting Help", "# Getting Help\nFor account or launcher help, describe the problem and any safe error message. For reproducible defects, use #bug-reports. For build and skill questions, use #class-help. Never post passwords, tokens, private account data, or sensitive logs.");
  await ensureBotMessage(managed.get("class-overview").id, bot.id, "# EverLeaf Class Guides", "# EverLeaf Class Guides\nUse the class channels for authoritative availability, progression, skill, equipment, and balance information. Discussion and personal build questions belong in #class-help.");

  currentStep = "cleanup_legacy_status_messages";
  const cleanedStatusMessages = await cleanupLegacyStatusMessages(managed.get("server-status").id, bot.id);

  console.log("discord_reconcile=ok");
  console.log(`discord_categories_ready=${categoryOrder.length}`);
  console.log(`discord_text_and_forum_channels_ready=${specs.length}`);
  console.log(`discord_voice_channels_ready=${voice.length}`);
  console.log("discord_existing_channels_deleted=0");
  console.log(`discord_legacy_status_messages_deleted=${cleanedStatusMessages}`);
})().catch((error) => {
  reportFailure(currentStep, error);
  process.exitCode = 1;
});