const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const header = read('src/views/partials/header.ejs');
const design = read('DESIGN.md');
const css = read('public/css/refero-everleaf-2026.css');
const rankings = read('src/views/rankings.ejs');
const wiki = read('src/views/wiki.ejs');
const account = read('src/views/account.ejs');

test('EverLeaf design contract now targets the supplied Max Yinger Refero style', () => {
  assert.match(design, /Max Yinger/);
  assert.match(design, /#12130f/);
  assert.match(design, /#e4dfda/);
  assert.match(design, /No box shadows/);
  assert.match(design, /Pill interactions/);
  assert.match(design, /Edge-anchored composition/);
  assert.match(design, /Rankings/);
  assert.match(design, /Wiki/);
  assert.match(design, /Auth \/ Account/);
});

test('Max Yinger-inspired stylesheet is loaded last with server-rendered route classes', () => {
  const oldPortal = header.indexOf('/css/full-site-portal-2026.css?v=1');
  const refero = header.indexOf('/css/refero-everleaf-2026.css?v=2');
  assert.ok(oldPortal >= 0, 'existing portal layer should remain available');
  assert.ok(refero > oldPortal, 'final Refero layer must load after the existing portal layer');
  assert.match(header, /const routeKey=/);
  assert.match(header, /route-<%=routeKey%>/);
  assert.match(header, /theme-color" content="#12130f"/);
  assert.match(header, /color-scheme" content="dark"/);
});

test('new terminal system covers the full public website, not just home', () => {
  for (const selector of [
    'body.homeRoute:not(.route-admin) .mapleHero',
    'body.innerRoute:not(.route-admin) .lightTitle',
    'body:not(.route-admin) .newsList',
    'body:not(.route-admin) .downloadGrid',
    'body:not(.route-admin) .rankingPodium',
    'body:not(.route-admin) .wikiDataSearch',
    'body:not(.route-admin) .helpGrid',
    'body:not(.route-admin) .authWrap',
    'body:not(.route-admin) .accountPage',
    'body:not(.route-admin) .siteFooter'
  ]) assert.ok(css.includes(selector), `missing full-site terminal coverage for ${selector}`);

  assert.match(css, /@media\(max-width:960px\)/);
  assert.match(css, /@media\(max-width:640px\)/);
  assert.match(css, /@media\(prefers-reduced-motion:reduce\)/);
});

test('style tokens follow the supplied dark two-color system with rose reserved for art glow', () => {
  assert.match(css, /--el-carbon:#12130f/);
  assert.match(css, /--el-bone:#e4dfda/);
  assert.match(css, /--el-vein:#3c3c38/);
  assert.match(css, /--el-rose:#f5c2c8/);
  assert.match(css, /border-radius:9999px/);
  assert.match(css, /box-shadow:none!important/);
  assert.match(css, /font:400 12px\/1\.25 var\(--el-mono\)/);
  assert.doesNotMatch(css, /--el-paper:/);
  assert.doesNotMatch(css, /--el-leaf:/);
  assert.doesNotMatch(css, /#59ad62/i);
});

test('redesign preserves live product integrations', () => {
  assert.match(rankings, /data-live-avatar/);
  assert.match(rankings, /\/character-avatar\//);
  assert.match(wiki, /WZ \+ MySQL/);
  assert.match(account, /\/account\/password/);
  assert.match(account, /\/account\/discord\/connect/);
});

test('redesign does not import reference-site assets, fonts, or remote styles', () => {
  assert.doesNotMatch(css, /https?:\/\//i);
  assert.doesNotMatch(css, /@import/i);
  assert.doesNotMatch(css, /refero\.design|styles\.refero/i);
  assert.doesNotMatch(css, /Arbeit Technik|Inline VF|Arbeit Contrast/i);
});
