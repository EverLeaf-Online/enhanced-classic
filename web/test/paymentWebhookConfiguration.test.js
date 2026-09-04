const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const repositoryRoot = path.resolve(__dirname, "..", "..");
const read = relative => fs.readFileSync(path.join(repositoryRoot, relative), "utf8");

test("live provider configuration subscribes to payments and refunds", () => {
  const stripe = read("tools/everleaf-ops/configure-stripe-live-webhook.js");
  const paypal = read("tools/everleaf-ops/configure-paypal-live-webhook.js");
  assert.match(stripe, /checkout\.session\.completed/);
  assert.match(stripe, /charge\.refunded/);
  assert.match(paypal, /PAYMENT\.CAPTURE\.COMPLETED/);
  assert.match(paypal, /PAYMENT\.CAPTURE\.REFUNDED/);
});

test("live readiness requires refund subscriptions", () => {
  const readiness = read("tools/everleaf-ops/verify-live-payment-readiness.js");
  assert.match(readiness, /charge\.refunded/);
  assert.match(readiness, /PAYMENT\.CAPTURE\.REFUNDED/);
});
