const test=require('node:test');
const assert=require('node:assert/strict');
const policy=require('../src/services/wikiPublicCatalog')._test;

test('public Wiki catalog removes obvious internal records',()=>{
  const rows=[
    {type:'items',id:1000001,name:'Red Bandana',description:'A bandana.',subtype:'Equipment'},
    {type:'items',id:1000002,name:'Dummy Item',description:'internal',subtype:'Equipment'},
    {type:'items',id:1000003,name:'?',description:'',subtype:'Equipment'},
    {type:'items',id:1000004,name:'Debug Sword',description:'do not use',subtype:'Equipment'}
  ];
  const result=policy.dedupeEntities(rows);
  assert.equal(result.length,1);
  assert.equal(result[0].name,'Red Bandana');
});

test('public Wiki catalog consolidates identical duplicate listings',()=>{
  const rows=[
    {type:'npcs',id:9000000,name:'Cody',description:'Event NPC',subtype:''},
    {type:'npcs',id:9000001,name:' Cody ',description:'Event NPC',subtype:''},
    {type:'npcs',id:9000002,name:'Cody',description:'Different function',subtype:''}
  ];
  const result=policy.dedupeEntities(rows);
  assert.equal(result.length,2);
  const duplicate=result.find(row=>row.description==='Event NPC');
  assert.ok(duplicate);
  assert.equal(duplicate.id,9000000);
  assert.equal(duplicate.variantCount,2);
  assert.deepEqual(duplicate.variantIds,[9000000,9000001]);
});

test('catalog cleanup does not hide legitimate quest names containing Test',()=>{
  const rows=[{type:'quests',id:1001,name:'Test of Wisdom',description:'Complete the challenge.',subtype:''}];
  const result=policy.dedupeEntities(rows);
  assert.equal(result.length,1);
  assert.equal(result[0].name,'Test of Wisdom');
});
