const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const header = read('src/views/partials/header.ejs');
const design = read('DESIGN.md');
const css = read('public/css/refero-everleaf-2026.css');
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
  assert.match(design, /proprietary reference fonts/);
});

test('Refero-informed stylesheet is loaded last with server-rendered route classes', () => {
  const oldPortal = header.indexOf('/css/full-site-portal-2026.css?v=1');
  const refero = header.indexOf('/css/refero-everleaf-2026.css?v=2');
  assert.ok(oldPortal >= 0, 'existing functional portal layer should remain available');
  assert.ok(refero > oldPortal, 'terminal Refero layer must load after the existing portal layer');
  assert.match(header, /const routeKey=/);
  assert.match(header, /route-<%=routeKey%>/);
  assert.match(header, /route-admin/);
  assert.match(header, /theme-color" content="#12130f"/);
  assert.match(header, /color-scheme" content="dark"/);
});

test('new system deliberately covers the homepage and all major shared surfaces', () => {
  for (const selector of [
    '.terminalHero',
    '.terminalNav',
    '.signalStrip',
    '.dossierSection',
    '.entrySection',
    '.classMatrix',
    '.dataSection',
    '.wikiSignalSection',
    '.lightPage',
    '.authWrap',
    '.rankingTable',
    '.wikiSearch',
    '.terminalFooter'
  ]) assert.ok(css.includes(selector), `missing terminal redesign coverage for ${selector}`);

  for(const token of ['terminalHero','everleafArtifact','heroTelemetry','classMatrix','dataSplit','finalTransmission']) {
    assert.ok(home.includes(token), `homepage should include ${token}`);
  }
  assert.match(css, /@media \(max-width:960px\)/);
  assert.match(css, /@media \(max-width:640px\)/);
  assert.match(css, /prefers-reduced-motion/);
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
  assert.doesNotMatch(css, /https?:\/\//i);
  assert.doesNotMatch(css, /@import/i);
  assert.doesNotMatch(css, /refero\.design|styles\.refero/i);
  assert.doesNotMatch(css, /Recoleta|Suisse|Jersey 10|Manrope/i);
  assert.match(css, /--terminal-bg:#12130f/);
  assert.match(css, /--terminal-text:#e4dfda/);
  assert.match(css, /--terminal-line:#3c3c38/);
  assert.match(css, /--terminal-glow:#f5c2c8/);
});
