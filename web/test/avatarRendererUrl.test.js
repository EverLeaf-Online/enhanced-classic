const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.join(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');

test('character avatar proxy composes saved appearance from local v83 WZ first',()=>{
  const avatar=read('src/routes/avatar.js');
  const env=read('src/config/env.js');
  assert.match(avatar,/localRendererIds/);
  assert.match(avatar,/2000 \+ skin/);
  assert.match(avatar,/12000 \+ skin/);
  assert.match(avatar,/appearance\.hair/);
  assert.match(avatar,/appearance\.face/);
  assert.match(avatar,/appearance\.equipment/);
  assert.match(avatar,/\/api\/character\/compose/);
  assert.match(avatar,/pose: "stand1"/);
  assert.match(avatar,/scale: "2"/);
  assert.match(avatar,/env\.avatar\.localBaseUrl/);
  assert.match(avatar,/"local-wz"/);
  assert.match(env,/CHARACTER_WZ_RENDERER_URL/);
  assert.match(env,/http:\/\/127\.0\.0\.1:3011/);
  assert.match(avatar,/Content-Type/);
  assert.match(avatar,/X-EverLeaf-Avatar-Source/);
  assert.match(avatar,/stale-while-revalidate/);
});

test('external character renderer is optional rather than the production default',()=>{
  const avatar=read('src/routes/avatar.js');
  const env=read('src/config/env.js');
  assert.match(env,/remoteBaseUrl: String\(process\.env\.MAPLESTORY_IO_BASE_URL \|\| ""\)/);
  assert.match(avatar,/if \(env\.avatar\.remoteBaseUrl\)/);
  assert.match(avatar,/external-renderer/);
});
