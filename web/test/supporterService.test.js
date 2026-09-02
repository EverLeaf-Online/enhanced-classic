const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const testDir = fs.mkdtempSync(path.join(os.tmpdir(), "everleaf-supporter-"));
process.env.CMS_DB_PATH = path.join(testDir, "cms.sqlite");
process.env.STRIPE_ENABLED = "false";
process.env.PAYPAL_ENABLED = "false";

let db, service, initializeCms, nativeReady=true;
try {
  ({db,initCms:initializeCms} = require("../src/db/cms"));
  initializeCms();
  service = require("../src/services/supporterService");
} catch(error) {
  if(!String(error.message).includes("bindings file")) throw error;
  nativeReady=false;
}

test.after(() => {
  if(db) db.close();
  fs.rmSync(testDir,{recursive:true,force:true});
});

test("provider controls fail closed without complete credentials", {skip:!nativeReady}, () => {
  assert.equal(service.providerReady("stripe"),false);
  assert.equal(service.providerReady("paypal"),false);
  assert.throws(() => service.validateCheckout({provider:"stripe",amountCents:1000,accountId:1,accountName:"Player"}),/not available/);
});

test("checkout validation rejects arbitrary amounts and providers", {skip:!nativeReady}, () => {
  assert.throws(() => service.validateCheckout({provider:"cash",amountCents:1000,accountId:1,accountName:"Player"}),/Unsupported payment provider/);
  assert.throws(() => service.validateCheckout({provider:"stripe",amountCents:999,accountId:1,accountName:"Player"}),/Unsupported contribution amount/);
});

test("payment orders allow only explicit forward transitions", {skip:!nativeReady}, () => {
  db.prepare(`INSERT INTO payment_orders(id,game_account_id,game_account_name,provider,amount_cents,currency,status) VALUES('order-1',1,'Player','stripe',1000,'usd','created')`).run();
  assert.equal(service.transitionOrder("order-1","pending","checkout-1").status,"pending");
  assert.equal(service.transitionOrder("order-1","paid").status,"paid");
  assert.throws(() => service.transitionOrder("order-1","pending"),/Invalid payment transition/);
  assert.throws(() => service.transitionOrder("order-1","refunded"),/Invalid payment transition/);
});

test("provider events are idempotent and retain only payload identity", {skip:!nativeReady}, () => {
  const event={provider:"stripe",eventId:"evt-1",orderId:"order-1",eventType:"checkout.completed",rawPayload:'{"sensitive":"discarded"}'};
  assert.equal(service.recordProviderEvent(event),true);
  assert.equal(service.recordProviderEvent(event),false);
  const stored=db.prepare("SELECT * FROM payment_events WHERE provider_event_id='evt-1'").get();
  assert.match(stored.payload_sha256,/^[a-f0-9]{64}$/);
  assert.equal(Object.prototype.hasOwnProperty.call(stored,"raw_payload"),false);
});

test("confirmed payments update supporter totals exactly once", {skip:!nativeReady}, () => {
  db.prepare(`INSERT INTO payment_orders(id,game_account_id,game_account_name,provider,amount_cents,currency,status) VALUES('order-2',2,'Supporter','paypal',2500,'usd','pending')`).run();
  const confirmation={provider:"paypal",eventId:"paypal-event-1",orderId:"order-2",eventType:"PAYMENT.CAPTURE.COMPLETED",rawPayload:"verified-payload",providerReference:"capture-1"};
  assert.equal(service.confirmPayment(confirmation),true);
  assert.equal(db.prepare("SELECT status FROM payment_orders WHERE id='order-2'").get().status,"paid");
  assert.equal(db.prepare("SELECT lifetime_cents FROM supporter_profiles WHERE game_account_id=2").get().lifetime_cents,2500);
  assert.equal(service.confirmPayment(confirmation),false);
  assert.equal(db.prepare("SELECT lifetime_cents FROM supporter_profiles WHERE game_account_id=2").get().lifetime_cents,2500);
});

test("partial and full refunds reduce supporter totals exactly once", {skip:!nativeReady}, () => {
  db.prepare(`INSERT INTO payment_orders(id,game_account_id,game_account_name,provider,amount_cents,currency,status)
    VALUES('refund-order',3,'RefundedSupporter','stripe',2500,'usd','pending')`).run();
  service.confirmPayment({provider:"stripe",eventId:"refund-paid",orderId:"refund-order",eventType:"checkout.session.completed",rawPayload:"paid",providerReference:"pi-refund"});

  const partial={provider:"stripe",eventId:"refund-partial",orderId:"refund-order",eventType:"charge.refunded",rawPayload:"partial",refundCents:500};
  assert.equal(service.refundPayment(partial),true);
  assert.equal(service.refundPayment(partial),false);
  assert.equal(service.getOrder("refund-order").status,"paid");
  assert.equal(service.getOrder("refund-order").refunded_cents,500);
  assert.equal(service.accountSummary(3).profile.lifetime_cents,2000);

  assert.equal(service.refundPayment({provider:"stripe",eventId:"refund-full",orderId:"refund-order",eventType:"charge.refunded",rawPayload:"full",refundCents:2000}),true);
  assert.equal(service.getOrder("refund-order").status,"refunded");
  assert.equal(service.accountSummary(3).profile.lifetime_cents,0);
  assert.throws(()=>service.refundPayment({provider:"stripe",eventId:"refund-too-much",orderId:"refund-order",eventType:"charge.refunded",rawPayload:"invalid",refundCents:1}),/Refund amount/);
});
