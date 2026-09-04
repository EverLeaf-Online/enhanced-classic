const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.join(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');

test('public route templates carry production-verifiable markers',()=>{
  const rankings=read('src/views/rankings.ejs');
  const wiki=read('src/views/wiki.ejs');
  const wikiRoute=read('src/routes/wiki.js');
  assert.match(rankings,/\/character-avatar\/\$\{Number\(r\.id\)\}\.png/);
  assert.match(rankings,/Live saved appearance/);
  assert.match(wiki,/EVERLEAF DATA WIKI/);
  assert.match(wiki,/WZ \+ MySQL/);
  assert.match(wiki,/BROWSE CATALOG/);
  assert.match(wikiRoute,/services\/wikiPublicCatalog/);
  assert.match(wikiRoute,/\/wiki\/guides/);
});
