const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const header = read('src/views/partials/header.ejs');
const design = read('DESIGN.md');
const css = read('public/css/max-yinger-everleaf-2026.css');
const rankings = read('src/views/rankings.ejs');
const wiki = read('src/views/wiki.ejs');
const account = read('src/views/account.ejs');

test('EverLeaf now targets the supplied Max Yinger Refero system', () => {
  assert.match(design, /Max Yinger/);
  assert.match(design, /#12130f/);
  assert.match(design, /#e4dfda/);
  assert.match(design, /No box shadows/);
  assert.match(design, /Rankings/);
  assert.match(design, /Wiki/);
  assert.match(design, /Auth \/ Account/);
});

test('Max Yinger layer loads last with dark metadata and route-aware shell', () => {
  const previous = header.indexOf('/css/refero-everleaf-2026.css?v=1');
  const finalLayer = header.indexOf('/css/max-yinger-everleaf-2026.css?v=1');
  assert.ok(previous >= 0, 'previous public layer remains available underneath');
  assert.ok(finalLayer > previous, 'Max Yinger layer must be the final public CSS authority');
  assert.match(header, /const routeKey=/);
  assert.match(header, /route-<%=routeKey%>/);
  assert.match(header, /theme-color" content="#12130f"/);
  assert.match(header, /color-scheme" content="dark"/);
});

test('terminal system covers all major public surfaces', () => {
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
  ]) assert.ok(css.includes(selector), `missing Max Yinger redesign coverage for ${selector}`);
  assert.match(css, /@media\(max-width:960px\)/);
  assert.match(css, /@media\(max-width:640px\)/);
  assert.match(css, /@media\(prefers-reduced-motion:reduce\)/);
});

test('tokens match the supplied near-black and bone-white design', () => {
  assert.match(css, /--my-carbon:#12130f/);
  assert.match(css, /--my-bone:#e4dfda/);
  assert.match(css, /--my-vein:#3c3c38/);
  assert.match(css, /--my-rose:#f5c2c8/);
  assert.match(css, /border-radius:9999px/);
  assert.match(css, /box-shadow:none!important/);
  assert.doesNotMatch(css, /#59ad62/i);
  assert.doesNotMatch(css, /#fbf6e9/i);
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
