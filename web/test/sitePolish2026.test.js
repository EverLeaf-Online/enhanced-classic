const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const root=path.join(__dirname,'..');
const read=file=>fs.readFileSync(path.join(root,file),'utf8');

test('shared shell loads accessibility metadata and the unified terminal layer',()=>{
  const header=read('src/views/partials/header.ejs');
  assert.match(header,/site-polish-2026\.css/);
  assert.match(header,/\/js\/site\.js\?v=2/);
  assert.match(header,/aria-current="page"/);
  assert.match(header,/aria-controls="mobile-navigation"/);
  assert.match(header,/meta name="robots"/);
  assert.match(header,/rel="preload" as="image" href="\/assets\/hero-forest\.webp"/);
  assert.match(header,/refero-everleaf-2026\.css\?v=3/);
  assert.match(header,/unified-terminal-2026\.css\?v=1/);
});

test('homepage exposes onboarding and live status without removed promo blocks',()=>{
  const home=read('src/views/home.ejs');
  const statusJs=read('public/js/home-status.js');
  assert.match(home,/id="server-status"/);
  assert.match(home,/id="live-refresh"/);
  assert.match(home,/class="entrySequence"/);
  assert.match(home,/class="dossierMetrics"/);
  assert.match(home,/class="signalStrip"/);
  assert.doesNotMatch(home,/classMatrix|wikiSignalSection|CHOOSE YOUR SIGNAL|KNOW THE WORLD/i);
  assert.match(statusJs,/cache: 'no-store'/);
  assert.match(statusJs,/visibilitychange/);
  assert.match(statusJs,/refreshes every 30 seconds/);
});

test('global polish keeps responsive behavior and does not re-inject old shells',()=>{
  const css=read('public/css/unified-terminal-2026.css');
  const siteJs=read('public/js/site.js');
  assert.match(css,/@media\(max-width:960px\)/);
  assert.match(css,/@media\(max-width:640px\)/);
  assert.match(css,/legacy scallop\/ribbon\/cloud decoration/i);
  assert.doesNotMatch(siteJs,/full-site-portal-2026\.css/);
  assert.match(siteJs,/Escape/);
  assert.match(siteJs,/aria-expanded/);
});
