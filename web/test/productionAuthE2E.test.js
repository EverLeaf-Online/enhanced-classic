const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");

const cleanup = fs.readFileSync(
  path.resolve(__dirname, "../../tools/everleaf-ops/cleanup-production-auth-e2e.js"),
  "utf8",
);

test("production authentication cleanup is restricted to empty E2E accounts", () => {
  assert.match(cleanup, /\^e2e\[a-z0-9\]/);
  assert.match(cleanup, /@example\.invalid/);
  assert.match(cleanup, /LEFT JOIN characters c ON c\.accountid = a\.id/);
  assert.match(cleanup, /c\.id IS NULL/);
  assert.match(cleanup, /stdout\.trim\(\) !== "1"/);
  assert.doesNotMatch(cleanup, /GAME_DB_PASSWORD/);
});
