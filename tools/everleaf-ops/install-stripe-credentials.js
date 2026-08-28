const fs = require("fs");

const [credentialPath, envPath] = process.argv.slice(2);
if (!credentialPath || !envPath) {
  throw new Error("Credential and environment paths are required.");
}

const credentials = JSON.parse(fs.readFileSync(credentialPath, "utf8"));
let text = fs.readFileSync(envPath, "utf8");
const values = {
  STRIPE_ENABLED: "false",
  STRIPE_ENVIRONMENT: "sandbox",
  STRIPE_SANDBOX_SECRET_KEY: credentials.sandbox.secretKey,
  STRIPE_SANDBOX_PUBLISHABLE_KEY: credentials.sandbox.publishableKey,
  STRIPE_LIVE_SECRET_KEY: credentials.live.secretKey,
  STRIPE_LIVE_PUBLISHABLE_KEY: credentials.live.publishableKey,
};

for (const [key, value] of Object.entries(values)) {
  if (!value || /[\r\n]/.test(value)) {
    throw new Error(`Invalid value for ${key}.`);
  }
  const line = `${key}=${value}`;
  const pattern = new RegExp(`^${key}=.*$`, "m");
  text = pattern.test(text)
    ? text.replace(pattern, line)
    : `${text.trimEnd()}\n${line}\n`;
}

fs.writeFileSync(envPath, text, { mode: 0o600 });
fs.chmodSync(envPath, 0o600);
console.log("Stripe credentials installed with the provider disabled.");
