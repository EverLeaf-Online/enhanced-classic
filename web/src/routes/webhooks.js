const express = require("express");
const stripe = require("../services/stripeService");

const router = express.Router();

router.post("/stripe", express.raw({ type: "application/json", limit: "100kb" }), (req, res) => {
  try {
    const signature = req.get("stripe-signature");
    if (!signature) return res.status(400).send("Missing Stripe signature.");
    const event = stripe.constructEvent(req.body, signature);
    stripe.processEvent(event, req.body);
    res.json({ received: true });
  } catch (error) {
    console.warn("Stripe webhook rejected:", error.message);
    res.status(400).send("Webhook rejected.");
  }
});

module.exports = router;
