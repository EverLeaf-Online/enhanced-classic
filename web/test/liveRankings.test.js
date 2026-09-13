const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.join(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');

test('rankings service reads real character data with account safety filters',()=>{
  const service=read('src/services/gameService.js');
  assert.match(service,/async function rankingPage/);
  assert.match(service,/INNER JOIN/);
  assert.match(service,/accountBanned/);
  assert.match(service,/characterGm/);
  assert.match(service,/LIMIT \? OFFSET \?/);
  assert.match(service,/characterLevel/);
  assert.match(service,/characterExp/);
  assert.match(service,/characterFame/);
});

test('rankings route uses viewport pagination, player search, and all supported families',()=>{
  const route=read('src/routes/public.js');
  assert.match(route,/game\.rankingPage/);
  assert.match(route,/RANKINGS_PAGE_SIZE = 6/);
  for(const family of ['adventurer','beginner','warrior','magician','bowman','thief','pirate','cygnus','dawn_warrior','blaze_wizard','wind_archer','night_walker','thunder_breaker','aran','evan']) assert.match(route,new RegExp(`${family}:`));
  assert.match(route,/parent:"adventurer"/);
  assert.match(route,/parent:"cygnus"/);
  assert.match(route,/search:q/);
  assert.match(route,/onlinePlayers/);
});

test('rankings UI exposes live data, useful stats, and hierarchical job filters',()=>{
  const view=read('src/views/rankings.ejs');
  const css=read('public/css/rankings-wide-2026.css');
  const header=read('src/views/partials/header.ejs');
  assert.match(view,/EverLeaf Leaderboard/);
  assert.match(view,/Search character name/);
  assert.match(view,/rankingsInlineStats/);
  assert.match(view,/Ranked/);
  assert.match(view,/Online/);
  assert.match(view,/rankingsFilterStack/);
  assert.match(view,/rankingsSubTabs/);
  assert.match(view,/>Fame</);
  assert.match(view,/>EXP</);
  assert.match(view,/data-live-avatar/);
  assert.match(css,/\.rankingsInlineStats/);
  assert.match(css,/\.rankingsSearchInline/);
  assert.match(css,/\.rankingsSubTabs/);
  assert.match(header,/rankings-wide-2026\.css\?v=6/);
});
