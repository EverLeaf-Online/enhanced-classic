const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const testDir = fs.mkdtempSync(path.join(os.tmpdir(), "everleaf-admin-supporter-"));
process.env.CMS_DB_PATH = path.join(testDir, "cms.sqlite");
process.env.DISCORD_ENABLED = "false";

let db, supporter, discord, service, nativeReady = true;
try {
  const cms = require("../src/db/cms");
  db = cms.db;
  cms.initCms();
  supporter = require("../src/services/supporterService");
  discord = require("../src/services/discordService");
  service = require("../src/services/adminSupporterService");
} catch { nativeReady = false; }

test("admin supporter summary reports confirmed and unresolved payments", { skip: !nativeReady }, () => {
  db.exec("DELETE FROM payment_orders; DELETE FROM supporter_profiles; DELETE FROM audit_log;");
  const insert = db.prepare("INSERT INTO payment_orders(id,game_account_id,game_account_name,provider,amount_cents,status) VALUES(?,?,?,?,?,?)");
  insert.run("paid", 1, "Leaf", "stripe", 500, "paid");
  insert.run("pending", 1, "Leaf", "paypal", 1000, "pending");
  insert.run("failed", 1, "Leaf", "stripe", 2500, "failed");
  assert.deepEqual(service.dashboardSummary(), { confirmedCents: 500, paidCount: 1, refundedCount: 0, pendingCount: 1, failedCount: 1 });
});

test("Discord role retries are eligibility-gated and audited without Discord identity", { skip: !nativeReady }, async () => {
  db.exec("DELETE FROM payment_orders; DELETE FROM supporter_profiles; DELETE FROM audit_log;");
  db.prepare("INSERT INTO supporter_profiles(game_account_id,game_account_name,discord_user_id,lifetime_cents,discord_role_status) VALUES(?,?,?,?,?)")
    .run(91, "Supporter", "123456789012345678", 500, "failed");
  const original = discord.syncAccount;
  discord.syncAccount = async (accountId) => { supporter.setDiscordRoleStatus(accountId, "assigned"); return true; };
  try {
    assert.equal(await service.retryDiscordRole(91, 7), "assigned");
  } finally { discord.syncAccount = original; }
  const audit = db.prepare("SELECT action,details FROM audit_log ORDER BY id DESC LIMIT 1").get();
  assert.equal(audit.action, "supporter.discord_role_sync");
  assert.equal(audit.details.includes("123456789012345678"), false);
  await assert.rejects(() => service.retryDiscordRole(999, 7), /not eligible/);
});
