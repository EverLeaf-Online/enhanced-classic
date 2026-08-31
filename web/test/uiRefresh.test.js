const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname,"..");
const read = file => fs.readFileSync(path.join(root,file),"utf8");
const header = read("src/views/partials/header.ejs");
const footer = read("src/views/partials/footer.ejs");
const home = read("src/views/home.ejs");
const design = read("public/css/design-v2.css");
const homeCss = read("public/css/home-v2.css");
const cmsCss = read("public/css/cms-v2.css");

test("global navigation loads the complete responsive design system",()=>{
  assert.match(header,/design-v2\.css/);
  assert.match(header,/home-v2\.css/);
  assert.match(header,/cms-v2\.css/);
  assert.match(header,/mobileMenu/);
  assert.match(header,/siteBanner/);
});

test("footer exposes useful site navigation",()=>{
  assert.match(footer,/footerGrid/);
  assert.match(footer,/\/downloads/);
  assert.match(footer,/\/rankings/);
  assert.match(footer,/\/recover/);
});

test("homepage uses a materially different EverLeaf layout while preserving brand art",()=>{
  assert.match(home,/everleaf-logo\.webp/);
  assert.match(home,/homeV2Hero/);
  assert.match(home,/homeV2Status/);
  assert.match(home,/homeFeatureGrid/);
  assert.match(home,/homeCta/);
  assert.match(homeCss,/hero-forest\.webp/);
});

test("v2 styles cover public pages, authentication, CMS and mobile layouts",()=>{
  for (const token of [".lightPage",".pageHeroGrid",".newsList",".accountShell",".authWrap",".adminShell","@media(max-width:720px)"]) assert.match(design,new RegExp(token.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")));
  assert.match(cmsCss,/\.cmsManagerNav/);
  assert.match(cmsCss,/\.cmsWorkspace/);
  assert.match(cmsCss,/@media\(max-width:620px\)/);
});
