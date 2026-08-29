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
  assert.match(cleanup, /FROM characters WHERE accountid/);
  assert.match(cleanup, /affectedRows !== 1/);
});
