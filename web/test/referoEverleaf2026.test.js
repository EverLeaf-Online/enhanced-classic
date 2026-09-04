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

test('EverLeaf keeps a repo-resident design contract for the redesign', () => {
  assert.match(design, /Storybook field journal meets classic MMORPG portal/);
  assert.match(design, /Game world first/);
  assert.match(design, /Rankings/);
  assert.match(design, /Wiki/);
  assert.match(design, /Account \/ Auth/);
  assert.match(design, /Do not/);
  assert.match(design, /proprietary fonts/);
});

test('Refero-informed stylesheet is loaded last with server-rendered route classes', () => {
  const oldPortal = header.indexOf('/css/full-site-portal-2026.css?v=1');
  const refero = header.indexOf('/css/refero-everleaf-2026.css?v=1');
  assert.ok(oldPortal >= 0, 'existing portal layer should remain available');
  assert.ok(refero > oldPortal, 'Refero-informed layer must load after the existing portal layer');
  assert.match(header, /const routeKey=/);
  assert.match(header, /route-<%=routeKey%>/);
  assert.match(header, /theme-color" content="#173f38"/);
});

test('new system deliberately covers all major public surfaces', () => {
  for (const selector of [
    'body.homeRoute:not(.route-admin) .mapleHero',
    'body.route-news .newsList',
    'body.route-downloads .contentGrid',
    'body.route-rankings .rankingPodium',
    'body.route-wiki .wikiDataHero',
    'body.route-help .helpGrid',
    'body.route-login .authWrap',
    'body.route-register .authWrap',
    'body.route-recover .authWrap',
    'body.route-account .accountShell',
    'body:not(.route-admin) .siteFooter'
  ]) assert.ok(css.includes(selector), `missing Refero redesign coverage for ${selector}`);

  assert.match(css, /@media \(max-width:820px\)/);
  assert.match(css, /@media \(prefers-reduced-motion:reduce\)/);
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
  assert.doesNotMatch(css, /Recoleta|Suisse|Jersey 10|Manrope/i);
  assert.match(css, /--el-paper:#fbf6e9/);
  assert.match(css, /--el-leaf:#59ad62/);
});
