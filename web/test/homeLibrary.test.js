const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const root=path.join(__dirname,'..');
const read=file=>fs.readFileSync(path.join(root,file),'utf8');
const publicRoute=read('src/routes/public.js');
const home=read('src/views/home.ejs');
const {bySlug}=require('../src/services/wikiCatalog');

test('homepage no longer renders the handbook promo section',()=>{
  for(const slug of ['enhanced-classic','launcher-repair-updates','nx-reward-sources']){
    assert.ok(bySlug.has(slug),`${slug} should remain available in the Wiki catalog`);
  }
  assert.doesNotMatch(home,/featuredWiki|wikiSignalSection|KNOW THE WORLD/i);
  assert.match(home,/href="\/wiki"/);
});

test('sitemap still exposes the Wiki hub and every published CMS article',()=>{
  assert.match(publicRoute,/staticPaths=\["\/","\/news","\/downloads","\/rankings","\/wiki"/);
  assert.match(publicRoute,/const wikiEntries=wiki\.listPublished\(\)/);
  assert.match(publicRoute,/wikiEntries\.map\(entry=>\(\{loc:`\$\{siteUrl\}\/wiki\/\$\{encodeURIComponent\(entry\.slug\)\}`/);
});
