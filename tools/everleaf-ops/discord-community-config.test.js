const fs = require("node:fs");
const test = require("node:test");
const assert = require("node:assert/strict");

const source = fs.readFileSync(require.resolve("./provision-discord-community"), "utf8");

test("preserves forum channels instead of creating text-channel duplicates", () => {
  assert.match(source, /channelSpec\("suggestions", 15,/);
  assert.match(source, /channelSpec\("bug-reports", 15,/);
  assert.match(source, /refusing to create a duplicate/);
});

test("does not delete channels and limits cleanup to legacy bot status posts", () => {
  assert.match(source, /message\.author\?\.id === botId/);
  assert.match(source, /EverLeaf Status Alert/);
  assert.match(source, /\/messages\/\$\{message\.id\}/);
  assert.equal((source.match(/method:\s*["']DELETE["']/g) || []).length, 1);
  assert.match(source, /discord_existing_channels_deleted=0/);
});

test("uses the current 20-channel topology in the bug template", () => {
  assert.match(source, /CH1–CH20/);
  assert.doesNotMatch(source, /CH1–CH8/);
});

test("keeps the class guides read-only and moves known issues into news", () => {
  assert.match(source, /guides: await ensureCategory\(channels, \{ name: "📚 CLASS GUIDES", fallbackName: "Wiki" \}\)/);
  assert.doesNotMatch(source, /guides: await ensureCategory\([^\n]+permission_overwrites: readOnlyOverwrites/);
  assert.match(source, /channelSpec\("known-issues", 0, categories\.news/);
  assert.match(source, /channelSpec\("class-overview"[^\n]+permission_overwrites: readOnlyOverwrites/);
  assert.match(source, /skill-changelog[^\n]+permission_overwrites: readOnlyOverwrites/);
});

test("reports safe category and channel context for Discord mutation failures", () => {
  assert.match(source, /category=\$\{spec\.name\}/);
  assert.match(source, /channel=\$\{spec\.name\}/);
});
