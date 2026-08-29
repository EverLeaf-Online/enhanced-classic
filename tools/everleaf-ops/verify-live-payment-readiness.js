const fs = require("fs");

const [webRoot, envPath] = process.argv.slice(2);
if (!webRoot || !envPath) throw new Error("Web root and environment path are required.");
const values = Object.fromEntries(fs.readFileSync(envPath, "utf8").split(/\r?\n/).filter((line) => line && !line.startsWith("#") && line.includes("=")).map((line) => [line.slice(0, line.indexOf("=")), line.slice(line.indexOf("=") + 1)]));

async function json(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`Provider readiness request failed with ${response.status}.`);
  return response.json();
}

(async () => {
  const stripe = await json("https://api.stripe.com/v1/webhook_endpoints?limit=100", { headers: { Authorization: `Bearer ${values.STRIPE_LIVE_SECRET_KEY}` } });
  const stripeEvents = ["checkout.session.completed", "charge.refunded"];
  const stripeReady = (stripe.data || []).some((item) => item.url === "https://everleafms.duckdns.org/webhooks/stripe" && item.status === "enabled" && stripeEvents.every((event) => item.enabled_events.includes(event)));

  const auth = await json("https://api-m.paypal.com/v1/oauth2/token", { method: "POST", headers: { Authorization: `Basic ${Buffer.from(`${values.PAYPAL_LIVE_CLIENT_ID}:${values.PAYPAL_LIVE_CLIENT_SECRET}`).toString("base64")}`, "Content-Type": "application/x-www-form-urlencoded" }, body: "grant_type=client_credentials" });
  const paypal = await json("https://api-m.paypal.com/v1/notifications/webhooks", { headers: { Authorization: `Bearer ${auth.access_token}` } });
  const paypalEvents = ["PAYMENT.CAPTURE.COMPLETED", "PAYMENT.CAPTURE.REFUNDED"];
  const paypalReady = (paypal.webhooks || []).some((item) => item.id === values.PAYPAL_LIVE_WEBHOOK_ID && item.url === "https://everleafms.duckdns.org/webhooks/paypal" && paypalEvents.every((name) => item.event_types.some((event) => event.name === name)));

  console.log(`stripe_environment=${values.STRIPE_ENVIRONMENT}`);
  console.log(`stripe_live_ready=${stripeReady}`);
  console.log(`paypal_environment=${values.PAYPAL_ENVIRONMENT}`);
  console.log(`paypal_live_ready=${paypalReady}`);
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
