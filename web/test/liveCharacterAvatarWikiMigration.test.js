const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.join(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');

test('rankings query exposes the real character id needed for appearance rendering',()=>{
  const service=read('src/services/gameService.js');
  assert.match(service,/characterId/);
  assert.match(service,/c\.\$\{I\(g\.characterId\)\} id/);
  assert.match(service,/function characterAppearance/);
  assert.match(service,/characterSkin/);
  assert.match(service,/characterFace/);
  assert.match(service,/characterHair/);
  assert.match(service,/inventoryItemsTable/);
  assert.match(service,/inventorytype=-1/);
  assert.match(service,/type=1/);
  assert.match(service,/resolveVisibleEquipment/);
});

test('same-origin avatar route renders saved appearance and falls back safely',()=>{
  const avatar=read('src/routes/avatar.js');
  const server=read('src/server.js');
  const env=read('src/config/env.js');
  assert.match(server,/routes\/avatar/);
  assert.match(avatar,/\/character-avatar\/:id\.png/);
  assert.match(avatar,/game\.characterAppearance/);
  assert.match(avatar,/Character\/center/);
  assert.match(avatar,/appearance\.face/);
  assert.match(avatar,/appearance\.hair/);
  assert.match(avatar,/appearance\.equipment/);
  assert.match(avatar,/fetchAvatar\(rendererUrl\(appearance,true\)\)/);
  assert.match(avatar,/fetchAvatar\(rendererUrl\(appearance,false\)\)/);
  assert.match(avatar,/fallbackAsset/);
  assert.match(env,/MAPLESTORY_IO_BASE_URL/);
  assert.match(env,/MAPLESTORY_IO_VERSION/);
});

test('Wiki migration refreshes only untouched seed rows',()=>{
  const cms=read('src/db/cms.js');
  assert.match(cms,/WIKI_SEED_VERSION = 2/);
  assert.match(cms,/wiki_player_seed_version/);
  assert.match(cms,/WHERE slug=@slug AND updated_at=created_at/);
  assert.match(cms,/RETIRED_DEVELOPER_SLUGS/);
  assert.match(cms,/published=0/);
});

test('public Wiki is server-data first while preserving staff guides',()=>{
  const catalog=read('src/services/wikiCatalog.js');
  const dataService=read('src/services/wikiDataService.js');
  const view=read('src/views/wiki.ejs');
  const route=read('src/routes/wiki.js');
  for(const text of ['Getting Started','Knights of Cygnus','Voting for EverLeaf','Installing EverLeaf','Live Player Rankings']) {
    assert.match(catalog,new RegExp(text.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')));
  }
  assert.match(dataService,/TYPE_META/);
  assert.match(dataService,/drop_data/);
  assert.match(dataService,/shopitems/);
  assert.match(view,/EVERLEAF DATA WIKI/);
  assert.match(view,/WZ \+ MySQL/);
  assert.match(route,/\/wiki\/guides/);
  assert.doesNotMatch(view,/EVERLEAF PLAYER WIKI/);
});
