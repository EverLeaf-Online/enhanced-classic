const net = require("net");
const env = require("../config/env");
const { getPool, safeIdent: I } = require("../db/game");
const { hashPassword, verifyPassword } = require("../utils/password");

function portOpen(host, port, timeout=900) {
  return new Promise(resolve => {
    const s = net.createConnection({ host, port });
    const done = ok => { try { s.destroy(); } catch {} resolve(ok); };
    s.setTimeout(timeout);
    s.once("connect", () => done(true));
    s.once("timeout", () => done(false));
    s.once("error", () => done(false));
  });
}

async function serverStatus() {
  const login = await portOpen(env.game.host, env.game.loginPort);
  const channels = await Promise.all(env.game.channelPorts.map(p => portOpen(env.game.host, p)));
  return { online: login, channels: channels.filter(Boolean).length, totalChannels: channels.length };
}

async function onlineCount() {
  const db = getPool(), g = env.gameDb;
  const sql = `SELECT COUNT(*) count FROM ${I(g.accountsTable)} WHERE ${I(g.accountLoggedIn)} > 0`;
  const [rows] = await db.query(sql);
  return Number(rows[0]?.count || 0);
}

async function rankings(limit=50, jobRange=null) {
  const db = getPool(), g = env.gameDb;
  const params = [];
  let jobClause = "";
  if (jobRange) {
    jobClause = `AND ${I(g.characterJob)} >= ? AND ${I(g.characterJob)} < ?`;
    params.push(jobRange[0], jobRange[1]);
  }
  const sql = `
    SELECT
      ${I(g.characterName)} name,
      ${I(g.characterLevel)} level,
      ${I(g.characterJob)} job,
      ${I(g.characterFame)} fame,
      ${I(g.characterExp)} exp
    FROM ${I(g.charactersTable)}
    WHERE COALESCE(${I(g.characterGm)},0) = 0 ${jobClause}
    ORDER BY ${I(g.characterLevel)} DESC, ${I(g.characterExp)} DESC
    LIMIT ?
  `;
  params.push(Number(limit));
  const [rows] = await db.query(sql, params);
  return rows;
}

async function login(username, password) {
  const db = getPool(), g = env.gameDb;
  const sql = `
    SELECT ${I(g.accountId)} id, ${I(g.accountName)} name,
           ${I(g.accountPassword)} password, ${I(g.accountBanned)} banned
    FROM ${I(g.accountsTable)}
    WHERE ${I(g.accountName)} = ?
    LIMIT 1
  `;
  const [rows] = await db.query(sql, [username]);
  const account = rows[0];
  if (!account || account.banned) return null;
  const ok = await verifyPassword(password, account.password);
  return ok ? { id: account.id, name: account.name } : null;
}

async function register({ username, password, email }) {
  if (!env.registration.enabled) throw new Error("Website registration is disabled.");
  const db = getPool(), g = env.gameDb;
  const hashed = await hashPassword(password, env.registration.mode);

  const sql = `
    INSERT INTO ${I(g.accountsTable)}
      (${I(g.accountName)}, ${I(g.accountPassword)}, ${I(g.accountEmail)}, ${I("tos")})
    VALUES (?, ?, ?, 1)
  `;
  await db.query(sql, [username, hashed, email]);
}

async function accountCharacters(accountId) {
  const db = getPool(), g = env.gameDb;
  const sql = `
    SELECT ${I(g.characterName)} name,
           ${I(g.characterLevel)} level,
           ${I(g.characterJob)} job,
           ${I(g.characterFame)} fame,
           ${I(g.characterExp)} exp
    FROM ${I(g.charactersTable)}
    WHERE ${I(g.characterAccountId)} = ?
    ORDER BY ${I(g.characterLevel)} DESC, ${I(g.characterExp)} DESC
  `;
  const [rows] = await db.query(sql, [Number(accountId)]);
  return rows;
}

