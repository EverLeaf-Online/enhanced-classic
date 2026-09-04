const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {categories,entries,bySlug,searchEntries}=require('../src/services/wikiCatalog');
const root=path.join(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');

test('wiki seed catalog is player-facing EverLeaf knowledge',()=>{
  assert.ok(categories.length>=7);
  assert.ok(entries.length>=19);
  for(const slug of ['enhanced-classic','getting-started','adventurer-jobs','cygnus-knights','aran-guide','evan-guide','level-250-progression','hp-washing-replacement','nx-reward-sources','voting-guide','pet-vac','trade-button-free-market','everleaf-launcher','launcher-repair-updates','widescreen-support','rankings-guide','rooted-content','wiki-how-to-use']) {
    assert.ok(bySlug.has(slug),`${slug} should exist`);
  }
  for(const retired of ['server-authority','reward-delivery-safety','custom-ui-layer','npc-map-integrity','custom-nx-pipeline','custom-item-id-discipline']) {
    assert.equal(bySlug.has(retired),false,`${retired} should no longer be a public seed guide`);
  }
  assert.ok(searchEntries('pet vac').some(x=>x.slug==='pet-vac'));
  assert.ok(searchEntries('repair').some(x=>x.slug==='launcher-repair-updates'));
  assert.ok(searchEntries('new player').some(x=>x.slug==='getting-started'));
  assert.ok(entries.every(x=>x.sourceDoc&&x.verification),'every seed entry should carry source and verification metadata');
});

test('CMS schema owns persistent Wiki storage and safely refreshes untouched seeds',()=>{
  const cms=read('src/db/cms.js');
  assert.match(cms,/CREATE TABLE IF NOT EXISTS wiki_articles/);
  assert.match(cms,/INSERT OR IGNORE INTO wiki_articles/);
  assert.match(cms,/WIKI_SEED_VERSION = 2/);
  assert.match(cms,/wiki_player_seed_version/);
  assert.match(cms,/updated_at=created_at/);
  assert.match(cms,/RETIRED_DEVELOPER_SLUGS/);
  assert.match(cms,/services\/wikiCatalog/);
});

test('Wiki service provides database search, article parsing, and publishing',()=>{
  const service=read('src/services/wikiService.js');
  assert.match(service,/SELECT \* FROM wiki_articles WHERE published=1/);
  assert.match(service,/function searchEntries/);
  assert.match(service,/function parseBody/);
  assert.match(service,/function saveArticle/);
  assert.match(service,/updated_at=CURRENT_TIMESTAMP/);
});

test('wiki routes serve CMS articles, search, and article detail pages',()=>{
  const route=read('src/routes/wiki.js');
  assert.match(route,/services\/wikiService/);
  assert.match(route,/wiki\.listPublished/);
  assert.match(route,/wiki\.searchEntries/);
  assert.match(route,/wiki\.getBySlug/);
  assert.match(route,/router\.get\("\/wiki"/);
  assert.match(route,/router\.get\("\/wiki\/:slug"/);
});

test('Wiki UI is explicitly a searchable player guide',()=>{
  const hub=read('src/views/wiki.ejs');
  const entry=read('src/views/wiki-entry.ejs');
  const css=read('public/css/wiki-cms.css');
  const playerCss=read('public/css/wiki-player-2026.css');
  const header=read('src/views/partials/header.ejs');
  assert.match(hub,/EVERLEAF PLAYER WIKI/);
  assert.match(hub,/wikiSearch/);
  assert.match(hub,/QUICK START/);
  assert.match(hub,/getting-started/);
  assert.match(hub,/Staff maintained/);
  assert.match(hub,/Staff-maintained EverLeaf guide/);
  assert.doesNotMatch(hub,/entry\.sourceDoc\|\|entry\.source/);
  assert.match(entry,/wikiToc/);
  assert.match(entry,/wikiProvenance/);
  assert.match(css,/\.wikiBreadcrumb/);
  assert.match(playerCss,/\.wikiQuickGrid/);
  assert.match(header,/wiki-player-2026\.css/);
});

test('CMS knowledge dashboard supports creating and editing Wiki articles',()=>{
  const route=read('src/routes/admin-knowledge.js');
  const view=read('src/views/admin-knowledge.ejs');
  const editor=read('src/views/admin-knowledge-edit.ejs');
  assert.match(route,/\/knowledge\/new/);
  assert.match(route,/\/knowledge\/:id\/edit/);
  assert.match(route,/\/knowledge\/save/);
  assert.match(route,/wiki\.saveArticle/);
  assert.match(view,/NEW ARTICLE/);
  assert.match(view,/Published/);
  assert.match(editor,/Article body/);
  assert.match(editor,/## Heading/);
  assert.match(editor,/name="published"/);
});
