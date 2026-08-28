const fs = require("fs");

const envPath = process.argv[2];
if (!envPath) throw new Error("Environment path is required.");
const parse = (text) => Object.fromEntries(text.split(/\r?\n/).filter((line) => line && !line.startsWith("#") && line.includes("=")).map((line) => [line.slice(0, line.indexOf("=")), line.slice(line.indexOf("=") + 1)]));
let text = fs.readFileSync(envPath, "utf8");
const env = parse(text);
if (!env.STRIPE_LIVE_SECRET_KEY) throw new Error("Stripe live secret key is missing.");

const endpointUrl = "https://everleafms.duckdns.org/webhooks/stripe";
async function request(path, options = {}) {
  const response = await fetch(`https://api.stripe.com${path}`, { ...options, headers: { Authorization: `Bearer ${env.STRIPE_LIVE_SECRET_KEY}`, ...(options.headers || {}) } });
  if (!response.ok) throw new Error(`Stripe API returned ${response.status} for ${path}.`);
  return response.json();
}

(async () => {
  const listed = await request("/v1/webhook_endpoints?limit=100");
  const existing = (listed.data || []).find((item) => item.url === endpointUrl && item.status === "enabled");
  let webhookSecret = env.STRIPE_LIVE_WEBHOOK_SECRET || "";
  if (!existing) {
    const body = new URLSearchParams();
    body.set("url", endpointUrl);
    body.append("enabled_events[]", "checkout.session.completed");
    body.set("description", "EverLeaf production checkout webhook");
    const created = await request("/v1/webhook_endpoints", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body });
    webhookSecret = created.secret;
  } else if (!webhookSecret) {
    throw new Error("A live Stripe webhook already exists, but its signing secret is not installed.");
  }
  if (!webhookSecret) throw new Error("Stripe did not return a live webhook signing secret.");

  const values = { STRIPE_LIVE_WEBHOOK_SECRET: webhookSecret, STRIPE_ENVIRONMENT: "live", STRIPE_ENABLED: "true" };
  for (const [key, value] of Object.entries(values)) {
    if (!value || /[\r\n]/.test(value)) throw new Error(`Invalid value for ${key}.`);
    const line = `${key}=${value}`;
    const pattern = new RegExp(`^${key}=.*$`, "m");
    text = pattern.test(text) ? text.replace(pattern, line) : `${text.trimEnd()}\n${line}\n`;
  }
  fs.writeFileSync(envPath, text, { mode: 0o600 });
  fs.chmodSync(envPath, 0o600);
  console.log("stripe_live=enabled");
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
