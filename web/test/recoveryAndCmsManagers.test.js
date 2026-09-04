const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");

const root=path.join(__dirname,"..");
const read=file=>fs.readFileSync(path.join(root,file),"utf8");
const server=read("src/server.js");
const recovery=read("src/routes/recovery.js");
const adminContent=read("src/routes/admin-content.js");
const cms=read("src/db/cms.js");
const login=read("src/views/login.ejs");
const admin=read("src/views/admin.ejs");

test("recovery requests are rate limited and privacy safe",()=>{
  assert.match(server,/"\/recover"/);
  assert.match(server,/req\.path==="\/recover"/);
  assert.match(recovery,/Always return the same response/);
  assert.match(recovery,/account_recovery_requests/);
  assert.match(login,/href="\/recover"/);
});

test("CMS initializes a staff recovery queue",()=>{
  assert.match(cms,/CREATE TABLE IF NOT EXISTS account_recovery_requests/);
  assert.match(cms,/CHECK\(status IN \('pending','resolved','rejected'\)\)/);
  assert.match(adminContent,/router\.get\("\/recoveries"/);
  assert.match(adminContent,/recovery\.update/);
});

test("CMS dashboard links dedicated content managers",()=>{
  assert.match(admin,/href="\/admin\/news"/);
  assert.match(admin,/href="\/admin\/settings-view"/);
  assert.match(admin,/href="\/admin\/audit"/);
  assert.match(admin,/href="\/admin\/recoveries"/);
});
