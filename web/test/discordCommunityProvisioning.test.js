const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");

const script = fs.readFileSync(
  path.resolve(__dirname, "../../tools/everleaf-ops/provision-discord-community.js"),
  "utf8",
);

test("Discord community messages are reconciled instead of only seeded once", () => {
  assert.match(script, /async function ensureBotMessage/);
  assert.match(script, /method: "PATCH"/);
  assert.doesNotMatch(script, /created\.get\("downloads-and-links"\)\?\.created/);
});

test("official Discord links use the production domain", () => {
  assert.match(script, /https:\/\/everleafms\.online\/downloads/);
  assert.match(script, /https:\/\/everleafms\.online\/account/);
  assert.doesNotMatch(script, /everleafms\.duckdns\.org/);
});
