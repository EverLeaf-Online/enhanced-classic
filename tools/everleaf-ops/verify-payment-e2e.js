const webRoot = process.argv[2];
if (!webRoot) throw new Error("Web root is required.");

const { db } = require(`${webRoot}/src/db/cms`);
const order = db.prepare(`SELECT provider, amount_cents, status
  FROM payment_orders ORDER BY created_at DESC LIMIT 1`).get();
const profile = db.prepare(`SELECT lifetime_cents, discord_role_status
  FROM supporter_profiles ORDER BY updated_at DESC LIMIT 1`).get();
const paypalEvents = db.prepare(`SELECT COUNT(*) AS count FROM payment_events
  WHERE provider='paypal'`).get();

console.log(`latest_provider=${order?.provider || "missing"}`);
console.log(`latest_amount_cents=${order?.amount_cents ?? "missing"}`);
console.log(`latest_status=${order?.status || "missing"}`);
console.log(`paypal_event_count=${paypalEvents.count}`);
console.log(`confirmed_support_cents=${profile?.lifetime_cents ?? "missing"}`);
console.log(`discord_role_status=${profile?.discord_role_status || "missing"}`);