async function changePassword(accountId, currentPassword, newPassword) {
  const db = getPool(), g = env.gameDb;
  const sql = `SELECT ${I(g.accountPassword)} password FROM ${I(g.accountsTable)} WHERE ${I(g.accountId)}=? LIMIT 1`;
  const [rows] = await db.query(sql, [Number(accountId)]);
  const account = rows[0];
  if (!account || !(await verifyPassword(currentPassword, account.password))) return false;
  const hashed = await hashPassword(newPassword, "bcrypt");
  await db.query(`UPDATE ${I(g.accountsTable)} SET ${I(g.accountPassword)}=? WHERE ${I(g.accountId)}=?`, [hashed, Number(accountId)]);
  return true;
}

async function voteBalance(accountId) {
  const db = getPool(), g = env.gameDb;
  const [rows] = await db.query(
    `SELECT COALESCE(${I(g.accountVotePoints)},0) votePoints FROM ${I(g.accountsTable)} WHERE ${I(g.accountId)}=? LIMIT 1`,
    [Number(accountId)]
  );
  return Number(rows[0]?.votePoints || 0);
}

function utcDateString(date = new Date()) {
  return date.toISOString().slice(0, 10);
}

/**
 * Credit a provider-verified vote exactly once per account/provider/UTC day.
 * The vote ledger insert and account balance mutation share one transaction,
 * so callback retries cannot mint duplicate Vote Points.
 */
async function rewardVerifiedVote({ username, provider, voterIp=null, reason=null, rewardPoints=1, votedAt=new Date() }) {
  const g = env.gameDb;
  const points = Number(rewardPoints);
  if (!/^[A-Za-z0-9_]{4,13}$/.test(String(username || ""))) {
    return { status: "invalid_username", rewarded: false };
  }
  if (!/^[a-z0-9_-]{2,32}$/.test(String(provider || ""))) {
    throw new Error("Invalid vote provider");
  }
  if (!Number.isInteger(points) || points < 1 || points > 10) {
    throw new Error("Invalid Vote Point reward amount");
  }

  const db = getPool();
  const con = await db.getConnection();
  try {
    await con.beginTransaction();
    const [accounts] = await con.query(
      `SELECT ${I(g.accountId)} id, ${I(g.accountName)} name, COALESCE(${I(g.accountVotePoints)},0) votePoints
       FROM ${I(g.accountsTable)}
       WHERE ${I(g.accountName)}=?
       LIMIT 1 FOR UPDATE`,
      [username]
    );
    const account = accounts[0];
    if (!account) {
      await con.rollback();
      return { status: "account_not_found", rewarded: false };
    }

    const voteDate = utcDateString(votedAt instanceof Date && !Number.isNaN(votedAt.valueOf()) ? votedAt : new Date());
    const [insert] = await con.query(
      `INSERT IGNORE INTO everleaf_vote_reward_ledger
         (account_id, provider, vote_date_utc, source_username, voter_ip, vote_points, provider_reason)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [account.id, provider, voteDate, account.name, voterIp ? String(voterIp).slice(0,45) : null, points, reason ? String(reason).slice(0,255) : null]
    );

    if (insert.affectedRows !== 1) {
      await con.commit();
      return { status: "already_rewarded", rewarded: false, accountId: account.id, votePoints: Number(account.votePoints) };
    }

    await con.query(
      `UPDATE ${I(g.accountsTable)} SET ${I(g.accountVotePoints)}=${I(g.accountVotePoints)}+? WHERE ${I(g.accountId)}=?`,
      [points, account.id]
    );
    await con.commit();
    return {
      status: "rewarded",
      rewarded: true,
      accountId: account.id,
      amount: points,
      votePoints: Number(account.votePoints) + points,
      voteDateUtc: voteDate
    };
  } catch (error) {
    try { await con.rollback(); } catch {}
    throw error;
  } finally {
    con.release();
  }
}

module.exports = {
  serverStatus,
  onlineCount,
  rankings,
  login,
  register,
  accountCharacters,
  changePassword,
  voteBalance,
  rewardVerifiedVote
};