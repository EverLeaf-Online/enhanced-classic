const fs = require("fs");

const [credentialPath, envPath] = process.argv.slice(2);
if (!credentialPath || !envPath) throw new Error("Credential and environment paths are required.");
const credentials = JSON.parse(fs.readFileSync(credentialPath, "utf8"));
const secret = credentials.DISCORD_CLIENT_SECRET;
if (!secret || /[\r\n]/.test(secret)) throw new Error("Invalid Discord OAuth secret.");

let text = fs.readFileSync(envPath, "utf8");
const values = {
  DISCORD_ENABLED: "true",
  DISCORD_CLIENT_ID: "1542634637862633602",
  DISCORD_CLIENT_SECRET: secret,
  DISCORD_GUILD_ID: "1542634066451365889",
  DISCORD_REDIRECT_URI: "https://everleafms.duckdns.org/account/discord/callback",
};
for (const [key, value] of Object.entries(values)) {
  const line = `${key}=${value}`;
  const pattern = new RegExp(`^${key}=.*$`, "m");
  text = pattern.test(text) ? text.replace(pattern, line) : `${text.trimEnd()}\n${line}\n`;
}
fs.writeFileSync(envPath, text, { mode: 0o600 });
fs.chmodSync(envPath, 0o600);
console.log("Discord OAuth configuration installed.");
