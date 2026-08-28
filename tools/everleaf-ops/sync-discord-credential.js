const fs = require("fs");

const [sourcePath, destinationPath] = process.argv.slice(2);
if (!sourcePath || !destinationPath) {
  throw new Error("Source and destination environment paths are required.");
}

const source = fs.readFileSync(sourcePath, "utf8");
const token = source.match(/^DISCORD_BOT_TOKEN=(.+)$/m)?.[1];
if (!token || /[\r\n]/.test(token)) {
  throw new Error("The source Discord bot token is missing or invalid.");
}

let destination = fs.existsSync(destinationPath)
  ? fs.readFileSync(destinationPath, "utf8")
  : "";
const line = `DISCORD_BOT_TOKEN=${token}`;
destination = /^DISCORD_BOT_TOKEN=.*$/m.test(destination)
  ? destination.replace(/^DISCORD_BOT_TOKEN=.*$/m, line)
  : `${destination.trimEnd()}\n${line}\n`;

fs.writeFileSync(destinationPath, destination, { mode: 0o600 });
fs.chmodSync(destinationPath, 0o600);
console.log("Discord credential synchronized.");
