const fs = require("fs");

const [webRoot, outputPath] = process.argv.slice(2);
if (!webRoot || !outputPath) throw new Error("Web root and output path are required.");
const { db } = require(`${webRoot}/src/db/cms`);
const paypal = require(`${webRoot}/src/services/paypalService`);

(async()=>{
  const profile=db.prepare(`SELECT game_account_id,game_account_name FROM supporter_profiles
    WHERE discord_user_id <> '' ORDER BY updated_at DESC LIMIT 1`).get();
  if(!profile) throw new Error("No linked supporter profile is available for the sandbox test.");
  const checkout=await paypal.createCheckout({
    provider:"paypal",amountCents:500,
    accountId:profile.game_account_id,accountName:profile.game_account_name,
  });
  fs.writeFileSync(outputPath,checkout.url,{mode:0o600});
  fs.chmodSync(outputPath,0o600);
  console.log("PayPal sandbox Checkout session created.");
})().catch(error=>{console.error(error.message);process.exitCode=1;});
