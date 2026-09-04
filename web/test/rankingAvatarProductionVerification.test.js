const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const workflow=fs.readFileSync(path.join(__dirname,'../../.github/workflows/verify-web-ranking-avatars.yml'),'utf8');
const deploy=fs.readFileSync(path.join(__dirname,'../../.github/workflows/deploy-web.yml'),'utf8');
const grants=fs.readFileSync(path.join(__dirname,'../sql/recommended_web_user.sql'),'utf8');

test('production verification requires a full equipped local Character.wz ranking avatar',()=>{
  assert.match(workflow,/workflow_run/);
  assert.match(workflow,/Deploy EverLeaf Web/);
  assert.match(workflow,/\/rankings/);
  assert.match(workflow,/data-live-avatar/);
  assert.match(workflow,/character-avatar/);
  assert.match(workflow,/content-type:/i);
  assert.match(workflow,/image\//);
  assert.match(workflow,/x-everleaf-avatar-source:/i);
  assert.match(workflow,/local-wz\(-cache\)/);
  assert.match(workflow,/x-everleaf-avatar-mode:/i);
  assert.match(workflow,/full/);
  assert.match(workflow,/x-everleaf-avatar-equipment-count:/i);
  assert.match(workflow,/\[1-9\]\[0-9\]\*/);
  assert.match(workflow,/PNG/);
  assert.match(workflow,/onerror=/);
});

test('production deployment grants only the equipment read access rankings require',()=>{
  assert.match(grants,/GRANT SELECT ON cosmic\.inventoryitems TO 'everleaf_web'@'127\.0\.0\.1'/);
  assert.match(deploy,/mysql\.user WHERE User='everleaf_web'/);
  assert.match(deploy,/GRANT SELECT ON .*inventoryitems.*TO/);
  assert.match(deploy,/WEB_DB_ACCOUNT_COUNT/);
  assert.match(deploy,/x-everleaf-avatar-equipment-count:/i);
  assert.match(deploy,/\[1-9\]\[0-9\]\*/);
  assert.doesNotMatch(grants,/GRANT (?:ALL|INSERT|UPDATE|DELETE) ON cosmic\.inventoryitems/i);
});
