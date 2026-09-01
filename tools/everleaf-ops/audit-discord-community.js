const fs = require("fs");

const envPath = process.argv[2];
if (!envPath) throw new Error("Environment path is required.");
const env = Object.fromEntries(fs.readFileSync(envPath, "utf8").split(/\r?\n/).filter((line) => line && !line.startsWith("#") && line.includes("=")).map((line) => [line.slice(0, line.indexOf("=")), line.slice(line.indexOf("=") + 1)]));
const headers = { Authorization: `Bot ${env.DISCORD_BOT_TOKEN}` };

async function get(path) {
  const response = await fetch(`https://discord.com/api/v10${path}`, { headers });
  if (!response.ok) throw new Error(`Discord audit request failed with ${response.status}.`);
  return response.json();
}

(async () => {
  const [bot, roles, channels] = await Promise.all([
    get("/users/@me"),
    get(`/guilds/${env.DISCORD_GUILD_ID}/roles`),
    get(`/guilds/${env.DISCORD_GUILD_ID}/channels`),
  ]);
  const roleNames = ["Moderator", "Game Master", "Closed Beta Tester", "Supporter"];
  const expectedCategories = ["🍃 START HERE", "📢 NEWS & STATUS", "🌿 COMMUNITY", "🛠 GAME HELP", "📚 CLASS GUIDES", "🎉 EVENTS & GROUPS", "🔊 VOICE LOUNGES", "💚 SUPPORTERS", "🔒 STAFF"];
  const expectedText = [
    "welcome", "rules", "downloads-and-links", "announcements", "server-status", "patch-notes", "known-issues",
    "general", "introductions", "screenshots-and-media", "help-and-support", "class-help",
    "class-overview", "warrior", "magician", "bowman", "thief", "pirate", "cygnus-knights", "aran", "skill-changelog",
    "events", "party-finder", "guild-recruitment", "supporter-lounge", "staff-chat", "staff-logs",
  ];
  const expectedForums = ["suggestions", "bug-reports"];
  const expectedVoice = ["General", "Party 1", "Party 2", "Bossing", "AFK"];
  const rolesReady = roleNames.every((name) => roles.some((role) => role.name === name));
  const noStaffAdministrator = roles.filter((role) => ["Moderator", "Game Master"].includes(role.name)).every((role) => (BigInt(role.permissions) & (1n << 3n)) === 0n);
  const categoriesReady = expectedCategories.every((name) => channels.some((channel) => channel.type === 4 && channel.name === name));
  const textReady = expectedText.every((name) => channels.some((channel) => channel.type === 0 && channel.name === name));
  const forumsReady = expectedForums.every((name) => channels.some((channel) => channel.type === 15 && channel.name === name));
  const voiceReady = expectedVoice.every((name) => channels.some((channel) => channel.type === 2 && channel.name === name));
  const privateCategories = channels.filter((channel) => channel.type === 4 && ["💚 SUPPORTERS", "🔒 STAFF"].includes(channel.name));
  const privateReady = privateCategories.length === 2 && privateCategories.every((channel) => channel.permission_overwrites.some((overwrite) => overwrite.id === env.DISCORD_GUILD_ID && (BigInt(overwrite.deny) & (1n << 10n)) !== 0n));
  const readonlyNames = ["welcome", "rules", "downloads-and-links", "announcements", "server-status", "patch-notes", "known-issues", "class-overview", "warrior", "magician", "bowman", "thief", "pirate", "cygnus-knights", "aran", "skill-changelog"];
  const readonlyReady = readonlyNames.every((name) => {
    const channel = channels.find((item) => item.type === 0 && item.name === name);
    return channel?.permission_overwrites.some((overwrite) => overwrite.id === env.DISCORD_GUILD_ID && (BigInt(overwrite.deny) & (1n << 11n)) !== 0n);
  });
  const bugReports = channels.find((channel) => channel.type === 15 && channel.name === "bug-reports");
  const suggestions = channels.find((channel) => channel.type === 15 && channel.name === "suggestions");
  const forumTagsReady = [bugReports, suggestions].every((channel) => channel && (channel.flags & 16) !== 0 && channel.available_tags.length >= 10);
  const bugTemplateReady = bugReports?.topic?.includes("CH1–CH20") === true;
  const welcome = channels.find((channel) => channel.type === 0 && channel.name === "welcome");
  const messages = welcome ? await get(`/channels/${welcome.id}/messages?limit=20`) : [];
  const onboardingReady = messages.some((message) => message.author?.id === bot.id && message.content.includes("# Welcome to EverLeaf"));

  const checks = {
    discord_roles_ready: rolesReady,
    discord_staff_without_administrator: noStaffAdministrator,
    discord_categories_ready: categoriesReady,
    discord_text_channels_ready: textReady,
    discord_forums_ready: forumsReady,
    discord_voice_channels_ready: voiceReady,
    discord_private_boundaries_ready: privateReady,
    discord_readonly_channels_ready: readonlyReady,
    discord_forum_tags_ready: forumTagsReady,
    discord_20_channel_bug_template_ready: bugTemplateReady,
    discord_onboarding_message_ready: onboardingReady,
  };
  for (const [name, value] of Object.entries(checks)) console.log(`${name}=${value}`);
  if (Object.values(checks).some((value) => !value)) process.exitCode = 1;
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
