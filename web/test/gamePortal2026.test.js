const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname,"..");
const read = file => fs.readFileSync(path.join(root,file),"utf8");
const header = read("src/views/partials/header.ejs");
const home = read("src/views/home.ejs");
const portal = read("public/css/game-portal-2026.css");
const refero = read("public/css/refero-everleaf-2026.css");

test("EverLeaf keeps the existing portal foundation beneath the final terminal layer",()=>{
  assert.match(header,/game-portal-2026\.css\?v=1/);
  assert.match(header,/full-site-portal-2026\.css\?v=1/);
  assert.match(header,/refero-everleaf-2026\.css\?v=2/);
  assert.match(header,/route-<%=routeKey%>/);
  assert.match(header,/route-admin/);
  assert.ok(header.indexOf("game-portal-2026.css") > header.indexOf("visuals-2026.css"));
  assert.ok(header.indexOf("refero-everleaf-2026.css") > header.indexOf("full-site-portal-2026.css"));
});

test("home portal uses local EverLeaf artwork inside the new terminal composition",()=>{
  assert.match(home,/\/assets\/hero-left\.webp/);
  assert.match(home,/\/assets\/hero-right\.webp/);
  assert.match(home,/terminalHero/);
  assert.match(home,/everleafArtifact/);
  assert.match(home,/heroTelemetry/);
  assert.match(home,/signalStrip/);
  assert.match(home,/classMatrix/);
  assert.match(refero,/\.terminalHero\{/);
  assert.match(refero,/\.everleafArtifact\{/);
  assert.match(refero,/\.terminalNav\{/);
});

test("portal styling remains original to EverLeaf and does not depend on foreign assets",()=>{
  for (const foreignToken of ["BeyondMS","beyond-ms.com","hero-world-day","landing-world-day","clouds-footer.png"]) {
    assert.doesNotMatch(portal,new RegExp(foreignToken,"i"));
    assert.doesNotMatch(refero,new RegExp(foreignToken,"i"));
    assert.doesNotMatch(header,new RegExp(foreignToken,"i"));
  }
  assert.doesNotMatch(refero,/https?:\/\//i);
  assert.doesNotMatch(refero,/@import/i);
});

test("terminal portal includes responsive and reduced-motion behavior",()=>{
  assert.match(refero,/@media \(max-width:960px\)/);
  assert.match(refero,/@media \(max-width:640px\)/);
  assert.match(refero,/@media \(prefers-reduced-motion:no-preference\)/);
  assert.match(refero,/prefers-reduced-motion/);
});
