const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.join(__dirname,'..');
const repo=path.join(root,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const readRepo=p=>fs.readFileSync(path.join(repo,p),'utf8');

test('local avatar sidecar is pinned, loopback-only, and reads production Character.wz',()=>{
  const unit=read('ops/everleaf-wz-avatar.service');
  const runner=read('ops/run-wz-avatar-renderer.py');
  const installer=read('scripts/install-wz-avatar-renderer.sh');
  assert.match(unit,/Description=EverLeaf local v83 WZ character renderer/);
  assert.match(unit,/run-wz-avatar-renderer\.py/);
  assert.match(unit,/NoNewPrivileges=true/);
  assert.match(unit,/ReadOnlyPaths=\/opt\/everleaf\/patches\/files\/Character\.wz/);
  assert.match(runner,/\/opt\/everleaf\/patches\/files\/Character\.wz/);
  assert.match(runner,/region="GMS"/);
  assert.match(runner,/version=83/);
  assert.match(runner,/127\.0\.0\.1/);
  assert.match(runner,/3011/);
  assert.match(runner,/threaded=False/);
  assert.match(installer,/013b47b7ee2903e45d178d3ec6dd320f10e8b713/);
  assert.match(installer,/Leonana69\/wz-python/);
  assert.match(installer,/api\/character\/compose/);
  assert.match(installer,/00002000/);
  assert.match(installer,/00012000/);
  assert.match(installer,/PNG/);
});

test('production web deployment installs and proves the local WZ renderer',()=>{
  const deploy=readRepo('.github/workflows/deploy-web.yml');
  assert.match(deploy,/python3-venv git/);
  assert.match(deploy,/install-wz-avatar-renderer\.sh/);
  assert.match(deploy,/CHARACTER_WZ_RENDERER_URL/);
  assert.match(deploy,/MAPLESTORY_IO_BASE_URL ""/);
  assert.match(deploy,/systemctl is-active --quiet everleaf-wz-avatar/);
  assert.match(deploy,/x-everleaf-avatar-source:/i);
  assert.match(deploy,/local-wz\(-cache\)/);
  assert.match(deploy,/d\[:8\]==b"\\x89PNG\\r\\n\\x1a\\n"/);
});
