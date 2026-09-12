const test=require('node:test');
const assert=require('node:assert/strict');
const taxonomy=require('../src/services/wikiItemTaxonomy');

const item=(id,name,subtype,description='')=>({type:'items',id,name,subtype,description});

test('item taxonomy separates the major player-facing item families',()=>{
  assert.equal(taxonomy.leafCategory(item(1000000,'Blue Beanie','Equipment')),'equipment-hat');
  assert.equal(taxonomy.leafCategory(item(1302000,'Sword','Equipment')),'equipment-weapon');
  assert.equal(taxonomy.leafCategory(item(2040000,'Scroll for Helmet','Consumable')),'consumable-scroll');
  assert.equal(taxonomy.leafCategory(item(2000000,'Red Potion','Consumable')),'consumable-potion-food');
  assert.equal(taxonomy.leafCategory(item(3010000,'Relaxer Chair','Install / Chair')),'install-chair');
  assert.equal(taxonomy.leafCategory(item(4030000,'Quest Relic','ETC')),'etc-quest');
  assert.equal(taxonomy.leafCategory(item(4010000,'Bronze Ore','ETC')),'etc-material');
  assert.equal(taxonomy.leafCategory(item(5000000,'Brown Kitty','Pet')),'pets');
  assert.equal(taxonomy.leafCategory(item(5190000,'Pet Item Pick-Up','Cash')),'cash-pet');
  assert.equal(taxonomy.leafCategory(item(5070000,'Megaphone','Cash')),'cash-messaging');
});

test('broad item filters include their detailed subcategories',()=>{
  const hat=item(1000000,'Blue Beanie','Equipment');
  const scroll=item(2040000,'Scroll for Helmet','Consumable');
  assert.equal(taxonomy.matches(hat,'equipment'),true);
  assert.equal(taxonomy.matches(hat,'equipment-hat'),true);
  assert.equal(taxonomy.matches(hat,'consumable-scroll'),false);
  assert.equal(taxonomy.matches(scroll,'consumables'),true);
  assert.equal(taxonomy.matches(scroll,'consumable-scroll'),true);
});

test('category counts expose both broad and detailed totals',()=>{
  const rows=[
    item(1000000,'Blue Beanie','Equipment'),
    item(1302000,'Sword','Equipment'),
    item(2040000,'Scroll for Helmet','Consumable'),
    item(3010000,'Relaxer Chair','Install / Chair')
  ];
  const counts=taxonomy.counts(rows);
  assert.equal(counts.all,4);
  assert.equal(counts.equipment,2);
  assert.equal(counts['equipment-hat'],1);
  assert.equal(counts['equipment-weapon'],1);
  assert.equal(counts['consumable-scroll'],1);
  assert.equal(counts['install-chair'],1);
});
