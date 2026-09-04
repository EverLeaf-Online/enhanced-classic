const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.join(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');

test('character avatar proxy targets the v83-first centered renderer',()=>{
  const avatar=read('src/routes/avatar.js');
  assert.match(avatar,/\/api\/\$\{encodeURIComponent\(env\.avatar\.region\)\}\/\$\{encodeURIComponent\(version\)\}\/Character\/center/);
  assert.match(avatar,/rendererVersions/);
  assert.match(avatar,/\["83", String\(env\.avatar\.version/);
  assert.match(avatar,/2000 \+ Math\.max\(0, Number\(appearance\.skincolor/);
  assert.match(avatar,/stand1\/0\?resize=2&padding=6/);
  assert.match(avatar,/Content-Type/);
  assert.match(avatar,/X-EverLeaf-Avatar-Source/);
  assert.match(avatar,/stale-while-revalidate/);
});
