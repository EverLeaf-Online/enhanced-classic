const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.join(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');

test('character avatar proxy targets the versioned centered renderer',()=>{
  const avatar=read('src/routes/avatar.js');
  assert.match(avatar,/\/api\/\$\{encodeURIComponent\(env\.avatar\.region\)\}\/\$\{encodeURIComponent\(env\.avatar\.version\)\}\/Character\/center/);
  assert.match(avatar,/2000 \+ Math\.max\(0, Number\(appearance\.skincolor/);
  assert.match(avatar,/stand1\/0\?resize=2&padding=6/);
  assert.match(avatar,/Content-Type/);
  assert.match(avatar,/stale-while-revalidate/);
});
