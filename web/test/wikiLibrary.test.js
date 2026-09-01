const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {categories,entries,bySlug,searchEntries}=require('../src/services/wikiCatalog');
const root=path.join(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');

test('wiki catalog exposes curated EverLeaf knowledge',()=>{
  assert.ok(categories.length>=6);
  assert.ok(entries.length>=10);
  for(const slug of ['enhanced-classic','level-250-progression','hp-washing-replacement','nx-reward-sources','everleaf-launcher','adventurer-jobs']) assert.ok(bySlug.has(slug));
  assert.ok(searchEntries('pet vac').some(x=>x.slug==='pet-vac'));
  assert.ok(searchEntries('', 'progression').every(x=>x.category==='progression'));
});

test('wiki catalog lives outside deploy-excluded data directories',()=>{
  assert.ok(fs.existsSync(path.join(root,'src/services/wikiCatalog.js')));
  assert.equal(fs.existsSync(path.join(root,'src/data/wikiCatalog.js')),false);
  const route=read('src/routes/wiki.js');
  assert.match(route,/\.\.\/services\/wikiCatalog/);
  assert.doesNotMatch(route,/\.\.\/data\/wikiCatalog/);
});

test('wiki routes support search and article detail pages',()=>{
  const route=read('src/routes/wiki.js');
  assert.match(route,/searchEntries/);
  assert.match(route,/router\.get\("\/wiki"/);
  assert.match(route,/router\.get\("\/wiki\/:slug"/);
  assert.match(route,/wiki-entry/);
});

test('wiki UI ships searchable database and source labels',()=>{
  const hub=read('src/views/wiki.ejs');
  const entry=read('src/views/wiki-entry.ejs');
  const css=read('public/css/wiki-remaster.css');
  const header=read('src/views/partials/header.ejs');
  assert.match(hub,/wikiSearch/);
  assert.match(hub,/Browse database/);
  assert.match(hub,/entry\.source/);
  assert.match(entry,/wikiFacts/);
  assert.match(entry,/Curated into the website from EverLeaf's durable research library/);
  assert.match(css,/\.wikiArticleGrid/);
  assert.match(css,/\.wikiEntryLayout/);
  assert.match(header,/wiki-remaster\.css/);
});
