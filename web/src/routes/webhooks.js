const express = require("express");
const stripe = require("../services/stripeService");
const discord = require("../services/discordService");

const router = express.Router();

router.post("/stripe", express.raw({ type: "application/json", limit: "100kb" }), async (req, res) => {
  try {
    const signature = req.get("stripe-signature");
    if (!signature) return res.status(400).send("Missing Stripe signature.");
    const event = stripe.constructEvent(req.body, signature);
    const credited = stripe.processEvent(event, req.body);
    if (credited && event.type === "checkout.session.completed") {
      const orderId = event.data.object.metadata.orderId;
      const order = require("../services/supporterService").getOrder(orderId);
      if (order) await discord.syncAccount(order.game_account_id);
    }
    res.json({ received: true });
  } catch (error) {
    console.warn("Stripe webhook rejected:", error.message);
    res.status(400).send("Webhook rejected.");
  }
});

module.exports = router;
