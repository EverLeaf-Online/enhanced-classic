const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const header = read('src/views/partials/header.ejs');
const css = read('public/css/app-frame-v2-2026.css');
const rankings = read('src/views/rankings.ejs');
const wiki = read('src/views/wiki.ejs');

test('public routes use the viewport app frame after all prior style layers', () => {
  const clean = header.indexOf('/css/inner-app-clean-2026.css?v=1');
  const frame = header.indexOf('/css/app-frame-v2-2026.css?v=1');
  assert.ok(clean >= 0);
  assert.ok(frame > clean);
  assert.match(css, /height:100dvh!important/);
  assert.match(css, /overflow:hidden!important/);
  assert.match(css, /\.siteContent>main/);
  assert.match(css, /overscroll-behavior:contain/);
});

test('rankings are treated as a dense data workspace', () => {
  for (const token of ['rankingStats','rankingSearch','rankingTabs','rankingPodium','rankingBoardV2','rankingTableV2']) {
    assert.match(rankings, new RegExp(token));
  }
  assert.match(css, /body\.route-rankings \.siteContent>main/);
  assert.match(css, /grid-template-rows:auto minmax\(0,1fr\)/);
  assert.match(css, /Top three are a compact leader strip/);
  assert.match(css, /thead\{position:sticky/);
});

test('wiki is treated as a compact searchable workspace', () => {
  assert.match(wiki, /wikiDataSearch/);
  assert.match(wiki, /wikiCatalogGrid/);
  assert.match(wiki, /wikiDataResultGrid/);
  assert.match(css, /body\.route-wiki \.siteContent>main\.wikiDataPage/);
  assert.match(css, /Search is the dominant Wiki control/);
  assert.match(css, /grid-template-columns:repeat\(3,minmax\(0,1fr\)\)/);
});

test('app frame does not import remote assets or affect admin styling', () => {
  assert.match(css, /:not\(\.route-admin\)/);
  assert.doesNotMatch(css, /@import|https?:\/\//i);
});
