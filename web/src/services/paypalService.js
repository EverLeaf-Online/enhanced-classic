const env = require("../config/env");
const supporter = require("./supporterService");

function activeConfig() {
  return env.payments.paypal[env.payments.paypal.environment];
}

function apiBase() {
  return env.payments.paypal.environment === "live" ? "https://api-m.paypal.com" : "https://api-m.sandbox.paypal.com";
}

async function accessToken() {
  const config = activeConfig();
  if (!config.clientId || !config.clientSecret) throw new Error("PayPal credentials are not configured.");
  const response = await fetch(`${apiBase()}/v1/oauth2/token`, {
    method: "POST",
    headers: {
      Authorization: `Basic ${Buffer.from(`${config.clientId}:${config.clientSecret}`).toString("base64")}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: "grant_type=client_credentials",
  });
  if (!response.ok) throw new Error(`PayPal authentication failed with status ${response.status}.`);
  return (await response.json()).access_token;
}

async function paypalRequest(path,options={}) {
  const token=await accessToken();
  try {
    const response=await fetch(`${apiBase()}${path}`,{
      ...options,
      headers:{Authorization:`Bearer ${token}`,"Content-Type":"application/json",...(options.headers||{})},
    });
    if(!response.ok) throw new Error(`PayPal API request failed with status ${response.status}.`);
    return response.status===204?null:response.json();
  } finally {
    // Do not retain access tokens beyond a single provider request.
  }
}

async function createCheckout(input) {
  const order=supporter.createOrder({...input,provider:"paypal"});
  try {
    const paypalOrder=await paypalRequest("/v2/checkout/orders",{
      method:"POST",
      headers:{"PayPal-Request-Id":`everleaf-${order.id}`},
      body:JSON.stringify({
        intent:"CAPTURE",
        purchase_units:[{
          custom_id:order.id,
          invoice_id:order.id,
          description:"EverLeaf supporter contribution",
          amount:{currency_code:order.currency.toUpperCase(),value:(order.amountCents/100).toFixed(2)},
        }],
        payment_source:{paypal:{experience_context:{
          brand_name:"EverLeaf",
          user_action:"PAY_NOW",
          return_url:`${env.payments.publicBaseUrl}/donate/paypal/return`,
          cancel_url:`${env.payments.publicBaseUrl}/donate?checkout=canceled`,
        }}},
      }),
    });
    const approval=paypalOrder.links&&paypalOrder.links.find(link=>link.rel==="payer-action"||link.rel==="approve");
    if(!paypalOrder.id||!approval||!approval.href) throw new Error("PayPal did not return an approval URL.");
    supporter.transitionOrder(order.id,"pending",paypalOrder.id);
    return {order,url:approval.href};
  } catch(error) {
    supporter.transitionOrder(order.id,"failed");
    throw error;
  }
}

async function captureCheckout(providerOrderId,accountId) {
  const order=supporter.getOrderByProviderReference("paypal",providerOrderId);
  if(!order||order.game_account_id!==Number(accountId)||order.status!=="pending") throw new Error("PayPal order is not available for capture.");
  await paypalRequest(`/v2/checkout/orders/${encodeURIComponent(providerOrderId)}/capture`,{
    method:"POST",
    headers:{"PayPal-Request-Id":`everleaf-capture-${order.id}`},
    body:"{}",
  });
  return order;
}

async function verifyEvent(headers,event) {
  const webhookId=activeConfig().webhookId;
  if(!webhookId) throw new Error("PayPal webhook verification is not configured.");
  const result=await paypalRequest("/v1/notifications/verify-webhook-signature",{
    method:"POST",
    body:JSON.stringify({
      auth_algo:headers["paypal-auth-algo"],
      cert_url:headers["paypal-cert-url"],
      transmission_id:headers["paypal-transmission-id"],
      transmission_sig:headers["paypal-transmission-sig"],
      transmission_time:headers["paypal-transmission-time"],
      webhook_id:webhookId,
      webhook_event:event,
    }),
  });
  return result.verification_status==="SUCCESS";
}

function processEvent(event,rawPayload) {
  if(event.event_type==="PAYMENT.CAPTURE.REFUNDED") {
    const refund=event.resource||{};
    const order=supporter.getOrder(refund.custom_id);
    const amount=refund.amount||{};
    if(!order||order.provider!=="paypal"||refund.invoice_id!==order.id) throw new Error("PayPal refund does not match a payment order.");
    if(String(refund.status).toUpperCase()!=="COMPLETED") throw new Error("PayPal refund is not completed.");
    if(String(amount.currency_code).toLowerCase()!==order.currency) throw new Error("PayPal refund currency does not match the order.");
    const refundCents=Math.round(Number(amount.value)*100);
    return supporter.refundPayment({provider:"paypal",eventId:event.id,orderId:order.id,eventType:event.event_type,rawPayload,refundCents});
  }

  if(event.event_type!=="PAYMENT.CAPTURE.COMPLETED") {
    return supporter.recordProviderEvent({provider:"paypal",eventId:event.id,eventType:event.event_type,rawPayload});
  }
  const capture=event.resource||{};
  const providerOrderId=capture.supplementary_data&&capture.supplementary_data.related_ids&&capture.supplementary_data.related_ids.order_id;
  const order=supporter.getOrderByProviderReference("paypal",providerOrderId);
  if(!order) throw new Error("PayPal event does not match a payment order.");
  const amount=capture.amount||{};
  if(String(capture.status).toUpperCase()!=="COMPLETED") throw new Error("PayPal capture is not completed.");
  if(Math.round(Number(amount.value)*100)!==order.amount_cents||String(amount.currency_code).toLowerCase()!==order.currency) {
    throw new Error("PayPal payment amount or currency does not match the order.");
  }
  if(capture.custom_id!==order.id||capture.invoice_id!==order.id) throw new Error("PayPal order identity does not match.");
  // Keep the PayPal order ID as the stable provider reference so retries can
  // resolve the local order before the event idempotency check.
  return supporter.confirmPayment({provider:"paypal",eventId:event.id,orderId:order.id,eventType:event.event_type,rawPayload,providerReference:null});
}

module.exports={activeConfig,apiBase,createCheckout,captureCheckout,verifyEvent,processEvent};
