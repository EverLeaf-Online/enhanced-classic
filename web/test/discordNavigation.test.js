const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.join(__dirname, "..");
const home = fs.readFileSync(path.join(root, "src/views/home.ejs"), "utf8");
const footer = fs.readFileSync(path.join(root, "src/views/partials/footer.ejs"), "utf8");
const header = fs.readFileSync(path.join(root, "src/views/partials/header.ejs"), "utf8");

test("Discord remains accessible without restoring the removed top navigation", () => {
  assert.doesNotMatch(header, /terminalNav|mobileMenu|worldRibbon|terminalRibbon/);
  assert.match(home, /href="<%=brand\.discordUrl%>" target="_blank" rel="noopener noreferrer"><span>05<\/span><strong>DISCORD<\/strong><small>Community \+ support<\/small><\/a>/);
  assert.match(footer, /href="<%=brand\.discordUrl%>" target="_blank" rel="noopener noreferrer">DISCORD ↗<\/a>/);
  assert.doesNotMatch(header, /href="\/community"/);
});
