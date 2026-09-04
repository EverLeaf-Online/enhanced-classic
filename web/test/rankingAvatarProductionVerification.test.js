const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const workflow=fs.readFileSync(path.join(__dirname,'../../.github/workflows/verify-web-ranking-avatars.yml'),'utf8');

test('production verification requires a deliverable ranking avatar',()=>{
  assert.match(workflow,/workflow_run/);
  assert.match(workflow,/Deploy EverLeaf Web/);
  assert.match(workflow,/\/rankings/);
  assert.match(workflow,/data-live-avatar/);
  assert.match(workflow,/character-avatar/);
  assert.match(workflow,/content-type:/i);
  assert.match(workflow,/image\//);
  assert.match(workflow,/onerror=/);
});
