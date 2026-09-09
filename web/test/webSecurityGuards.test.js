const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname,"..");
const server = fs.readFileSync(path.join(root,"src/server.js"),"utf8");
const publicRoutes = fs.readFileSync(path.join(root,"src/routes/public.js"),"utf8");
const footer = fs.readFileSync(path.join(root,"src/views/partials/footer.ejs"),"utf8");

test("authentication and recovery POSTs have a dedicated tighter limiter",()=>{
  assert.match(server,/windowMs:15\*60_000/);
  assert.match(server,/max:12/);
  assert.match(server,/skip:req=>req\.method!=="POST"/);
  assert.match(server,/\["\/login","\/register","\/recover","\/admin\/login"\]/);
});

test("sensitive account and admin responses disable caching",()=>{
  assert.match(server,/req\.path\.startsWith\("\/account"\)/);
  assert.match(server,/req\.path\.startsWith\("\/admin"\)/);
  assert.match(server,/req\.path==="\/recover"/);
  assert.match(server,/res\.set\("Cache-Control","no-store"\)/);
});

test("CMS-managed legal and information pages remain routed after footer removal",()=>{
  assert.match(publicRoutes,/router\.get\("\/about"/);
  assert.match(publicRoutes,/router\.get\("\/rules"/);
  assert.match(publicRoutes,/router\.get\("\/terms"/);
  assert.doesNotMatch(footer,/<footer|href="\/about"|href="\/rules"|href="\/terms"/);
});
