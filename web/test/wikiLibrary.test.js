const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {categories,entries,bySlug,searchEntries,sourceCoverage}=require('../src/services/wikiCatalog');
const root=path.join(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');

test('wiki seed catalog preserves expanded EverLeaf knowledge',()=>{
  assert.ok(categories.length>=7);
  assert.ok(entries.length>=19);
  for(const slug of ['enhanced-classic','server-authority','level-250-progression','hp-washing-replacement','nx-reward-sources','everleaf-launcher','launcher-repair-updates','launcher-first-play','widescreen-support','npc-map-integrity','custom-nx-pipeline','custom-item-id-discipline','adventurer-jobs']) assert.ok(bySlug.has(slug),`${slug} should exist`);
  assert.ok(searchEntries('pet vac').some(x=>x.slug==='pet-vac'));
  assert.ok(searchEntries('manifest').some(x=>x.slug==='launcher-repair-updates'));
  assert.ok(searchEntries('NPC').some(x=>x.slug==='npc-map-integrity'));
  assert.ok(entries.every(x=>x.sourceDoc&&x.verification),'every seed entry should carry source and verification metadata');
  assert.ok(sourceCoverage().some(x=>x.doc==='SERVER-SYSTEMS.md'&&x.count>=1));
});

test('CMS schema owns persistent Wiki article storage and seed import',()=>{
  const cms=read('src/db/cms.js');
  assert.match(cms,/CREATE TABLE IF NOT EXISTS wiki_articles/);
  assert.match(cms,/INSERT OR IGNORE INTO wiki_articles/);
  assert.match(cms,/services\/wikiCatalog/);
  assert.match(cms,/updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP/);
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

test('Wiki UI exposes searchable CMS database, contents navigation, and provenance',()=>{
  const hub=read('src/views/wiki.ejs');
  const entry=read('src/views/wiki-entry.ejs');
  const css=read('public/css/wiki-cms.css');
  const header=read('src/views/partials/header.ejs');
  assert.match(hub,/wikiSearch/);
  assert.match(hub,/CMS-backed/);
  assert.match(hub,/entry\.updatedAt/);
  assert.match(entry,/wikiToc/);
  assert.match(entry,/wikiProvenance/);
  assert.match(entry,/entry\.sourceDoc/);
  assert.match(entry,/entry\.verification/);
  assert.match(css,/\.wikiBreadcrumb/);
  assert.match(css,/\.wikiToc/);
  assert.match(header,/wiki-cms\.css/);
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
