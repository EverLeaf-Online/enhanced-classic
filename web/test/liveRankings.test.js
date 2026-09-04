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

test('rankings route uses database pagination, player search, and all supported families',()=>{
  const route=read('src/routes/public.js');
  assert.match(route,/game\.rankingPage/);
  assert.match(route,/RANKINGS_PAGE_SIZE = 25/);
  for(const family of ['adventurer','warrior','magician','bowman','thief','pirate','cygnus','aran','evan']) assert.match(route,new RegExp(`${family}:`));
  assert.match(route,/search:q/);
  assert.match(route,/onlinePlayers/);
});

test('rankings UI clearly identifies live MySQL data and exposes useful stats',()=>{
  const view=read('src/views/rankings.ejs');
  const css=read('public/css/rankings-live.css');
  const header=read('src/views/partials/header.ejs');
  assert.match(view,/Live MySQL leaderboard/);
  assert.match(view,/FIND A PLAYER/);
  assert.match(view,/Ranked characters/);
  assert.match(view,/Players online/);
  assert.match(view,/>Fame</);
  assert.match(view,/>EXP</);
  assert.match(css,/\.rankingStats/);
  assert.match(css,/\.rankingSearch/);
  assert.match(header,/rankings-live\.css/);
});
