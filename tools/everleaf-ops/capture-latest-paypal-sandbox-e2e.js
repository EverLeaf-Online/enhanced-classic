const webRoot = process.argv[2];
if (!webRoot) throw new Error("Web root is required.");

const { db } = require(`${webRoot}/src/db/cms`);
const paypal = require(`${webRoot}/src/services/paypalService`);

(async () => {
  const order = db.prepare(`SELECT id, game_account_id, provider_reference
    FROM payment_orders
    WHERE provider='paypal' AND status='pending'
    ORDER BY created_at DESC LIMIT 1`).get();
  if (!order) throw new Error("No pending PayPal sandbox order was found.");
  await paypal.captureCheckout(order.provider_reference, order.game_account_id);
  console.log("paypal_capture=requested");
})().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
