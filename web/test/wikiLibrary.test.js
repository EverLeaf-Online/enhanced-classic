const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {categories,entries,bySlug,searchEntries,sourceCoverage}=require('../src/services/wikiCatalog');
const root=path.join(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');

test('wiki catalog exposes expanded curated EverLeaf knowledge',()=>{
  assert.ok(categories.length>=7);
  assert.ok(entries.length>=19);
  for(const slug of ['enhanced-classic','server-authority','level-250-progression','hp-washing-replacement','nx-reward-sources','everleaf-launcher','launcher-repair-updates','launcher-first-play','widescreen-support','npc-map-integrity','custom-nx-pipeline','custom-item-id-discipline','adventurer-jobs']) assert.ok(bySlug.has(slug),`${slug} should exist`);
  assert.ok(searchEntries('pet vac').some(x=>x.slug==='pet-vac'));
  assert.ok(searchEntries('manifest').some(x=>x.slug==='launcher-repair-updates'));
  assert.ok(searchEntries('NPC').some(x=>x.slug==='npc-map-integrity'));
  assert.ok(searchEntries('', 'progression').every(x=>x.category==='progression'));
  assert.ok(entries.every(x=>x.sourceDoc&&x.verification),'every public entry should carry source and verification metadata');
  assert.ok(sourceCoverage().some(x=>x.doc==='SERVER-SYSTEMS.md'&&x.count>=1));
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

test('wiki UI ships searchable database with provenance labels',()=>{
  const hub=read('src/views/wiki.ejs');
  const entry=read('src/views/wiki-entry.ejs');
  const css=read('public/css/wiki-remaster.css');
  const v2=read('public/css/wiki-library-v2.css');
  const header=read('src/views/partials/header.ejs');
  assert.match(hub,/wikiSearch/);
  assert.match(hub,/Browse database/);
  assert.match(hub,/entry\.source/);
  assert.match(entry,/wikiFacts/);
  assert.match(entry,/wikiProvenance/);
  assert.match(entry,/entry\.sourceDoc/);
  assert.match(entry,/entry\.verification/);
  assert.match(css,/\.wikiArticleGrid/);
  assert.match(css,/\.wikiEntryLayout/);
  assert.match(v2,/\.wikiVerified/);
  assert.match(v2,/\.wikiProvenance/);
  assert.match(header,/wiki-remaster\.css/);
  assert.match(header,/wiki-library-v2\.css/);
});

test('CMS knowledge dashboard exposes source and verification coverage',()=>{
  const route=read('src/routes/admin-knowledge.js');
  const view=read('src/views/admin-knowledge.ejs');
  const css=read('public/css/cms-knowledge.css');
  assert.match(route,/sourceCoverage/);
  assert.match(route,/verifiedCount/);
  assert.match(view,/knowledgeSummary/);
  assert.match(view,/SOURCE COVERAGE/);
  assert.match(view,/entry\.sourceDoc/);
  assert.match(view,/entry\.verification/);
  assert.match(css,/\.knowledgeSummary/);
  assert.match(css,/\.knowledgeSourceCoverage/);
});
