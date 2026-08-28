const fs = require("fs");

const [credentialPath, envPath] = process.argv.slice(2);
if (!credentialPath || !envPath) throw new Error("Credential and environment paths are required.");
const credentials = JSON.parse(fs.readFileSync(credentialPath,"utf8"));
let text = fs.readFileSync(envPath,"utf8");

const values = {
  PAYPAL_ENABLED: "false",
  PAYPAL_ENVIRONMENT: "sandbox",
  PAYPAL_SANDBOX_CLIENT_ID: credentials.sandbox.clientId,
  PAYPAL_SANDBOX_CLIENT_SECRET: credentials.sandbox.secret,
  PAYPAL_LIVE_CLIENT_ID: credentials.live.clientId,
  PAYPAL_LIVE_CLIENT_SECRET: credentials.live.secret
};

for (const [key,value] of Object.entries(values)) {
  if (!value || /[\r\n]/.test(value)) throw new Error(`Invalid value for ${key}.`);
  const line = `${key}=${value}`;
  const pattern = new RegExp(`^${key}=.*$`,"m");
  text = pattern.test(text) ? text.replace(pattern,line) : `${text.trimEnd()}\n${line}\n`;
}

fs.writeFileSync(envPath,text,{mode:0o600});
fs.chmodSync(envPath,0o600);
console.log("Payment credentials installed with providers disabled.");
