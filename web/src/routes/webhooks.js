const express = require("express");
const stripe = require("../services/stripeService");
const discord = require("../services/discordService");
const paypal = require("../services/paypalService");
const supporter = require("../services/supporterService");
const vote = require("./vote");

const router = express.Router();

// GTop100 calls this route server-to-server, before browser sessions/CSRF are
// mounted in server.js. Parse only this callback locally; payment webhooks keep
// their raw bodies for signature verification.
router.post(
  "/gtop",
  express.json({ limit: "50kb" }),
  express.urlencoded({ extended: false, limit: "50kb" }),
  vote.handlePingback
);

router.post("/stripe", express.raw({ type: "application/json", limit: "100kb" }), async (req, res) => {
  try {
    const signature = req.get("stripe-signature");
    if (!signature) return res.status(400).send("Missing Stripe signature.");
    const event = stripe.constructEvent(req.body, signature);
    const credited = stripe.processEvent(event, req.body);
    if (credited && event.type === "checkout.session.completed") {
      const orderId = event.data.object.metadata.orderId;
      const order = supporter.getOrder(orderId);
      if (order) await discord.syncAccount(order.game_account_id);
    }
    if (credited && event.type === "charge.refunded") {
      const order = supporter.getOrderByProviderReference("stripe", event.data.object.payment_intent);
      if (order) await discord.syncAccount(order.game_account_id);
    }
    res.json({ received: true });
  } catch (error) {
    console.warn("Stripe webhook rejected:", error.message);
    res.status(400).send("Webhook rejected.");
  }
});

router.post("/paypal", express.raw({ type: "application/json", limit: "100kb" }), async (req,res)=>{
  try {
    const raw=req.body;
    const event=JSON.parse(raw.toString("utf8"));
    if(!await paypal.verifyEvent(req.headers,event)) return res.status(400).send("Webhook rejected.");
    const credited=paypal.processEvent(event,raw);
    if(credited&&event.event_type==="PAYMENT.CAPTURE.COMPLETED") {
      const providerOrderId=event.resource.supplementary_data.related_ids.order_id;
      const order=supporter.getOrderByProviderReference("paypal",providerOrderId);
      if(order) await discord.syncAccount(order.game_account_id);
    }
    if(credited&&event.event_type==="PAYMENT.CAPTURE.REFUNDED") {
      const order=supporter.getOrder(event.resource.custom_id);
      if(order) await discord.syncAccount(order.game_account_id);
    }
    res.json({received:true});
  } catch(error) {
    console.warn("PayPal webhook rejected:",error.message);
    res.status(400).send("Webhook rejected.");
  }
});

module.exports = router;
