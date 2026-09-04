#!/usr/bin/env node
const { getPool, safeIdent: I } = require("../src/db/game");
const env = require("../src/config/env");
const { hashPassword } = require("../src/utils/password");
const passwordPolicy = require("../src/utils/playerPasswordPolicy");

function readSecret(prompt) {
  if (!process.stdin.isTTY || typeof process.stdin.setRawMode !== "function") {
    throw new Error("Run this command in an interactive terminal.");
  }
  process.stdout.write(prompt);
  process.stdin.setRawMode(true);
  process.stdin.resume();
  process.stdin.setEncoding("utf8");

  return new Promise((resolve, reject) => {
    let value = "";
    const finish = (error) => {
      process.stdin.setRawMode(false);
      process.stdin.pause();
      process.stdin.removeListener("data", onData);
      process.stdout.write("\n");
      if (error) reject(error); else resolve(value);
    };
    const onData = chunk => {
      for (const character of chunk) {
        if (character === "\u0003") return finish(new Error("Cancelled."));
        if (character === "\r" || character === "\n") return finish();
        if (character === "\u007f" || character === "\b") value = value.slice(0, -1);
        else value += character;
      }
    };
    process.stdin.on("data", onData);
  });
}

async function main() {
  const username = process.argv[2];
  if (!username || !/^[A-Za-z0-9_]{4,13}$/.test(username)) {
    throw new Error("Usage: npm run reset-player-password -- <username>");
  }

  const password = await readSecret("New 8-12 character password: ");
  const confirmation = await readSecret("Confirm new password: ");
  if (!passwordPolicy.loginPassword.safeParse(password).success ||
      password.length < passwordPolicy.MIN_LENGTH || password.length > passwordPolicy.MAX_LENGTH) {
    throw new Error(passwordPolicy.REQUIREMENT);
  }
  if (password !== confirmation) throw new Error("Passwords do not match.");

  const db = getPool(), g = env.gameDb;
  const hash = await hashPassword(password, "bcrypt");
  const [result] = await db.query(
    `UPDATE ${I(g.accountsTable)} SET ${I(g.accountPassword)}=? WHERE ${I(g.accountName)}=? LIMIT 1`,
    [hash, username]
  );
  await db.end();
  if (result.affectedRows !== 1) throw new Error("Account was not found.");
  console.log(`Password reset completed for ${username}.`);
}

main().catch(error => {
  console.error(error.message);
  process.exitCode = 1;
});
