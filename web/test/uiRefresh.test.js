const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname,"..");
const read = file => fs.readFileSync(path.join(root,file),"utf8");
const header = read("src/views/partials/header.ejs");
const footer = read("src/views/partials/footer.ejs");
const home = read("src/views/home.ejs");
const css = read("public/css/refresh.css");

test("global navigation has responsive mobile controls",()=>{
  assert.match(header,/refresh\.css/);
  assert.match(header,/mobileMenu/);
  assert.match(header,/mobileMenuPanel/);
  assert.match(header,/siteBanner/);
});

test("footer exposes useful site navigation",()=>{
  assert.match(footer,/footerGrid/);
  assert.match(footer,/\/downloads/);
  assert.match(footer,/\/rankings/);
  assert.match(footer,/\/recover/);
});

test("homepage keeps EverLeaf art while improving hierarchy",()=>{
  assert.match(home,/hero-forest\.webp/);
  assert.match(home,/everleaf-logo\.webp/);
  assert.match(home,/homeFeatureGrid/);
  assert.match(home,/homeCta/);
});

test("refresh stylesheet covers public, auth, CMS and responsive layouts",()=>{
  for (const token of [".mobileMenu",".homeFeatureGrid",".lightPage",".authCard",".adminShell",".siteFooter","@media(max-width:900px)"]) assert.match(css,new RegExp(token.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")));
});
