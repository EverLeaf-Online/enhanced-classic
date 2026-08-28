const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const testDir=fs.mkdtempSync(path.join(os.tmpdir(),"everleaf-paypal-"));
process.env.CMS_DB_PATH=path.join(testDir,"cms.sqlite");
process.env.PAYPAL_ENABLED="true";
process.env.PAYPAL_ENVIRONMENT="sandbox";
process.env.PAYPAL_SANDBOX_CLIENT_ID="sandbox-client";
process.env.PAYPAL_SANDBOX_CLIENT_SECRET="sandbox-secret";
process.env.PAYPAL_SANDBOX_WEBHOOK_ID="sandbox-webhook";

let db,supporter,paypal,nativeReady=true;
try {
  ({db,initCms}=require("../src/db/cms"));
  initCms();
  supporter=require("../src/services/supporterService");
  paypal=require("../src/services/paypalService");
} catch(error) {
  if(!String(error.message).includes("bindings file")) throw error;
  nativeReady=false;
}

const originalFetch=global.fetch;
test.after(()=>{
  global.fetch=originalFetch;
  if(db) db.close();
  fs.rmSync(testDir,{recursive:true,force:true});
});

function pendingOrder(id="paypal-order-1",providerReference="PAYPAL-ORDER-1") {
  db.prepare(`INSERT INTO payment_orders(id,game_account_id,game_account_name,provider,amount_cents,currency,status,provider_reference)
    VALUES(?,71,'PayPalPlayer','paypal',1000,'usd','pending',?)`).run(id,providerReference);
}

function captureEvent(overrides={}) {
  return {
    id:"WH-PAYPAL-1",
    event_type:"PAYMENT.CAPTURE.COMPLETED",
    resource:{
      id:"CAPTURE-1",status:"COMPLETED",custom_id:"paypal-order-1",invoice_id:"paypal-order-1",
      amount:{currency_code:"USD",value:"10.00"},
      supplementary_data:{related_ids:{order_id:"PAYPAL-ORDER-1"}},
      ...overrides,
    },
  };
}

test("PayPal webhook verification delegates signature validation to PayPal",{skip:!nativeReady},async()=>{
  const requests=[];
  global.fetch=async(url,options)=>{
    requests.push({url,options});
    if(url.endsWith("/v1/oauth2/token")) return {ok:true,status:200,json:async()=>({access_token:"temporary-token"})};
    return {ok:true,status:200,json:async()=>({verification_status:"SUCCESS"})};
  };
  const verified=await paypal.verifyEvent({
    "paypal-auth-algo":"SHA256withRSA","paypal-cert-url":"https://api.paypal.com/cert",
    "paypal-transmission-id":"transmission","paypal-transmission-sig":"signature","paypal-transmission-time":"time",
  },{id:"WH-VERIFY",event_type:"CHECKOUT.ORDER.APPROVED"});
  assert.equal(verified,true);
  assert.match(requests[1].url,/\/v1\/notifications\/verify-webhook-signature$/);
  assert.equal(JSON.parse(requests[1].options.body).webhook_id,"sandbox-webhook");
});

test("matching PayPal captures credit supporter totals exactly once",{skip:!nativeReady},()=>{
  pendingOrder();
  const event=captureEvent();
  assert.equal(paypal.processEvent(event,JSON.stringify(event)),true);
  assert.equal(paypal.processEvent(event,JSON.stringify(event)),false);
  assert.equal(supporter.getOrder("paypal-order-1").status,"paid");
  assert.equal(supporter.accountSummary(71).profile.lifetime_cents,1000);
});

test("PayPal captures reject amount, currency, status, and identity mismatches",{skip:!nativeReady},()=>{
  const cases=[
    ["amount",{amount:{currency_code:"USD",value:"25.00"}}],
    ["currency",{amount:{currency_code:"EUR",value:"10.00"}}],
    ["status",{status:"PENDING"}],
    ["custom",{custom_id:"another-order"}],
    ["invoice",{invoice_id:"another-order"}],
  ];
  for(const [suffix,override] of cases) {
    const id=`paypal-mismatch-${suffix}`,reference=`PAYPAL-${suffix}`;
    pendingOrder(id,reference);
    const event=captureEvent({...override,custom_id:override.custom_id||id,invoice_id:override.invoice_id||id,supplementary_data:{related_ids:{order_id:reference}}});
    assert.throws(()=>paypal.processEvent({...event,id:`WH-${suffix}`},JSON.stringify(event)));
    assert.equal(supporter.getOrder(id).status,"pending");
  }
});

test("PayPal capture requires the signed-in account to own a pending order",{skip:!nativeReady},async()=>{
  pendingOrder("paypal-capture-owner","PAYPAL-CAPTURE-OWNER");
  await assert.rejects(()=>paypal.captureCheckout("PAYPAL-CAPTURE-OWNER",999),/not available/);
});
