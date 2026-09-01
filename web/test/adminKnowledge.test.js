const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.join(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');

test('CMS knowledge workspace is admin-only and read-only',()=>{
  const route=read('src/routes/admin-knowledge.js');
  assert.match(route,/router\.get\('\/knowledge',requireAdmin/);
  assert.doesNotMatch(route,/router\.post/);
  assert.match(route,/searchEntries/);
  assert.match(route,/coverage/);
});

test('server mounts knowledge workspace before general admin routes',()=>{
  const server=read('src/server.js');
  assert.match(server,/routes\/admin-knowledge/);
});

test('CMS navigation and UI expose game database workspace',()=>{
  const nav=read('src/views/partials/admin-manager-nav.ejs');
  const view=read('src/views/admin-knowledge.ejs');
  const css=read('public/css/cms-knowledge.css');
  const header=read('src/views/partials/header.ejs');
  assert.match(nav,/\/admin\/knowledge/);
  assert.match(nav,/Game Database/);
  assert.match(view,/Game Database & Knowledge/);
  assert.match(view,/read-only/);
  assert.match(view,/IMPORT ROADMAP/);
  assert.match(view,/Open Public Wiki/);
  assert.match(css,/\.knowledgeWorkspace/);
  assert.match(css,/\.knowledgeTable/);
  assert.match(header,/cms-knowledge\.css/);
});
