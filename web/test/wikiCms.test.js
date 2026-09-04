const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');

const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'everleaf-wiki-'));
process.env.CMS_DB_PATH=path.join(tmp,'cms.sqlite');
const {db,initCms}=require('../src/db/cms');
initCms();
const wiki=require('../src/services/wikiService');

test.after(()=>{
  try{db.close();}catch{}
  fs.rmSync(tmp,{recursive:true,force:true});
});

test('initCms seeds the public Wiki into persistent CMS storage',()=>{
  const stats=wiki.stats();
  assert.ok(stats.total>=19);
  assert.ok(stats.published>=19);
  const article=wiki.getBySlug('enhanced-classic');
  assert.ok(article);
  assert.equal(article.published,true);
  assert.ok(article.sections.length>=1);
});

test('Wiki search reads article body, tags, and category from SQLite',()=>{
  assert.ok(wiki.searchEntries('manifest').some(entry=>entry.slug==='launcher-repair-updates'));
  assert.ok(wiki.searchEntries('pet vac').some(entry=>entry.slug==='pet-vac'));
  assert.ok(wiki.searchEntries('', 'progression').every(entry=>entry.category==='progression'));
});

test('staff can create a draft, edit it, then publish it',()=>{
  const created=wiki.saveArticle({
    slug:'test-player-guide',
    category:'systems',
    title:'Test Player Guide',
    eyebrow:'PLAYER GUIDE',
    summary:'A temporary article used to validate the CMS-backed Wiki workflow.',
    body:'## Overview\nDraft body.\n\n## Details\nMore details.',
    status:'Draft Guide',
    verification:'Test verified',
    source:'EverLeaf test',
    sourceDoc:'wikiCms.test.js',
    tags:'test, guide, test',
    facts:'Level: 1\nMode: Test',
    published:false
  });
  assert.equal(created.published,false);
  assert.equal(wiki.getBySlug('test-player-guide'),null);
  assert.ok(wiki.getBySlug('test-player-guide',true));
  const updated=wiki.saveArticle({...wiki.editorFields(created),id:created.id,body:'## Overview\nPublished body.',published:true});
  assert.equal(updated.published,true);
  assert.equal(wiki.getBySlug('test-player-guide').sections[0].body,'Published body.');
  assert.deepEqual(updated.tags,['test','guide']);
  assert.deepEqual(updated.facts,[['Level','1'],['Mode','Test']]);
});
