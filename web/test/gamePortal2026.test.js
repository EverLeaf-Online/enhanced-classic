const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname,"..");
const read = file => fs.readFileSync(path.join(root,file),"utf8");
const header = read("src/views/partials/header.ejs");
const home = read("src/views/home.ejs");
const siteJs = read("public/js/site.js");
const unified = read("public/css/unified-terminal-2026.css");
const refero = read("public/css/refero-everleaf-2026.css");

test("EverLeaf no longer loads or injects the legacy split portal shells",()=>{
  assert.doesNotMatch(header,/game-portal-2026\.css/);
  assert.doesNotMatch(header,/full-site-portal-2026\.css/);
  assert.doesNotMatch(header,/visuals-2026\.css/);
  assert.doesNotMatch(siteJs,/full-site-portal-2026\.css/);
  assert.doesNotMatch(siteJs,/data-everleaf-full-site-portal/);
  assert.match(header,/refero-everleaf-2026\.css\?v=3/);
  assert.match(header,/unified-terminal-2026\.css\?v=1/);
  assert.match(header,/body class="siteRoute route-<%=routeKey%>/);
});

test("home portal uses local EverLeaf artwork inside the terminal composition",()=>{
  assert.match(home,/\/assets\/hero-left\.webp/);
  assert.match(home,/\/assets\/hero-right\.webp/);
  assert.match(home,/terminalHero/);
  assert.match(home,/everleafArtifact/);
  assert.match(home,/heroTelemetry/);
  assert.match(home,/signalStrip/);
  assert.match(refero,/\.terminalHero\{/);
  assert.match(refero,/\.everleafArtifact\{/);
  assert.match(unified,/One header, every route/);
});

test("removed homepage areas stay removed",()=>{
  assert.doesNotMatch(home,/CHOOSE YOUR SIGNAL/i);
  assert.doesNotMatch(home,/classMatrix/);
  assert.doesNotMatch(home,/KNOW THE WORLD/i);
  assert.doesNotMatch(home,/wikiSignalSection/);
});

test("unified shell explicitly suppresses legacy ribbon decorations",()=>{
  assert.match(unified,/legacy scallop\/ribbon\/cloud decoration/i);
  assert.match(unified,/body\.siteRoute \.nav::after/);
  assert.match(unified,/body\.siteRoute \.lightTitle::after/);
  assert.match(unified,/@media\(max-width:960px\)/);
  assert.match(unified,/@media\(max-width:640px\)/);
});
