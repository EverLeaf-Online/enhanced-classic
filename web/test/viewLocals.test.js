const test = require("node:test");
const assert = require("node:assert/strict");

process.env.CMS_DB_PATH = ":memory:";
const viewLocals = require("../src/middleware/viewLocals");

test("view locals expose the logged-in player to shared navigation", () => {
  const player={id:42,name:"Kuro"};
  const req={session:{player},path:"/news"};
  const res={locals:{}};
  let called=false;
  viewLocals(req,res,()=>{called=true;});
  assert.equal(called,true);
  assert.equal(res.locals.player,player);
  assert.equal(res.locals.sessionPlayer,player);
  assert.equal(res.locals.currentPath,"/news");
});

test("view locals expose null player for logged-out visitors", () => {
  const req={session:{},path:"/downloads"};
  const res={locals:{}};
  viewLocals(req,res,()=>{});
  assert.equal(res.locals.player,null);
  assert.equal(res.locals.sessionPlayer,null);
});
