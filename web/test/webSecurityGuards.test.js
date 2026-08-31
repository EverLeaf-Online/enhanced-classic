const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname,"..");
const server = fs.readFileSync(path.join(root,"src/server.js"),"utf8");
const footer = fs.readFileSync(path.join(root,"src/views/partials/footer.ejs"),"utf8");

test("authentication POSTs have a dedicated tighter limiter",()=>{
  assert.match(server,/windowMs:15\*60_000/);
  assert.match(server,/max:12/);
  assert.match(server,/skip:req=>req\.method!=="POST"/);
  assert.match(server,/\["\/login","\/register","\/admin\/login"\]/);
});

test("sensitive account and admin responses disable caching",()=>{
  assert.match(server,/req\.path\.startsWith\("\/account"\)/);
  assert.match(server,/req\.path\.startsWith\("\/admin"\)/);
  assert.match(server,/res\.set\("Cache-Control","no-store"\)/);
});

test("footer exposes CMS-managed legal and information pages",()=>{
  assert.match(footer,/href="\/about">About/);
  assert.match(footer,/href="\/rules">Rules/);
  assert.match(footer,/href="\/terms">Terms/);
});
