const webRoot = process.argv[2];
if (!webRoot) throw new Error("Web root is required.");
const { db } = require(`${webRoot}/src/db/cms`);
for (const accountId of [1, 2]) {
  const profile = db.prepare("SELECT game_account_name,lifetime_cents,discord_role_status FROM supporter_profiles WHERE game_account_id=?").get(accountId);
  const orders = db.prepare("SELECT COUNT(*) AS count FROM payment_orders WHERE game_account_id=?").get(accountId).count;
  console.log(`account_${accountId}_profile=${profile ? profile.game_account_name : "none"}`);
  console.log(`account_${accountId}_confirmed_cents=${profile ? profile.lifetime_cents : 0}`);
  console.log(`account_${accountId}_orders=${orders}`);
}
