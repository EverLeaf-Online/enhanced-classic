const fs = require("fs");

const [credentialPath, envPath] = process.argv.slice(2);
if (!credentialPath || !envPath) throw new Error("Credential and environment paths are required.");

const credentials = JSON.parse(fs.readFileSync(credentialPath, "utf8"));
const secret = credentials.STRIPE_SANDBOX_WEBHOOK_SECRET;
if (!secret || /[\r\n]/.test(secret)) throw new Error("Invalid Stripe webhook secret.");

let text = fs.readFileSync(envPath, "utf8");
const values = {
  STRIPE_SANDBOX_WEBHOOK_SECRET: secret,
  STRIPE_ENVIRONMENT: "sandbox",
  STRIPE_ENABLED: "true",
};
for (const [key, value] of Object.entries(values)) {
  const line = `${key}=${value}`;
  const pattern = new RegExp(`^${key}=.*$`, "m");
  text = pattern.test(text) ? text.replace(pattern, line) : `${text.trimEnd()}\n${line}\n`;
}

fs.writeFileSync(envPath, text, { mode: 0o600 });
fs.chmodSync(envPath, 0o600);
console.log("Stripe sandbox webhook configured and sandbox checkout enabled.");
