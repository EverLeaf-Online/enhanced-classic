const assert = require("node:assert/strict");
const path = require("node:path");
const test = require("node:test");
const ejs = require("ejs");

test("primary navigation links directly to the official Discord server", async () => {
  const html = await ejs.renderFile(
    path.join(__dirname, "../src/views/partials/header.ejs"),
    {
      title: "Test",
      brand: { name: "EverLeaf", discordUrl: "https://discord.gg/w9ED8vtxa7" },
      currentPath: "/",
      player: null,
    },
  );

  assert.match(html, /href="https:\/\/discord\.gg\/w9ED8vtxa7"[^>]*target="_blank"[^>]*rel="noopener noreferrer"[^>]*>DISCORD<\/a>/);
  assert.doesNotMatch(html, />COMMUNITY<\/a>/);
  assert.doesNotMatch(html, /href="\/community"/);
});
