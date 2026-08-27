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

module.exports = { serverStatus, onlineCount, rankings, login, register, accountCharacters, changePassword };
