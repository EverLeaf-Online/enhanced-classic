const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const workflow=fs.readFileSync(path.join(__dirname,'../../.github/workflows/verify-web-data-wiki.yml'),'utf8');

test('production verification requires a non-empty live data Wiki',()=>{
  assert.match(workflow,/workflow_run/);
  assert.match(workflow,/Deploy EverLeaf Web/);
  assert.match(workflow,/EVERLEAF DATA WIKI/);
  assert.match(workflow,/WZ \+ MySQL/);
  assert.match(workflow,/Server data unavailable/);
  assert.match(workflow,/\/wiki\/items/);
  assert.match(workflow,/\/wiki\/monsters/);
  assert.match(workflow,/indexed records/);
});
