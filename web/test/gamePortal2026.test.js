const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname,"..");
const read = file => fs.readFileSync(path.join(root,file),"utf8");
const header = read("src/views/partials/header.ejs");
const home = read("src/views/home.ejs");
const portal = read("public/css/game-portal-2026.css");

test("EverLeaf keeps the immersive game-portal foundation under the final design layer",()=>{
  assert.match(header,/game-portal-2026\.css\?v=1/);
  assert.match(header,/body class="<%=isHome\?'homeRoute':'innerRoute'%> route-<%=routeKey%>"/);
  assert.ok(header.indexOf("game-portal-2026.css") > header.indexOf("visuals-2026.css"));
  assert.ok(header.indexOf("refero-everleaf-2026.css") > header.indexOf("game-portal-2026.css"));
});

test("home portal uses EverLeaf local artwork and an immersive floating navigation",()=>{
  assert.match(home,/\/assets\/hero-left\.webp/);
  assert.match(home,/\/assets\/hero-right\.webp/);
  assert.match(portal,/body\.homeRoute \.nav\{/);
  assert.match(portal,/position:fixed!important/);
  assert.match(portal,/backdrop-filter:blur\(18px\)/);
  assert.match(portal,/body\.homeRoute \.mapleHero\{/);
  assert.match(portal,/everleafWorldBreath/);
  assert.match(portal,/body\.homeRoute \.mapleQuick/);
  assert.match(portal,/body\.homeRoute \.everleafPromises/);
  assert.match(portal,/body\.homeRoute \.mapleJobsPolished/);
});

test("portal styling remains original to EverLeaf and does not depend on reference-site assets",()=>{
  for (const foreignToken of ["BeyondMS","beyond-ms.com","hero-world-day","landing-world-day","clouds-footer.png"]) {
    assert.doesNotMatch(portal,new RegExp(foreignToken,"i"));
    assert.doesNotMatch(header,new RegExp(foreignToken,"i"));
  }
  assert.match(portal,/EverLeaf immersive game portal/);
});

test("portal includes responsive and reduced-motion behavior",()=>{
  assert.match(portal,/@media\(max-width:900px\)/);
  assert.match(portal,/@media\(max-width:640px\)/);
  assert.match(portal,/@media\(prefers-reduced-motion:reduce\)/);
});
