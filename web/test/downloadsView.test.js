const assert = require("node:assert/strict");
const path = require("node:path");
const test = require("node:test");
const ejs = require("ejs");

test("downloads page uses the launcher as the complete bootstrap", async () => {
  const html = await ejs.renderFile(
    path.join(__dirname, "../src/views/downloads.ejs"),
    {
      brand: { name: "EverLeaf", version: "v83", launcherUrl: "/launcher/download", discordUrl: "#" },
      rows: [], settings: {footer_note: "test"}, currentPath: "/downloads", player: null
    }
  );
  assert.doesNotMatch(html, /DOWNLOAD FULL CLIENT/);
  assert.doesNotMatch(html, /RAR archive/);
  assert.match(html, /EVERLEAF LAUNCHER/);
  assert.match(html, /href="\/launcher\/download"/);
  assert.match(html, /installs, verifies, repairs, updates/i);
  assert.match(html, /Install EverLeaf/);
  assert.match(html, /<strong>EverLeaf\.exe<\/strong>/);
  assert.doesNotMatch(html, /beside <strong>MapleStory\.exe<\/strong>/);
  assert.match(html, /terminalDeployPage/);
  assert.match(html, /terminalManifest/);
});
