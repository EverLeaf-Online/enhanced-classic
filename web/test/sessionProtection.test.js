const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const os=require("node:os");
const path=require("node:path");
const express=require("express");
const session=require("express-session");
const Store=require("../src/utils/sqliteSessionStore");
const csrf=require("../src/middleware/csrf");
const call=(obj,method,...args)=>new Promise((resolve,reject)=>obj[method](...args,(e,v)=>e?reject(e):resolve(v)));

test("sessions survive store reopen; expiration, touch and logout are enforced",async()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),"everleaf-session-"));
 let now=1000;
 let store=new Store(path.join(dir,"sessions.sqlite"),{now:()=>now});
 try {
  await call(store,"set","one",{player:{id:42},cookie:{expires:new Date(2000)}});
  store.close();store=new Store(path.join(dir,"sessions.sqlite"),{now:()=>now});
  assert.equal((await call(store,"get","one")).player.id,42);
  await call(store,"touch","one",{cookie:{expires:new Date(4000)}});
  now=3000;assert.equal((await call(store,"get","one")).player.id,42);
  now=4001;assert.equal(await call(store,"get","one"),null);
  await call(store,"set","two",{cookie:{expires:new Date(6000)}});
  await call(store,"destroy","two");assert.equal(await call(store,"get","two"),null);
 }finally{store.close();fs.rmSync(dir,{recursive:true,force:true});}
});

test("HTTP forms require the token from their own session and login rotates the session",async()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),"everleaf-csrf-"));
 const store=new Store(path.join(dir,"sessions.sqlite"));
 const app=express();
 app.use(express.urlencoded({extended:false}));
 app.use(session({secret:"isolated-test-secret-not-production",store,resave:false,saveUninitialized:false}));
 app.use(csrf);
 app.get("/",(req,res)=>res.json({token:res.locals.csrfToken,sid:req.sessionID}));
 app.post("/login",async(req,res,next)=>{
  try {
   await new Promise((resolve,reject)=>req.session.regenerate(e=>e?reject(e):resolve()));
   req.session.player={id:42};res.json({sid:req.sessionID});
  }catch(e){next(e);}
 });
 const server=app.listen(0,"127.0.0.1");
 await new Promise(r=>server.once("listening",r));
 const url="http://127.0.0.1:"+server.address().port;
 try {
  const first=await fetch(url);
  const cookie=first.headers.get("set-cookie").split(";")[0];
  const original=await first.json();
  const post=(token,withCookie=true)=>fetch(url+"/login",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded",...(withCookie?{cookie}:{})},body:new URLSearchParams(token===undefined?{}:{_csrf:token})});
  assert.equal((await post()).status,403);
  assert.equal((await post("é".repeat(64))).status,403);
  assert.equal((await post(original.token,false)).status,403);
  const accepted=await post(original.token);assert.equal(accepted.status,200);
  assert.notEqual((await accepted.json()).sid,original.sid);
  assert.equal(await call(store,"get",original.sid),null);
 }finally{await new Promise(r=>server.close(r));store.close();fs.rmSync(dir,{recursive:true,force:true});}
});
