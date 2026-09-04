const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const header = read('src/views/partials/header.ejs');
const footer = read('src/views/partials/footer.ejs');
const design = read('DESIGN.md');
const css = read('public/css/terminal-everleaf-2026.css');
const home = read('src/views/home.ejs');
const rankings = read('src/views/rankings.ejs');
const wiki = read('src/views/wiki.ejs');
const account = read('src/views/account.ejs');
const admin = read('src/views/admin.ejs');
const adminNews = read('src/views/admin-news.ejs');
const adminKnowledge = read('src/views/admin-knowledge.ejs');

test('EverLeaf design contract now defines the full-bleed world terminal', () => {
  assert.match(design, /dark, full-bleed, edge-anchored operating-system aesthetic/i);
  assert.match(design, /--terminal-bg: #12130f/);
  assert.match(design, /--terminal-ink: #e4dfda/);
  assert.match(design, /The CMS must be redesigned as an operations terminal/);
  assert.match(design, /Do not/);
  assert.match(design, /restructure markup/i);
  assert.match(design, /proprietary fonts/i);
});

test('terminal stylesheet is the final visual layer and the shell is structurally replaced', () => {
  const oldRefero = header.indexOf('/css/refero-everleaf-2026.css?v=1');
  const terminal = header.indexOf('/css/terminal-everleaf-2026.css?v=1');
  assert.ok(oldRefero >= 0, 'legacy compatibility layer remains beneath the new system');
  assert.ok(terminal > oldRefero, 'terminal system must load last');
  assert.match(header, /terminalMode/);
  assert.match(header, /terminalHeader/);
  assert.match(header, /terminalNav/);
  assert.match(header, /theme-color" content="#12130f"/);
  assert.match(footer, /terminalFooter/);
});

test('the homepage is a new terminal composition rather than the old card portal', () => {
  for (const marker of ['terminalHero','terminalHeroArtifact','terminalWorldReadout','terminalSection','terminalJobGrid','terminalRankingPreview']) {
    assert.match(home, new RegExp(marker));
  }
  assert.match(home, /MAPLE\s*<br>WORLD\s*<br>RUNNING/);
  assert.match(home, /\/assets\/hero-left\.webp/);
  assert.match(home, /\/assets\/hero-right\.webp/);
  assert.match(home, /data-live-avatar/);
});

test('terminal system covers public product surfaces and CMS operations', () => {
  for (const selector of [
    '.terminalHero', '.terminalLogPage', '.terminalDeployPage', '.terminalHelpPage',
    '.terminalAuthPage', '.terminalAccountPage', 'body.terminalMode .rankingPodium',
    'body.terminalMode .wikiDataHero', 'body.terminalMode .adminShell',
    'body.terminalMode .cmsManagerNav', 'body.terminalMode .cmsWorkspace'
  ]) assert.ok(css.includes(selector), `missing terminal coverage for ${selector}`);
  assert.match(css, /@media\(max-width:720px\)/);
  assert.match(css, /@media\(prefers-reduced-motion:reduce\)/);
});

test('redesign preserves live game and account integrations', () => {
  assert.match(rankings, /data-live-avatar/);
  assert.match(rankings, /\/character-avatar\//);
  assert.match(wiki, /WZ \+ MySQL/);
  assert.match(account, /\/account\/password/);
  assert.match(account, /\/account\/discord\/connect/);
});

test('CMS is restructured, not just recolored', () => {
  assert.match(admin, /STAFF:\/\/CMS/);
  assert.match(admin, /adminShell/);
  assert.match(admin, /SERVER HEALTH/);
  assert.match(adminNews, /cmsWorkspace/);
  assert.match(adminNews, /ENTRY QUEUE/);
  assert.match(adminKnowledge, /ARTICLE LEDGER/);
  assert.match(adminKnowledge, /knowledgeTable/);
});

test('terminal design does not import reference assets or remote styles', () => {
  assert.doesNotMatch(css, /https?:\/\//i);
  assert.doesNotMatch(css, /@import/i);
  assert.doesNotMatch(css, /refero\.design|styles\.refero/i);
  assert.doesNotMatch(css, /Max Yinger/i);
  assert.match(css, /--terminal-bg:#12130f/);
  assert.match(css, /--terminal-ink:#e4dfda/);
});
