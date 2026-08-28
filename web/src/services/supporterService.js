const crypto = require("crypto");
const { db } = require("../db/cms");
const env = require("../config/env");

const AMOUNTS = Object.freeze([500, 1000, 2500, 5000]);
const PROVIDERS = Object.freeze(["stripe", "paypal"]);
const TRANSITIONS = Object.freeze({created:["pending","canceled","failed"],pending:["paid","canceled","failed"],paid:["refunded"],failed:[],canceled:[],refunded:[]});

function providerReady(provider) {
  if(provider==="stripe") {
    const config=env.payments.stripe[env.payments.stripe.environment];
    return env.payments.stripe.enabled&&!!config.secretKey&&!!config.webhookSecret;
  }
  if(provider==="paypal") {
    const config=env.payments.paypal[env.payments.paypal.environment];
    return env.payments.paypal.enabled&&!!config.clientId&&!!config.clientSecret&&!!config.webhookId;
  }
  return false;
}

function validateCheckout({provider,amountCents,accountId,accountName}) {
  if(!PROVIDERS.includes(provider)) throw new Error("Unsupported payment provider.");
  if(!AMOUNTS.includes(Number(amountCents))) throw new Error("Unsupported contribution amount.");
  if(!Number.isInteger(Number(accountId))||Number(accountId)<=0||!String(accountName||"").trim()) throw new Error("A player account is required.");
  if(!providerReady(provider)) throw new Error(`${provider==="stripe"?"Stripe":"PayPal"} checkout is not available yet.`);
}

function createOrder(input) {
  validateCheckout(input);
  const order={id:crypto.randomUUID(),accountId:Number(input.accountId),accountName:String(input.accountName),provider:input.provider,amountCents:Number(input.amountCents),currency:env.payments.currency};
  db.prepare(`INSERT INTO payment_orders(id,game_account_id,game_account_name,provider,amount_cents,currency,status) VALUES(?,?,?,?,?,?,'created')`)
    .run(order.id,order.accountId,order.accountName,order.provider,order.amountCents,order.currency);
  return order;
}

function transitionOrder(orderId,nextStatus,providerReference=null) {
  const order=db.prepare("SELECT * FROM payment_orders WHERE id=?").get(orderId);
  if(!order) throw new Error("Payment order was not found.");
  if(!(TRANSITIONS[order.status]||[]).includes(nextStatus)) throw new Error(`Invalid payment transition from ${order.status} to ${nextStatus}.`);
  db.prepare(`UPDATE payment_orders SET status=?,provider_reference=COALESCE(?,provider_reference),updated_at=CURRENT_TIMESTAMP WHERE id=?`).run(nextStatus,providerReference,orderId);
  return db.prepare("SELECT * FROM payment_orders WHERE id=?").get(orderId);
}

function recordProviderEvent({provider,eventId,orderId=null,eventType,rawPayload}) {
  if(!PROVIDERS.includes(provider)||!eventId||!eventType) throw new Error("Invalid provider event.");
  const payloadHash=crypto.createHash("sha256").update(rawPayload||"").digest("hex");
  const result=db.prepare(`INSERT OR IGNORE INTO payment_events(provider,provider_event_id,order_id,event_type,payload_sha256) VALUES(?,?,?,?,?)`)
    .run(provider,eventId,orderId,eventType,payloadHash);
  return result.changes===1;
}

const confirmPaymentTransaction=db.transaction(({provider,eventId,orderId,eventType,rawPayload,providerReference})=>{
  if(db.prepare("SELECT 1 FROM payment_events WHERE provider=? AND provider_event_id=?").get(provider,eventId)) return false;
  const order=db.prepare("SELECT * FROM payment_orders WHERE id=?").get(orderId);
  if(!order||order.provider!==provider) throw new Error("Payment order does not match the provider event.");
  if(order.status!=="pending") throw new Error(`Payment order cannot be confirmed from ${order.status}.`);
  const payloadHash=crypto.createHash("sha256").update(rawPayload||"").digest("hex");
  const event=db.prepare(`INSERT OR IGNORE INTO payment_events(provider,provider_event_id,order_id,event_type,payload_sha256) VALUES(?,?,?,?,?)`)
    .run(provider,eventId,orderId,eventType,payloadHash);
  if(event.changes===0) return false;
  db.prepare(`UPDATE payment_orders SET status='paid',provider_reference=COALESCE(?,provider_reference),updated_at=CURRENT_TIMESTAMP WHERE id=?`).run(providerReference||null,orderId);
  db.prepare(`INSERT INTO supporter_profiles(game_account_id,game_account_name,lifetime_cents)
    VALUES(?,?,?) ON CONFLICT(game_account_id) DO UPDATE SET
      game_account_name=excluded.game_account_name,
      lifetime_cents=supporter_profiles.lifetime_cents+excluded.lifetime_cents,
      updated_at=CURRENT_TIMESTAMP`).run(order.game_account_id,order.game_account_name,order.amount_cents);
  return true;
});

function confirmPayment(input) {
  if(!PROVIDERS.includes(input.provider)||!input.eventId||!input.orderId||!input.eventType) throw new Error("Invalid confirmed payment event.");
  return confirmPaymentTransaction(input);
}

function accountSummary(accountId) {
  const profile=db.prepare("SELECT * FROM supporter_profiles WHERE game_account_id=?").get(Number(accountId))||null;
  const orders=db.prepare(`SELECT id,provider,amount_cents,currency,status,created_at FROM payment_orders WHERE game_account_id=? ORDER BY created_at DESC LIMIT 20`).all(Number(accountId));
  return {profile,orders};
}

function getOrder(orderId) {
  return db.prepare("SELECT * FROM payment_orders WHERE id=?").get(String(orderId||""))||null;
}

module.exports={AMOUNTS,PROVIDERS,TRANSITIONS,providerReady,validateCheckout,createOrder,transitionOrder,recordProviderEvent,confirmPayment,accountSummary,getOrder};
