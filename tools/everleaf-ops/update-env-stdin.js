const fs = require("fs");

const envPath = process.argv[2];
if (!envPath) throw new Error("Environment path is required.");

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => { input += chunk; });
process.stdin.on("end", () => {
  const values = JSON.parse(input);
  const allowed = new Set([
    "PAYPAL_LIVE_CLIENT_ID", "PAYPAL_LIVE_CLIENT_SECRET",
    "STRIPE_LIVE_SECRET_KEY", "STRIPE_LIVE_PUBLISHABLE_KEY",
    "STRIPE_LIVE_WEBHOOK_SECRET",
  ]);
  let text = fs.readFileSync(envPath, "utf8");
  for (const [key, value] of Object.entries(values)) {
    if (!allowed.has(key) || typeof value !== "string" || !value || /[\r\n]/.test(value)) throw new Error(`Invalid environment value for ${key}.`);
    const line = `${key}=${value}`;
    const pattern = new RegExp(`^${key}=.*$`, "m");
    text = pattern.test(text) ? text.replace(pattern, line) : `${text.trimEnd()}\n${line}\n`;
  }
  fs.writeFileSync(envPath, text, { mode: 0o600 });
  fs.chmodSync(envPath, 0o600);
  console.log("environment_update=ok");
});
