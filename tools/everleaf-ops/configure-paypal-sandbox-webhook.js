const fs = require("fs");

const envPath = process.argv[2];
if (!envPath) throw new Error("Environment path is required.");
const parse = text => Object.fromEntries(text.split(/\r?\n/).filter(line => line && !line.startsWith("#") && line.includes("=")).map(line => [line.slice(0,line.indexOf("=")),line.slice(line.indexOf("=")+1)]));
let text = fs.readFileSync(envPath,"utf8");
const env = parse(text);
const clientId = env.PAYPAL_SANDBOX_CLIENT_ID;
const clientSecret = env.PAYPAL_SANDBOX_CLIENT_SECRET;
if (!clientId || !clientSecret) throw new Error("PayPal sandbox credentials are missing.");

const api = "https://api-m.sandbox.paypal.com";
const endpointUrl = "https://everleafms.duckdns.org/webhooks/paypal";
const requiredEvents = ["PAYMENT.CAPTURE.COMPLETED", "PAYMENT.CAPTURE.REFUNDED"];

async function request(path,options={}) {
  const response = await fetch(`${api}${path}`,options);
  if (!response.ok) throw new Error(`PayPal API returned ${response.status} for ${path}.`);
  return response.status === 204 ? null : response.json();
}

(async()=>{
  const auth = await request("/v1/oauth2/token",{
    method:"POST",
    headers:{Authorization:`Basic ${Buffer.from(`${clientId}:${clientSecret}`).toString("base64")}`,"Content-Type":"application/x-www-form-urlencoded"},
    body:"grant_type=client_credentials",
  });
  const headers={Authorization:`Bearer ${auth.access_token}`,"Content-Type":"application/json"};
  const existing=await request("/v1/notifications/webhooks",{headers});
  let webhook=(existing.webhooks||[]).find(item=>item.url===endpointUrl);
  if(!webhook) {
    webhook=await request("/v1/notifications/webhooks",{
      method:"POST",headers,
      body:JSON.stringify({url:endpointUrl,event_types:requiredEvents.map(name=>({name}))}),
    });
    console.log("paypal_webhook=created");
  } else {
    if(!requiredEvents.every(name=>webhook.event_types.some(event=>event.name===name))) {
      await request(`/v1/notifications/webhooks/${encodeURIComponent(webhook.id)}`,{
        method:"PATCH",headers,
        body:JSON.stringify([{op:"replace",path:"/event_types",value:requiredEvents.map(name=>({name}))}]),
      });
    }
    console.log("paypal_webhook=existing");
  }
  const values={PAYPAL_SANDBOX_WEBHOOK_ID:webhook.id,PAYPAL_ENVIRONMENT:"sandbox",PAYPAL_ENABLED:"true"};
  for(const [key,value] of Object.entries(values)) {
    if(!value||/[\r\n]/.test(value)) throw new Error(`Invalid value for ${key}.`);
    const line=`${key}=${value}`;
    const pattern=new RegExp(`^${key}=.*$`,"m");
    text=pattern.test(text)?text.replace(pattern,line):`${text.trimEnd()}\n${line}\n`;
  }
  fs.writeFileSync(envPath,text,{mode:0o600});
  fs.chmodSync(envPath,0o600);
  console.log("paypal_sandbox=enabled");
})().catch(error=>{console.error(error.message);process.exitCode=1;});
