const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.join(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');

test('CMS knowledge workspace is admin-only and supports audited Wiki editing',()=>{
  const route=read('src/routes/admin-knowledge.js');
  assert.match(route,/router\.get\('\/knowledge',requireAdmin/);
  assert.match(route,/router\.get\('\/knowledge\/new',requireAdmin/);
  assert.match(route,/router\.get\('\/knowledge\/:id\/edit',requireAdmin/);
  assert.match(route,/router\.post\('\/knowledge\/save',requireAdmin/);
  assert.match(route,/router\.get\('\/knowledge\/catalog',requireAdmin/);
  assert.match(route,/router\.post\('\/knowledge\/catalog\/:type\/:id\/visibility',requireAdmin/);
  assert.match(route,/wiki\.searchEntries/);
  assert.match(route,/visibility\.catalogList/);
  assert.match(route,/visibility\.setOverride/);
  assert.match(route,/visibility\.clearOverride/);
  assert.match(route,/wiki\.saveArticle/);
  assert.match(route,/audit_log/);
  assert.match(route,/coverage/);
});

test('server mounts knowledge workspace before general admin routes',()=>{
  const server=read('src/server.js');
  assert.match(server,/routes\/admin-knowledge/);
});

test('CMS navigation and UI expose editable game database workspace',()=>{
  const nav=read('src/views/partials/admin-manager-nav.ejs');
  const view=read('src/views/admin-knowledge.ejs');
  const editor=read('src/views/admin-knowledge-edit.ejs');
  const curation=read('src/views/admin-wiki-catalog.ejs');
  const css=read('public/css/cms-knowledge.css');
  const cmsCss=read('public/css/wiki-cms.css');
  const header=read('src/views/partials/header.ejs');
  assert.match(nav,/\/admin\/knowledge/);
  assert.match(nav,/Game Database/);
  assert.match(view,/Game Database & Knowledge/);
  assert.match(view,/NEW ARTICLE/);
  assert.match(view,/CURATE GAME DATA/);
  assert.match(view,/Publish without code changes/);
  assert.match(view,/Open Public Wiki/);
  assert.match(curation,/Wiki Data Curation/);
  assert.match(curation,/Automatic/);
  assert.match(curation,/Force public/);
  assert.match(curation,/Force hidden/);
  assert.match(curation,/name="reason"/);
  assert.match(editor,/CREATE ARTICLE/);
  assert.match(editor,/SAVE CHANGES/);
  assert.match(editor,/name="published"/);
  assert.match(css,/\.knowledgeWorkspace/);
  assert.match(css,/\.knowledgeTable/);
  assert.match(css,/\.wikiCurationWrap/);
  assert.match(css,/\.wikiVisibilityForm/);
  assert.match(cmsCss,/\.wikiEditor/);
  assert.match(header,/cms-knowledge\.css/);
  assert.match(header,/wiki-cms\.css/);
});
