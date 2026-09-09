const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const header = read('src/views/partials/header.ejs');
const design = read('DESIGN.md');
const css = read('public/css/refero-everleaf-2026.css');
const unified = read('public/css/unified-terminal-2026.css');
const siteJs = read('public/js/site.js');
const home = read('src/views/home.ejs');
const rankings = read('src/views/rankings.ejs');
const wiki = read('src/views/wiki.ejs');
const account = read('src/views/account.ejs');

test('EverLeaf keeps a repo-resident terminal design contract', () => {
  assert.match(design, /Midnight Maple terminal/);
  assert.match(design, /Full-bleed composition/);
  assert.match(design, /Typography is the main graphic/);
  assert.match(design, /Rankings/);
  assert.match(design, /Wiki/);
  assert.match(design, /Account \/ Auth/);
  assert.match(design, /Do not/);
});

test('one shared terminal shell is loaded after the base styles', () => {
  const refero = header.indexOf('/css/refero-everleaf-2026.css?v=3');
  const unifiedIndex = header.indexOf('/css/unified-terminal-2026.css?v=1');
  assert.ok(refero >= 0);
  assert.ok(unifiedIndex > refero);
  assert.match(header, /const routeKey=/);
  assert.match(header, /body class="siteRoute route-<%=routeKey%>/);
  assert.match(header, /theme-color" content="#12130f"/);
  assert.match(header, /color-scheme" content="dark"/);
  assert.doesNotMatch(header, /game-portal-2026\.css|full-site-portal-2026\.css|visuals-2026\.css/);
  assert.doesNotMatch(header, /terminalNav|worldRibbon|mobileMenu/);
  assert.doesNotMatch(siteJs, /full-site-portal-2026\.css/);
});

test('new system deliberately covers the simplified homepage and major shared surfaces', () => {
  for (const selector of [
    '.terminalHero', '.signalStrip', '.lightPage', '.authWrap',
    '.rankingTable', '.wikiSearch', '.terminalFooter'
  ]) assert.ok(css.includes(selector), `missing terminal redesign coverage for ${selector}`);

  for (const selector of [
    'body.siteRoute', 'body.siteRoute:not(.route-home) .lightTitle',
    'body.route-news .newsList', 'body.route-downloads .contentGrid',
    'body.route-rankings .rankingStats', 'body.route-wiki .wikiShell'
  ]) assert.ok(unified.includes(selector), `missing unified shell coverage for ${selector}`);

  for(const token of ['terminalHero','everleafArtifact','heroTelemetry','signalStrip']) {
    assert.ok(home.includes(token), `homepage should include ${token}`);
  }
  for(const token of ['terminalHome','dossierSection','entrySection','dataSection','dataSplit','finalTransmission']) {
    assert.ok(!home.includes(token), `homepage should not include removed ${token}`);
  }
  assert.doesNotMatch(home, /classMatrix|wikiSignalSection|CHOOSE YOUR SIGNAL|KNOW THE WORLD/i);
});

test('redesign preserves live product integrations', () => {
  assert.match(home, /id="live-dot"/);
  assert.match(home, /id="live-status"/);
  assert.match(home, /id="live-players"/);
  assert.match(home, /id="live-channels"/);
  assert.match(rankings, /data-live-avatar/);
  assert.match(rankings, /\/character-avatar\//);
  assert.match(wiki, /WZ \+ MySQL/);
  assert.match(account, /\/account\/password/);
  assert.match(account, /\/account\/discord\/connect/);
});

test('redesign does not import reference-site assets, fonts, or remote styles', () => {
  for (const sheet of [css, unified]) {
    assert.doesNotMatch(sheet, /https?:\/\//i);
    assert.doesNotMatch(sheet, /@import/i);
    assert.doesNotMatch(sheet, /refero\.design|styles\.refero/i);
  }
  assert.match(css, /--terminal-bg:#12130f/);
  assert.match(unified, /--ut-bg:#12130f/);
});
