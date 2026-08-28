const fs = require("fs");
const envPath = process.argv[2];
const env = Object.fromEntries(fs.readFileSync(envPath, "utf8").split(/\r?\n/).filter((line) => line && !line.startsWith("#") && line.includes("=")).map((line) => [line.slice(0, line.indexOf("=")), line.slice(line.indexOf("=") + 1)]));
const headers = { Authorization: `Bot ${env.DISCORD_BOT_TOKEN}` };
async function get(path) {
  const response = await fetch(`https://discord.com/api/v10${path}`, { headers });
  if (!response.ok) throw new Error(`Discord audit request failed with ${response.status}.`);
  return response.json();
}
(async () => {
  const roles = await get(`/guilds/${env.DISCORD_GUILD_ID}/roles`);
  const channels = await get(`/guilds/${env.DISCORD_GUILD_ID}/channels`);
  const roleNames = ["Moderator", "Game Master", "Closed Beta Tester", "Supporter"];
  const expectedCategories = ["🍃 START HERE", "📢 NEWS & STATUS", "🌿 COMMUNITY", "🛠 GAME HELP", "🎉 EVENTS & GROUPS", "💚 SUPPORTERS", "🔒 STAFF", "🔊 VOICE LOUNGES"];
  const expectedText = ["welcome", "rules", "downloads-and-links", "announcements", "server-status", "patch-notes", "general", "introductions", "screenshots-and-media", "suggestions", "help-and-support", "bug-reports", "class-help", "events", "party-finder", "guild-recruitment", "supporter-lounge", "staff-chat", "staff-logs"];
  const expectedVoice = ["General", "Party 1", "Party 2", "Bossing", "AFK"];
  const rolesReady = roleNames.every((name) => roles.some((role) => role.name === name));
  const noStaffAdministrator = roles.filter((role) => ["Moderator", "Game Master"].includes(role.name)).every((role) => (BigInt(role.permissions) & (1n << 3n)) === 0n);
  const categoriesReady = expectedCategories.every((name) => channels.some((channel) => channel.type === 4 && channel.name === name));
  const textReady = expectedText.every((name) => channels.some((channel) => channel.type === 0 && channel.name === name));
  const voiceReady = expectedVoice.every((name) => channels.some((channel) => channel.type === 2 && channel.name === name));
  const privateCategories = channels.filter((channel) => channel.type === 4 && ["💚 SUPPORTERS", "🔒 STAFF"].includes(channel.name));
  const privateReady = privateCategories.length === 2 && privateCategories.every((channel) => channel.permission_overwrites.some((overwrite) => overwrite.id === env.DISCORD_GUILD_ID && (BigInt(overwrite.deny) & (1n << 10n)) !== 0n));
  const readonlyReady = ["welcome", "rules", "announcements", "server-status", "patch-notes"].every((name) => {
    const channel = channels.find((item) => item.type === 0 && item.name === name);
    return channel?.permission_overwrites.some((overwrite) => overwrite.id === env.DISCORD_GUILD_ID && (BigInt(overwrite.deny) & (1n << 11n)) !== 0n);
  });
  const welcome = channels.find((channel) => channel.type === 0 && channel.name === "welcome");
  const messages = welcome ? await get(`/channels/${welcome.id}/messages?limit=5`) : [];
  console.log(`discord_roles_ready=${rolesReady}`);
  console.log(`discord_staff_without_administrator=${noStaffAdministrator}`);
  console.log(`discord_categories_ready=${categoriesReady}`);
  console.log(`discord_text_channels_ready=${textReady}`);
  console.log(`discord_voice_channels_ready=${voiceReady}`);
  console.log(`discord_private_boundaries_ready=${privateReady}`);
  console.log(`discord_readonly_channels_ready=${readonlyReady}`);
  console.log(`discord_onboarding_message_ready=${messages.length > 0}`);
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
