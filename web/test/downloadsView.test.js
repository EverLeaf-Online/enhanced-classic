const assert = require("node:assert/strict");
const path = require("node:path");
const test = require("node:test");
const ejs = require("ejs");

test("downloads page uses the launcher as the complete bootstrap", async () => {
  const html = await ejs.renderFile(
    path.join(__dirname, "../src/views/downloads.ejs"),
    {
      brand: {
        name: "EverLeaf",
        launcherUrl: "/launcher/download"
      },
      rows: [],
      settings: {footer_note: "test"},
      currentPath: "/downloads",
      player: null
    }
  );

  assert.doesNotMatch(html, /DOWNLOAD FULL CLIENT/);
  assert.doesNotMatch(html, /RAR archive/);
  assert.match(html, /EverLeaf Launcher/);
  assert.match(html, /href="\/launcher\/download"/);
  assert.match(html, /all 36 required files/);
  assert.match(html, /Install EverLeaf/);
  assert.match(html, /starting <strong>EverLeaf\.exe<\/strong>/);
  assert.doesNotMatch(html, /beside <strong>MapleStory\.exe<\/strong>/);
  assert.doesNotMatch(html, /Install the EverLeaf Launcher/);
});
