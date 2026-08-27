const mysql = require("mysql2/promise");
const env = require("../config/env");

let pool;

function safeIdent(v) {
  if (!/^[A-Za-z0-9_]+$/.test(v)) throw new Error("Unsafe SQL identifier");
  return `\`${v}\``;
}

function getPool() {
  if (!pool) {
    pool = mysql.createPool({
      host: env.gameDb.host,
      port: env.gameDb.port,
      user: env.gameDb.user,
      password: env.gameDb.password,
      database: env.gameDb.database,
      waitForConnections: true,
      connectionLimit: 5,
      queueLimit: 20,
      enableKeepAlive: true
    });
  }
  return pool;
}

module.exports = { getPool, safeIdent };
