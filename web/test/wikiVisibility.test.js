const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');

const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'everleaf-wiki-visibility-'));
process.env.CMS_DB_PATH=path.join(tmp,'cms.sqlite');
const {db,initCms}=require('../src/db/cms');
initCms();
const visibility=require('../src/services/wikiVisibilityService');

test.after(()=>{
  try{db.close();}catch{}
  fs.rmSync(tmp,{recursive:true,force:true});
});

test('CMS creates a persistent per-entity Wiki visibility table',()=>{
  const table=db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='wiki_entity_visibility'").get();
  assert.ok(table);
});

test('automatic curation hides obvious junk without hiding legitimate Test names',()=>{
  assert.equal(visibility.automaticDecision({type:'items',id:1,name:'Dummy Item',description:'internal'}).hidden,true);
  assert.equal(visibility.automaticDecision({type:'items',id:2,name:'[[FROZEN CONTENT]] Pet Skill',description:''}).hidden,true);
  assert.equal(visibility.automaticDecision({type:'items',id:3,name:'GM Only Item',description:''}).hidden,true);
  assert.equal(visibility.automaticDecision({type:'items',id:31,name:'MISSING NAME',description:''}).hidden,true);
  assert.equal(visibility.automaticDecision({type:'items',id:32,name:"Admin's Candle",description:''}).hidden,true);
  assert.equal(visibility.automaticDecision({type:'skills',id:33,name:'ADMIN_ANTIMACRO',description:''}).hidden,true);
  assert.equal(visibility.automaticDecision({type:'quests',id:4,name:'Test of Wisdom',description:'Complete the challenge.'}).hidden,false);
  assert.equal(visibility.automaticDecision({type:'items',id:5,name:'Red Bandana',description:'A bandana.'}).hidden,false);
});

test('manual overrides take precedence in both directions',()=>{
  db.prepare("INSERT INTO wiki_entity_visibility(entity_type,entity_id,visibility,reason,updated_by) VALUES(?,?,?,?,?)")
    .run('items',100,'hidden','Known GM/internal item','qa');
  db.prepare("INSERT INTO wiki_entity_visibility(entity_type,entity_id,visibility,reason,updated_by) VALUES(?,?,?,?,?)")
    .run('items',101,'visible','Confirmed legitimate despite legacy name','qa');

  const normal={type:'items',id:100,name:'Normal Looking Item',description:'',subtype:'Cash'};
  const autoHidden={type:'items',id:101,name:'Dummy Item',description:'',subtype:'Cash'};
  const hidden=visibility.decision(normal);
  const visible=visibility.decision(autoHidden);

  assert.equal(hidden.visible,false);
  assert.equal(hidden.source,'manual-hidden');
  assert.equal(hidden.reason,'Known GM/internal item');
  assert.equal(visible.visible,true);
  assert.equal(visible.source,'manual-visible');
  assert.equal(visible.automaticHidden,true);
});

test('public filtering applies persisted visibility decisions',()=>{
  const rows=[
    {type:'items',id:100,name:'Normal Looking Item',description:'',subtype:'Cash'},
    {type:'items',id:101,name:'Dummy Item',description:'',subtype:'Cash'},
    {type:'items',id:102,name:'Player Item',description:'',subtype:'Cash'}
  ];
  const filtered=visibility.filterPublic(rows);
  assert.deepEqual(filtered.map(row=>row.id),[101,102]);
});
