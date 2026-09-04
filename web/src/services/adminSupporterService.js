const { db } = require("../db/cms");
const discord = require("./discordService");

function dashboardSummary() {
  const row = db.prepare(`SELECT
    COALESCE(SUM(CASE WHEN status IN ('paid','refunded') THEN amount_cents-refunded_cents ELSE 0 END),0) AS confirmed_cents,
    SUM(CASE WHEN status='paid' THEN 1 ELSE 0 END) AS paid_count,
    SUM(CASE WHEN refunded_cents>0 THEN 1 ELSE 0 END) AS refunded_count,
    SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) AS pending_count,
    SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) AS failed_count
    FROM payment_orders`).get();
  return {
    confirmedCents: Number(row.confirmed_cents || 0),
    paidCount: Number(row.paid_count || 0),
    refundedCount: Number(row.refunded_count || 0),
    pendingCount: Number(row.pending_count || 0),
    failedCount: Number(row.failed_count || 0),
  };
}

function listPayments({ status = "", provider = "", search = "", page = 1, pageSize = 50 } = {}) {
  const normalizedStatus = ["created", "pending", "paid", "failed", "canceled", "refunded"].includes(status) ? status : "";
  const normalizedProvider = ["stripe", "paypal"].includes(provider) ? provider : "";
  const normalizedSearch = String(search || "").trim().slice(0, 80);
  const normalizedPage = Number.isSafeInteger(Number(page)) && Number(page) > 0 ? Number(page) : 1;
  const normalizedPageSize = Math.min(100, Math.max(1, Number(pageSize) || 50));
  const clauses = [];
  const parameters = [];
  if (normalizedStatus) { clauses.push("status=?"); parameters.push(normalizedStatus); }
  if (normalizedProvider) { clauses.push("provider=?"); parameters.push(normalizedProvider); }
  if (normalizedSearch) {
    clauses.push("(game_account_name LIKE ? ESCAPE '\\' OR id LIKE ? ESCAPE '\\')");
    const like = `%${escapeLike(normalizedSearch)}%`;
    parameters.push(like, like);
  }
  const where = clauses.length ? `WHERE ${clauses.join(" AND ")}` : "";
  const total = Number(db.prepare(`SELECT COUNT(*) count FROM payment_orders ${where}`).get(...parameters).count || 0);
  const pages = Math.max(1, Math.ceil(total / normalizedPageSize));
  const actualPage = Math.min(normalizedPage, pages);
  const rows = db.prepare(`SELECT id,game_account_id,game_account_name,provider,amount_cents,refunded_cents,currency,status,created_at,updated_at
    FROM payment_orders ${where} ORDER BY created_at DESC,id DESC LIMIT ? OFFSET ?`)
    .all(...parameters, normalizedPageSize, (actualPage - 1) * normalizedPageSize);
  return { rows, total, page: actualPage, pageSize: normalizedPageSize, pages };
}

function listSupporters({ search = "", roleStatus = "", limit = 100 } = {}) {
  const normalizedSearch = String(search || "").trim().slice(0, 80);
  const normalizedRoleStatus = ["not_linked", "linked", "assigned", "failed", "not_member"].includes(roleStatus) ? roleStatus : "";
  const normalizedLimit = Math.min(200, Math.max(1, Number(limit) || 100));
  const clauses = [];
  const parameters = [];
  if (normalizedSearch) {
    clauses.push("game_account_name LIKE ? ESCAPE '\\'");
    parameters.push(`%${escapeLike(normalizedSearch)}%`);
  }
  if (normalizedRoleStatus) { clauses.push("discord_role_status=?"); parameters.push(normalizedRoleStatus); }
  const where = clauses.length ? `WHERE ${clauses.join(" AND ")}` : "";
  return db.prepare(`SELECT game_account_id,game_account_name,lifetime_cents,discord_user_id<>'' AS discord_linked,discord_role_status,created_at,updated_at
    FROM supporter_profiles ${where} ORDER BY lifetime_cents DESC,game_account_name ASC LIMIT ?`)
    .all(...parameters, normalizedLimit);
}

function escapeLike(value) {
  return value.replace(/[\\%_]/g, character => `\\${character}`);
}

async function retryDiscordRole(accountId, adminId) {
  const id = Number(accountId);
  if (!Number.isSafeInteger(id) || id <= 0) throw new Error("Invalid supporter account.");
  const profile = db.prepare("SELECT game_account_name,discord_user_id,lifetime_cents FROM supporter_profiles WHERE game_account_id=?").get(id);
  if (!profile || !profile.discord_user_id) throw new Error("Supporter is not eligible for Discord role synchronization.");

  await discord.syncAccount(id);
  const updated = db.prepare("SELECT discord_role_status FROM supporter_profiles WHERE game_account_id=?").get(id);
  const status = updated?.discord_role_status || "failed";
  db.prepare("INSERT INTO audit_log(admin_id,action,details) VALUES(?,?,?)")
    .run(Number(adminId) || null, "supporter.discord_role_sync", JSON.stringify({ accountId: id, accountName: profile.game_account_name, status }));
  return status;
}

module.exports = { dashboardSummary, listPayments, listSupporters, retryDiscordRole };
