const fs = require("fs");

const envPath = process.argv[2];
const values = Object.fromEntries(
  fs.readFileSync(envPath, "utf8").split(/\r?\n/)
    .filter(line => line && !line.startsWith("#") && line.includes("="))
    .map(line => [line.slice(0, line.indexOf("=")), line.slice(line.indexOf("=") + 1)])
);

const token = values.DISCORD_BOT_TOKEN;
const guildId = values.DISCORD_GUILD_ID;
if (!token || !guildId) throw new Error("Discord bot token or guild ID is missing.");

async function discord(path) {
  const response = await fetch(`https://discord.com/api/v10${path}`, {
    headers: { Authorization: `Bot ${token}` },
  });
  if (!response.ok) throw new Error(`Discord API returned ${response.status}.`);
  return response.json();
}

(async () => {
  const guild = await discord(`/guilds/${guildId}`);
  const roles = await discord(`/guilds/${guildId}/roles`);
  const bot = await discord("/users/@me");
  const member = await discord(`/guilds/${guildId}/members/${bot.id}`);
  const botRoles = roles.filter(role => member.roles.includes(role.id));
  const permissions = botRoles.reduce((value, role) => value | BigInt(role.permissions), 0n);
  console.log(`guild_access=ok name=${JSON.stringify(guild.name)}`);
  console.log(`manage_roles=${(permissions & (1n << 28n)) !== 0n}`);
  console.log(`manage_channels=${(permissions & (1n << 4n)) !== 0n}`);
  console.log(`view_channels=${(permissions & (1n << 10n)) !== 0n}`);
  console.log(`send_messages=${(permissions & (1n << 11n)) !== 0n}`);
  console.log(`read_message_history=${(permissions & (1n << 16n)) !== 0n}`);
  for (const role of roles.filter(role => /support|donat|patron|leaf/i.test(role.name))) {
    console.log(`candidate_role=${JSON.stringify(role.name)} id=${role.id} managed=${role.managed}`);
  }
})().catch(error => {
  console.error(error.message);
  process.exitCode = 1;
});
