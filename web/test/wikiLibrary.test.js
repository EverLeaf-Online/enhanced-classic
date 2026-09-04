const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {categories,entries,bySlug,searchEntries}=require('../src/services/wikiCatalog');
const root=path.join(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');

test('wiki seed catalog remains available as supplemental EverLeaf guides',()=>{
  assert.ok(categories.length>=7);
  assert.ok(entries.length>=19);
  for(const slug of ['enhanced-classic','getting-started','adventurer-jobs','cygnus-knights','aran-guide','evan-guide','level-250-progression','hp-washing-replacement','nx-reward-sources','voting-guide','pet-vac','trade-button-free-market','everleaf-launcher','launcher-repair-updates','widescreen-support','rankings-guide','rooted-content','wiki-how-to-use']) {
    assert.ok(bySlug.has(slug),`${slug} should exist`);
  }
  assert.ok(searchEntries('pet vac').some(x=>x.slug==='pet-vac'));
  assert.ok(searchEntries('repair').some(x=>x.slug==='launcher-repair-updates'));
  assert.ok(entries.every(x=>x.sourceDoc&&x.verification),'every seed entry should carry source and verification metadata');
});

test('CMS schema still owns persistent supplemental guide storage',()=>{
  const cms=read('src/db/cms.js');
  assert.match(cms,/CREATE TABLE IF NOT EXISTS wiki_articles/);
  assert.match(cms,/INSERT OR IGNORE INTO wiki_articles/);
  assert.match(cms,/WIKI_SEED_VERSION = 2/);
  assert.match(cms,/updated_at=created_at/);
  assert.match(cms,/services\/wikiCatalog/);
});

test('Wiki service still provides guide search, parsing, and publishing',()=>{
  const service=read('src/services/wikiService.js');
  assert.match(service,/SELECT \* FROM wiki_articles WHERE published=1/);
  assert.match(service,/function searchEntries/);
  assert.match(service,/function parseBody/);
  assert.match(service,/function saveArticle/);
});

test('wiki routes prioritize live game-data pages and namespace staff guides',()=>{
  const route=read('src/routes/wiki.js');
  assert.match(route,/services\/wikiDataService/);
  assert.match(route,/data\.ensureCatalog/);
  assert.match(route,/data\.search/);
  assert.match(route,/data\.list/);
  assert.match(route,/data\.detail/);
  assert.match(route,/router\.get\("\/wiki"/);
  assert.match(route,/router\.get\("\/wiki\/guides"/);
  assert.match(route,/router\.get\("\/wiki\/guides\/:slug"/);
  assert.match(route,/router\.get\("\/wiki\/:type"/);
  assert.match(route,/router\.get\("\/wiki\/:type\/:id"/);
});

test('Wiki UI is explicitly a searchable server-data encyclopedia',()=>{
  const hub=read('src/views/wiki.ejs');
  const list=read('src/views/wiki-data-list.ejs');
  const entry=read('src/views/wiki-data-entry.ejs');
  const css=read('public/css/wiki-data-2026.css');
  const header=read('src/views/partials/header.ejs');
  assert.match(hub,/EVERLEAF DATA WIKI/);
  assert.match(hub,/WZ \+ MySQL/);
  assert.match(hub,/BROWSE CATALOG/);
  assert.match(hub,/wikiDataSearch/);
  assert.match(hub,/\/wiki\/guides/);
  assert.match(list,/wikiDataList/);
  assert.match(entry,/wikiEntityPage/);
  assert.match(css,/\.wikiCatalogGrid/);
  assert.match(css,/\.wikiDataTable/);
  assert.match(header,/wiki-data-2026\.css/);
});

test('CMS knowledge dashboard continues to support supplemental Wiki guides',()=>{
  const route=read('src/routes/admin-knowledge.js');
  const view=read('src/views/admin-knowledge.ejs');
  const editor=read('src/views/admin-knowledge-edit.ejs');
  assert.match(route,/\/knowledge\/new/);
  assert.match(route,/\/knowledge\/:id\/edit/);
  assert.match(route,/\/knowledge\/save/);
  assert.match(route,/wiki\.saveArticle/);
  assert.match(view,/NEW ARTICLE/);
  assert.match(editor,/Article body/);
  assert.match(editor,/name="published"/);
});
