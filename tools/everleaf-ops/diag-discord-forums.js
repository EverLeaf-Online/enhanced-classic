const fs = require("fs");
const envPath = process.argv[2];
const env = Object.fromEntries(fs.readFileSync(envPath, "utf8").split(/\r?\n/).filter((line) => line && !line.startsWith("#") && line.includes("=")).map((line) => [line.slice(0, line.indexOf("=")), line.slice(line.indexOf("=") + 1)]));
const token = env.DISCORD_BOT_TOKEN;
const guildId = env.DISCORD_GUILD_ID;
if (!token || !guildId) throw new Error("Discord production configuration is incomplete.");

async function get(path) {
  const response = await fetch(`https://discord.com/api/v10${path}`, { headers: { Authorization: `Bot ${token}` } });
  if (!response.ok) throw new Error(`Discord request failed status=${response.status}`);
  return response.json();
}

(async () => {
  const channels = await get(`/guilds/${guildId}/channels`);
  for (const name of ["suggestions", "bug-reports"]) {
    const channel = channels.find((item) => item.type === 15 && item.name === name);
    if (!channel) throw new Error(`Forum ${name} is missing.`);
    console.log(`forum=${name}`);
    console.log(`forum_${name}_parent_present=${Boolean(channel.parent_id)}`);
    console.log(`forum_${name}_topic=${JSON.stringify(channel.topic || "")}`);
    console.log(`forum_${name}_slowmode=${channel.rate_limit_per_user || 0}`);
    console.log(`forum_${name}_flags=${channel.flags || 0}`);
    console.log(`forum_${name}_require_tag=${((channel.flags || 0) & 16) !== 0}`);
    console.log(`forum_${name}_default_reaction=${JSON.stringify(channel.default_reaction_emoji || null)}`);
    console.log(`forum_${name}_tags=${JSON.stringify((channel.available_tags || []).map((tag) => ({ name: tag.name, moderated: Boolean(tag.moderated) })))}`);
    console.log(`forum_${name}_overwrite_count=${(channel.permission_overwrites || []).length}`);
  }
})().catch((error) => { console.error(`forum_diag_failed ${error.message}`); process.exitCode = 1; });
