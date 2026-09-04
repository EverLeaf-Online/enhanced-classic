const fs = require("fs");

const envPath = process.argv[2];
if (!envPath) throw new Error("Environment path is required.");
const env = Object.fromEntries(
  fs.readFileSync(envPath, "utf8")
    .split(/\r?\n/)
    .filter((line) => line && !line.startsWith("#") && line.includes("="))
    .map((line) => [line.slice(0, line.indexOf("=")), line.slice(line.indexOf("=") + 1)]),
);
if (!env.DISCORD_BOT_TOKEN || !env.DISCORD_GUILD_ID) {
  throw new Error("Discord production configuration is incomplete.");
}

async function discord(path) {
  const response = await fetch(`https://discord.com/api/v10${path}`, {
    headers: { Authorization: `Bot ${env.DISCORD_BOT_TOKEN}` },
  });
  if (!response.ok) throw new Error(`Discord inventory request failed with ${response.status}.`);
  return response.json();
}

function typeName(type) {
  return ({ 0: "text", 2: "voice", 4: "category", 5: "announcement", 13: "stage", 15: "forum", 16: "media" })[type] || `type-${type}`;
}

function roleName(overwrite, roles, guildId) {
  if (overwrite.id === guildId) return "@everyone";
  if (overwrite.type === 0) return roles.find((role) => role.id === overwrite.id)?.name || "unknown-role";
  return "member-specific";
}

(async () => {
  const [guild, bot, roles, channels] = await Promise.all([
    discord(`/guilds/${env.DISCORD_GUILD_ID}?with_counts=true`),
    discord("/users/@me"),
    discord(`/guilds/${env.DISCORD_GUILD_ID}/roles`),
    discord(`/guilds/${env.DISCORD_GUILD_ID}/channels`),
  ]);
  const botMember = await discord(`/guilds/${env.DISCORD_GUILD_ID}/members/${bot.id}`);
  const botRoles = roles.filter((role) => botMember.roles.includes(role.id));
  const botPermissions = botRoles.reduce((all, role) => all | BigInt(role.permissions), 0n);

  console.log(`guild=${JSON.stringify(guild.name)}`);
  console.log(`members=${guild.approximate_member_count ?? "unknown"}`);
  console.log(`verification_level=${guild.verification_level}`);
  console.log(`default_notifications=${guild.default_message_notifications}`);
  console.log(`content_filter=${guild.explicit_content_filter}`);
  console.log(`features=${JSON.stringify((guild.features || []).sort())}`);
  console.log(`bot_name=${JSON.stringify(bot.username)}`);
  console.log(`bot_manage_channels=${(botPermissions & (1n << 4n)) !== 0n}`);
  console.log(`bot_manage_roles=${(botPermissions & (1n << 28n)) !== 0n}`);
  console.log(`bot_manage_messages=${(botPermissions & (1n << 13n)) !== 0n}`);
  console.log("roles:");
  for (const role of [...roles].sort((a, b) => b.position - a.position)) {
    console.log(JSON.stringify({
      name: role.name,
      position: role.position,
      managed: role.managed,
      hoist: role.hoist,
      mentionable: role.mentionable,
      administrator: (BigInt(role.permissions) & (1n << 3n)) !== 0n,
      members: role.tags?.bot_id ? "bot-role" : undefined,
    }));
  }

  const categories = channels.filter((channel) => channel.type === 4).sort((a, b) => a.position - b.position);
  const uncategorized = channels.filter((channel) => channel.type !== 4 && !channel.parent_id).sort((a, b) => a.position - b.position);
  console.log("layout:");
  for (const category of categories) {
    console.log(JSON.stringify({ category: category.name, position: category.position, overwrites: category.permission_overwrites.map((item) => roleName(item, roles, env.DISCORD_GUILD_ID)) }));
    const children = channels.filter((channel) => channel.parent_id === category.id).sort((a, b) => a.position - b.position);
    for (const channel of children) {
      console.log(JSON.stringify({
        channel: channel.name,
        type: typeName(channel.type),
        position: channel.position,
        topic: channel.topic || "",
        slowmode: channel.rate_limit_per_user || 0,
        nsfw: channel.nsfw === true,
        tags: (channel.available_tags || []).map((tag) => ({ name: tag.name, moderated: tag.moderated })),
        defaultReaction: channel.default_reaction_emoji?.emoji_name || channel.default_reaction_emoji?.emoji_id || null,
        overwrites: channel.permission_overwrites.map((item) => roleName(item, roles, env.DISCORD_GUILD_ID)),
      }));
    }
  }
  if (uncategorized.length) {
    console.log(JSON.stringify({ category: "UNCATEGORIZED" }));
    for (const channel of uncategorized) {
      console.log(JSON.stringify({ channel: channel.name, type: typeName(channel.type), position: channel.position, topic: channel.topic || "" }));
    }
  }
})().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
