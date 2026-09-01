const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const root=path.join(__dirname,'..');
const read=file=>fs.readFileSync(path.join(root,file),'utf8');
const publicRoute=read('src/routes/public.js');
const home=read('src/views/home.ejs');
const css=read('public/css/home-polish.css');
const {bySlug}=require('../src/services/wikiCatalog');

test('homepage handbook is driven by curated wiki entries',()=>{
  assert.match(publicRoute,/entries:wikiEntries, bySlug:wikiBySlug/);
  assert.match(publicRoute,/featuredWikiSlugs/);
  for(const slug of ['enhanced-classic','launcher-repair-updates','nx-reward-sources']){
    assert.ok(bySlug.has(slug),`${slug} should exist in the Wiki catalog`);
    assert.match(publicRoute,new RegExp(slug));
  }
  assert.match(publicRoute,/featuredWiki,settings:settings\(\)/);
  assert.match(home,/\(featuredWiki\|\|\[\]\)\.forEach/);
  assert.match(home,/href="\/wiki\/<%=entry\.slug%>"/);
  assert.match(home,/entry\.summary/);
  assert.match(home,/entry\.status/);
  assert.match(home,/entry\.sourceDoc/);
  assert.match(css,/\.libraryFeatureCard/);
  assert.match(css,/\.libraryFeatureStatus/);
});

test('sitemap exposes the Wiki hub and every structured article',()=>{
  assert.match(publicRoute,/staticPaths=\["\/","\/news","\/downloads","\/rankings","\/wiki"/);
  assert.match(publicRoute,/wikiEntries\.map\(entry=>\(\{loc:`\$\{siteUrl\}\/wiki\/\$\{encodeURIComponent\(entry\.slug\)\}`/);
});
