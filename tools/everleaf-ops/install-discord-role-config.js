const fs = require("fs");

const [envPath] = process.argv.slice(2);
if (!envPath) throw new Error("Environment path is required.");
let text = fs.readFileSync(envPath, "utf8");
const values = {
  DISCORD_ENABLED: "true",
  DISCORD_GUILD_ID: "1542634066451365889",
  DISCORD_SUPPORTER_ROLE_ID: "1542769829268688936",
};
for (const [key, value] of Object.entries(values)) {
  const line = `${key}=${value}`;
  const pattern = new RegExp(`^${key}=.*$`, "m");
  text = pattern.test(text) ? text.replace(pattern, line) : `${text.trimEnd()}\n${line}\n`;
}
fs.writeFileSync(envPath, text, { mode: 0o600 });
fs.chmodSync(envPath, 0o600);
console.log("Discord supporter role configuration installed.");
