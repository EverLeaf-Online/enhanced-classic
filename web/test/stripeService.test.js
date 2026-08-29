const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const Stripe = require("stripe");

const testDir = fs.mkdtempSync(path.join(os.tmpdir(), "everleaf-stripe-"));
process.env.CMS_DB_PATH = path.join(testDir, "cms.sqlite");
process.env.STRIPE_ENABLED = "true";
process.env.STRIPE_ENVIRONMENT = "sandbox";
process.env.STRIPE_SANDBOX_SECRET_KEY = "sk_test_placeholder";
process.env.STRIPE_SANDBOX_WEBHOOK_SECRET = "whsec_everleaf_test_secret";

let db, supporter, stripe, nativeReady = true;
try {
  ({ db, initCms } = require("../src/db/cms"));
  initCms();
  supporter = require("../src/services/supporterService");
  stripe = require("../src/services/stripeService");
} catch (error) {
  if (!String(error.message).includes("bindings file")) throw error;
  nativeReady = false;
}

test.after(() => {
  if (db) db.close();
  fs.rmSync(testDir, { recursive: true, force: true });
});

function pendingOrder(id = "stripe-order-1") {
  db.prepare(`INSERT INTO payment_orders
    (id,game_account_id,game_account_name,provider,amount_cents,currency,status,provider_reference)
    VALUES(?,7,'StripePlayer','stripe',1000,'usd','pending',?)`).run(id, `cs_test_${id}`);
}

function completedEvent(overrides = {}) {
  const session = {
    id: "cs_test_checkout",
    payment_intent: "pi_test_payment",
    payment_status: "paid",
    amount_total: 1000,
    currency: "usd",
    client_reference_id: "stripe-order-1",
    metadata: { orderId: "stripe-order-1" },
    ...overrides,
  };
  return { id: "evt_stripe_complete", type: "checkout.session.completed", data: { object: session } };
}

test("Stripe webhook signatures are verified against the raw body", { skip: !nativeReady }, () => {
  const payload = JSON.stringify({ id: "evt_signed", type: "ping", data: { object: {} } });
  const header = Stripe.webhooks.generateTestHeaderString({
    payload,
    secret: process.env.STRIPE_SANDBOX_WEBHOOK_SECRET,
  });
  assert.equal(stripe.constructEvent(Buffer.from(payload), header).id, "evt_signed");
  assert.throws(() => stripe.constructEvent(Buffer.from(`${payload} `), header), /signature/i);
});

test("a matching paid Checkout event credits the supporter exactly once", { skip: !nativeReady }, () => {
  pendingOrder();
  const event = completedEvent();
  const raw = JSON.stringify(event);
  assert.equal(stripe.processEvent(event, raw), true);
  assert.equal(stripe.processEvent(event, raw), false);
  assert.equal(supporter.getOrder("stripe-order-1").status, "paid");
  assert.equal(db.prepare("SELECT lifetime_cents FROM supporter_profiles WHERE game_account_id=7").get().lifetime_cents, 1000);
});

test("Checkout completion rejects amount, currency, payment, and identity mismatches", { skip: !nativeReady }, () => {
  const cases = [
    ["amount", { amount_total: 2500 }],
    ["currency", { currency: "eur" }],
    ["payment", { payment_status: "unpaid" }],
    ["identity", { client_reference_id: "another-order" }],
    ["metadata", { metadata: { orderId: "another-order" } }],
  ];
  for (const [suffix, override] of cases) {
    const id = `stripe-mismatch-${suffix}`;
    pendingOrder(id);
    const event = completedEvent({
      client_reference_id: id,
      metadata: { orderId: id },
      ...override,
    });
    assert.throws(() => stripe.processEvent({ ...event, id: `evt_${suffix}` }, JSON.stringify(event)));
    assert.equal(supporter.getOrder(id).status, "pending");
  }
});

test("unhandled Stripe events are recorded without retaining their payload", { skip: !nativeReady }, () => {
  const event = { id: "evt_irrelevant", type: "customer.created", data: { object: { email: "private@example.invalid" } } };
  assert.equal(stripe.processEvent(event, JSON.stringify(event)), true);
  assert.equal(stripe.processEvent(event, JSON.stringify(event)), false);
  const stored = db.prepare("SELECT payload_sha256 FROM payment_events WHERE provider_event_id=?").get(event.id);
  assert.match(stored.payload_sha256, /^[a-f0-9]{64}$/);
});

test("Stripe cumulative refunds apply only the new amount", { skip: !nativeReady }, () => {
  pendingOrder("stripe-refund");
  const paid = completedEvent({client_reference_id:"stripe-refund",metadata:{orderId:"stripe-refund"},payment_intent:"pi_refund"});
  stripe.processEvent({...paid,id:"evt_refund_paid"},JSON.stringify(paid));
  const refund = amount => ({id:`evt_refund_${amount}`,type:"charge.refunded",data:{object:{payment_intent:"pi_refund",amount_refunded:amount,currency:"usd"}}});
  assert.equal(stripe.processEvent(refund(400),JSON.stringify(refund(400))),true);
  assert.equal(stripe.processEvent(refund(1000),JSON.stringify(refund(1000))),true);
  assert.equal(supporter.getOrder("stripe-refund").status,"refunded");
  assert.equal(supporter.getOrder("stripe-refund").refunded_cents,1000);
  assert.equal(supporter.accountSummary(7).profile.lifetime_cents,1000);
});
