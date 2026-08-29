const { spawnSync } = require("node:child_process");

const [username] = process.argv.slice(2);
if (!username) throw new Error("Username is required.");
if (!/^e2e[a-z0-9]{4,10}$/.test(username)) throw new Error("Refusing to remove a non-E2E account.");

const sql = `
DELETE a
FROM accounts a
LEFT JOIN characters c ON c.accountid = a.id
WHERE BINARY a.name = '${username}'
  AND a.email LIKE '%@example.invalid'
  AND c.id IS NULL;
SELECT ROW_COUNT();
`;
const result = spawnSync("mysql", ["--batch", "--skip-column-names", "cosmic"], {
  input: sql,
  encoding: "utf8",
});
if (result.status !== 0) throw new Error(`Temporary account cleanup failed: ${result.stderr.trim()}`);
if (result.stdout.trim() !== "1") throw new Error("Temporary E2E account cleanup did not remove exactly one safe row.");
console.log("TEMPORARY_ACCOUNT_REMOVED=true");
