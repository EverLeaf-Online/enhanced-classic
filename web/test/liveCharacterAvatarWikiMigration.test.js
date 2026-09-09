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

test('same-origin avatar route renders saved appearance through local Character.wz and falls back safely',()=>{
  const avatar=read('src/routes/avatar.js');
  const appearance=read('src/services/avatarAppearanceService.js');
  const rankings=read('src/views/rankings.ejs');
  const site=read('public/js/site.js');
  const server=read('src/server.js');
  const env=read('src/config/env.js');
  assert.match(server,/routes\/avatar/);
  assert.match(avatar,/\/character-avatar\/:id\.png/);
  assert.match(avatar,/appearances\.characterAppearance/);
  assert.match(appearance,/game\.characterAppearance/);
  assert.match(appearance,/retrying without equipment/);
  assert.match(appearance,/equipment:\[\]/);
  assert.match(avatar,/localRendererUrl/);
  assert.match(avatar,/localRendererIds/);
  assert.match(avatar,/2000 \+ skin/);
  assert.match(avatar,/12000 \+ skin/);
  assert.match(avatar,/appearance\.face/);
  assert.match(avatar,/appearance\.hair/);
  assert.match(avatar,/appearance\.equipment/);
  assert.match(avatar,/renderAppearance\(appearance,true\)/);
  assert.match(avatar,/renderAppearance\(appearance,false\)/);
  assert.match(avatar,/sendFallback/);
  assert.match(avatar,/X-EverLeaf-Avatar-Source/);
  assert.match(avatar,/local-wz/);
  assert.match(rankings,/data-live-avatar/);
  assert.doesNotMatch(rankings,/onerror=/);
  assert.match(site,/querySelectorAll\('img\[data-live-avatar\]'\)/);
  assert.match(site,/const probe = new Image\(\)/);
  assert.match(site,/image\.src = liveUrl/);
  assert.match(env,/CHARACTER_WZ_RENDERER_URL/);
  assert.match(env,/MAPLESTORY_IO_BASE_URL \|\| ""/);
  assert.match(env,/MAPLESTORY_IO_VERSION \|\| "83"/);
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
