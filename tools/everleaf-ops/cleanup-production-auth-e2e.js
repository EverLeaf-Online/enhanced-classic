const fs = require("node:fs");
const path = require("node:path");
const { createRequire } = require("node:module");

const [webRoot, envPath, username] = process.argv.slice(2);
if (!webRoot || !envPath || !username) throw new Error("Web root, environment path, and username are required.");
if (!/^e2e[a-z0-9]{4,10}$/.test(username)) throw new Error("Refusing to remove a non-E2E account.");

const env = Object.fromEntries(
  fs.readFileSync(envPath, "utf8")
    .split(/\r?\n/)
    .filter((line) => line && !line.startsWith("#") && line.includes("="))
    .map((line) => [line.slice(0, line.indexOf("=")), line.slice(line.indexOf("=") + 1)]),
);
const requireFromWeb = createRequire(path.join(path.resolve(webRoot), "package.json"));
const mysql = requireFromWeb("mysql2/promise");

(async () => {
  const connection = await mysql.createConnection({
    host: env.GAME_DB_HOST,
    port: Number(env.GAME_DB_PORT || 3306),
    user: env.GAME_DB_USER,
    password: env.GAME_DB_PASSWORD,
    database: env.GAME_DB_NAME,
  });
  try {
    await connection.beginTransaction();
    const [accountRows] = await connection.execute(
      "SELECT id FROM accounts WHERE BINARY name = ? AND email LIKE '%@example.invalid' FOR UPDATE",
      [username],
    );
    if (accountRows.length !== 1) throw new Error("Expected exactly one temporary E2E account.");
    const [characterRows] = await connection.execute(
      "SELECT COUNT(*) AS total FROM characters WHERE accountid = ?",
      [accountRows[0].id],
    );
    if (Number(characterRows[0].total) !== 0) throw new Error("Refusing to remove an E2E account that owns characters.");
    const [result] = await connection.execute("DELETE FROM accounts WHERE id = ? AND BINARY name = ?", [accountRows[0].id, username]);
    if (result.affectedRows !== 1) throw new Error("Temporary E2E account cleanup did not remove exactly one row.");
    await connection.commit();
    console.log("TEMPORARY_ACCOUNT_REMOVED=true");
  } catch (error) {
    await connection.rollback();
    throw error;
  } finally {
    await connection.end();
  }
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
