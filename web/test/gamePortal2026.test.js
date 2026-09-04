const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname,"..");
const read = file => fs.readFileSync(path.join(root,file),"utf8");
const header = read("src/views/partials/header.ejs");
const home = read("src/views/home.ejs");
const terminal = read("public/css/terminal-everleaf-2026.css");

test("EverLeaf loads the new terminal architecture after the legacy compatibility layers",()=>{
  assert.match(header,/game-portal-2026\.css\?v=1/);
  assert.match(header,/refero-everleaf-2026\.css\?v=1/);
  assert.match(header,/terminal-everleaf-2026\.css\?v=1/);
  assert.match(header,/body class="terminalMode/);
  assert.ok(header.indexOf("terminal-everleaf-2026.css") > header.indexOf("refero-everleaf-2026.css"));
});

test("home portal is structurally rebuilt around a full viewport world terminal",()=>{
  assert.match(home,/\/assets\/hero-left\.webp/);
  assert.match(home,/\/assets\/hero-right\.webp/);
  assert.match(home,/terminalHero/);
  assert.match(home,/terminalHeroArtifact/);
  assert.match(home,/terminalWorldReadout/);
  assert.match(home,/terminalHeroActions/);
  assert.match(home,/terminalSection/);
  assert.match(home,/terminalJobGrid/);
  assert.match(home,/terminalRankingPreview/);
  assert.match(terminal,/\.terminalHero\{/);
  assert.match(terminal,/min-height:100svh/);
});

test("terminal styling remains original to EverLeaf and does not depend on reference-site assets",()=>{
  for (const foreignToken of ["BeyondMS","beyond-ms.com","hero-world-day","landing-world-day","clouds-footer.png","styles.refero.design"]) {
    assert.doesNotMatch(terminal,new RegExp(foreignToken,"i"));
    assert.doesNotMatch(header,new RegExp(foreignToken,"i"));
  }
  assert.doesNotMatch(terminal,/https?:\/\//i);
});

test("terminal portal includes responsive and reduced-motion behavior",()=>{
  assert.match(terminal,/@media\(max-width:980px\)/);
  assert.match(terminal,/@media\(max-width:720px\)/);
  assert.match(terminal,/@media\(prefers-reduced-motion:reduce\)/);
});
