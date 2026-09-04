const Stripe = require("stripe");
const env = require("../config/env");
const supporter = require("./supporterService");

function activeConfig() {
  return env.payments.stripe[env.payments.stripe.environment];
}

function client() {
  const config = activeConfig();
  if (!config.secretKey) throw new Error("Stripe credentials are not configured.");
  return new Stripe(config.secretKey);
}

async function createCheckout(input) {
  const order = supporter.createOrder({ ...input, provider: "stripe" });
  try {
    const session = await client().checkout.sessions.create({
      mode: "payment",
      client_reference_id: order.id,
      metadata: { orderId: order.id },
      line_items: [{
        quantity: 1,
        price_data: {
          currency: order.currency,
          unit_amount: order.amountCents,
          product_data: { name: "EverLeaf supporter contribution" },
        },
      }],
      success_url: `${env.payments.publicBaseUrl}/donate?checkout=success`,
      cancel_url: `${env.payments.publicBaseUrl}/donate?checkout=canceled`,
    }, { idempotencyKey: `everleaf-checkout-${order.id}` });
    supporter.transitionOrder(order.id, "pending", session.id);
    return { order, url: session.url };
  } catch (error) {
    supporter.transitionOrder(order.id, "failed");
    throw error;
  }
}

function constructEvent(rawBody, signature) {
  const secret = activeConfig().webhookSecret;
  if (!secret) throw new Error("Stripe webhook verification is not configured.");
  return client().webhooks.constructEvent(rawBody, signature, secret);
}

function processEvent(event, rawBody) {
  if (event.type === "charge.refunded") {
    const charge = event.data && event.data.object;
    const order = supporter.getOrderByProviderReference("stripe", charge && charge.payment_intent);
    if (!order) throw new Error("Stripe refund does not match a payment order.");
    if (String(charge.currency).toLowerCase() !== order.currency) throw new Error("Stripe refund currency does not match the order.");
    const cumulative = Number(charge.amount_refunded);
    const current = Number(order.refunded_cents || 0);
    if (!Number.isSafeInteger(cumulative) || cumulative < current || cumulative > order.amount_cents) {
      throw new Error("Stripe refund amount does not match the order.");
    }
    if (cumulative === current) {
      supporter.recordProviderEvent({provider:"stripe",eventId:event.id,orderId:order.id,eventType:event.type,rawPayload:rawBody});
      return false;
    }
    return supporter.refundPayment({
      provider: "stripe",
      eventId: event.id,
      orderId: order.id,
      eventType: event.type,
      rawPayload: rawBody,
      refundCents: cumulative - current,
    });
  }

  if (event.type !== "checkout.session.completed") {
    return supporter.recordProviderEvent({
      provider: "stripe",
      eventId: event.id,
      eventType: event.type,
      rawPayload: rawBody,
    });
  }

  const session = event.data && event.data.object;
  const orderId = session && (session.metadata && session.metadata.orderId || session.client_reference_id);
  const order = supporter.getOrder(orderId);
  if (!order || order.provider !== "stripe") throw new Error("Stripe event does not match a payment order.");
  if (session.payment_status !== "paid") throw new Error("Stripe Checkout session is not paid.");
  if (Number(session.amount_total) !== order.amount_cents || String(session.currency).toLowerCase() !== order.currency) {
    throw new Error("Stripe payment amount or currency does not match the order.");
  }
  if (session.client_reference_id !== order.id || !session.metadata || session.metadata.orderId !== order.id) {
    throw new Error("Stripe Checkout order identity does not match.");
  }

  return supporter.confirmPayment({
    provider: "stripe",
    eventId: event.id,
    orderId: order.id,
    eventType: event.type,
    rawPayload: rawBody,
    providerReference: session.payment_intent || session.id,
  });
}

module.exports = { activeConfig, createCheckout, constructEvent, processEvent };
