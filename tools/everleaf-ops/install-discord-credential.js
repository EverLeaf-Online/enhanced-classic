const fs = require("fs");

const [credentialPath, envPath] = process.argv.slice(2);
if (!credentialPath || !envPath) {
  throw new Error("Credential and environment paths are required.");
}

const credentials = JSON.parse(fs.readFileSync(credentialPath, "utf8"));
const token = credentials.DISCORD_BOT_TOKEN;
if (!token || /[\r\n]/.test(token)) {
  throw new Error("Invalid Discord bot token.");
}

let text = fs.readFileSync(envPath, "utf8");
const values = {
  DISCORD_ENABLED: "false",
  DISCORD_BOT_TOKEN: token,
};

for (const [key, value] of Object.entries(values)) {
  const line = `${key}=${value}`;
  const pattern = new RegExp(`^${key}=.*$`, "m");
  text = pattern.test(text)
    ? text.replace(pattern, line)
    : `${text.trimEnd()}\n${line}\n`;
}

fs.writeFileSync(envPath, text, { mode: 0o600 });
fs.chmodSync(envPath, 0o600);
console.log("Discord credential installed with the integration disabled.");
