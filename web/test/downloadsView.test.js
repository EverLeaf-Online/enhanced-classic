const assert = require("node:assert/strict");
const path = require("node:path");
const test = require("node:test");
const ejs = require("ejs");

test("downloads page separates the complete client and portable launcher", async () => {
  const html = await ejs.renderFile(
    path.join(__dirname, "../src/views/downloads.ejs"),
    {
      brand: {
        name: "EverLeaf",
        clientUrl: "https://downloads.example/full-client.rar",
        launcherUrl: "/launcher/download"
      },
      rows: [],
      settings: {footer_note: "test"},
      currentPath: "/downloads",
      player: null
    }
  );

  assert.match(html, /DOWNLOAD FULL CLIENT/);
  assert.match(html, /href="https:\/\/downloads\.example\/full-client\.rar"/);
  assert.match(html, /EverLeaf Portable Launcher/);
  assert.match(html, /href="\/launcher\/download"/);
  assert.match(html, /all 36 required files/);
  assert.match(html, /starting <strong>EverLeaf\.exe<\/strong>/);
  assert.doesNotMatch(html, /beside <strong>MapleStory\.exe<\/strong>/);
  assert.doesNotMatch(html, /Install the EverLeaf Launcher/);
});
