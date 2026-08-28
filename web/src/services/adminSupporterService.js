const { db } = require("../db/cms");
const discord = require("./discordService");

function dashboardSummary() {
  const row = db.prepare(`SELECT
    COALESCE(SUM(CASE WHEN status='paid' THEN amount_cents ELSE 0 END),0) AS confirmed_cents,
    SUM(CASE WHEN status='paid' THEN 1 ELSE 0 END) AS paid_count,
    SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) AS pending_count,
    SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) AS failed_count
    FROM payment_orders`).get();
  return {
    confirmedCents: Number(row.confirmed_cents || 0),
    paidCount: Number(row.paid_count || 0),
    pendingCount: Number(row.pending_count || 0),
    failedCount: Number(row.failed_count || 0),
  };
}

async function retryDiscordRole(accountId, adminId) {
  const id = Number(accountId);
  if (!Number.isSafeInteger(id) || id <= 0) throw new Error("Invalid supporter account.");
  const profile = db.prepare("SELECT game_account_name,discord_user_id,lifetime_cents FROM supporter_profiles WHERE game_account_id=?").get(id);
  if (!profile || !profile.discord_user_id || profile.lifetime_cents <= 0) throw new Error("Supporter is not eligible for Discord role synchronization.");

  await discord.syncAccount(id);
  const updated = db.prepare("SELECT discord_role_status FROM supporter_profiles WHERE game_account_id=?").get(id);
  const status = updated?.discord_role_status || "failed";
  db.prepare("INSERT INTO audit_log(admin_id,action,details) VALUES(?,?,?)")
    .run(Number(adminId) || null, "supporter.discord_role_sync", JSON.stringify({ accountId: id, accountName: profile.game_account_name, status }));
  return status;
}

module.exports = { dashboardSummary, retryDiscordRole };
