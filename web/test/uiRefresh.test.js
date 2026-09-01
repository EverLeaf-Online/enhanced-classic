const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname,"..");
const read = file => fs.readFileSync(path.join(root,file),"utf8");
const header = read("src/views/partials/header.ejs");
const footer = read("src/views/partials/footer.ejs");
const home = read("src/views/home.ejs");
const remaster = read("public/css/maple-remaster.css");
const pages = read("public/css/maple-remaster-pages.css");
const admin = read("public/css/maple-remaster-admin.css");

test("global navigation loads the unified Maple remaster design system",()=>{
  assert.match(header,/maple-remaster\.css/);
  assert.match(header,/maple-remaster-pages\.css/);
  assert.match(header,/maple-remaster-admin\.css/);
  assert.doesNotMatch(header,/design-v2\.css/);
  assert.doesNotMatch(header,/home-v2\.css/);
  assert.doesNotMatch(header,/cms-v2\.css/);
  assert.match(header,/mobileMenu/);
  assert.match(header,/siteBanner/);
  assert.match(header,/worldRibbon/);
});

test("footer exposes useful site navigation",()=>{
  assert.match(footer,/footerGrid/);
  assert.match(footer,/\/downloads/);
  assert.match(footer,/\/rankings/);
  assert.match(footer,/\/recover/);
});

test("homepage uses a materially different EverLeaf Maple layout while preserving local world art",()=>{
  assert.match(home,/everleaf-remaster\.svg/);
  assert.match(home,/homeV2Hero/);
  assert.match(home,/homeV2Status/);
  assert.match(home,/homeFeatureGrid/);
  assert.match(home,/homeCta/);
  assert.match(home,/hero-left\.webp/);
  assert.match(home,/hero-right\.webp/);
  assert.match(remaster,/hero-forest\.webp/);
});

test("remaster styles cover public pages, authentication, CMS and mobile layouts",()=>{
  for (const token of [".lightPage",".pageHeroGrid",".newsList",".authWrap","@media(max-width:820px)"]) assert.match(remaster,new RegExp(token.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")));
  assert.match(pages,/\.accountShell/);
  assert.match(pages,/\.helpGrid/);
  assert.match(admin,/\.cmsManagerNav/);
  assert.match(admin,/\.cmsWorkspace/);
  assert.match(admin,/@media\(max-width:600px\)/);
});
