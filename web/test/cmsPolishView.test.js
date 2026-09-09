const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname,"..");
const header = fs.readFileSync(path.join(root,"src/views/partials/header.ejs"),"utf8");
const home = fs.readFileSync(path.join(root,"src/views/home.ejs"),"utf8");
const account = fs.readFileSync(path.join(root,"src/views/account.ejs"),"utf8");
const admin = fs.readFileSync(path.join(root,"src/views/admin.ejs"),"utf8");

test("account access moves out of the removed top navigation",()=>{
  assert.doesNotMatch(header,/accountNav|terminalNav|mobileMenu/);
  assert.match(home,/href="<%=sessionPlayer\?'\/account':'\/login'%>"/);
  assert.match(home,/sessionPlayer\?'ACCOUNT':'LOGIN'/);
});

test("account dashboard exposes the main player actions",()=>{
  assert.match(account,/PLAY \/ DOWNLOAD/);
  assert.match(account,/VOTE FOR NX/);
  assert.match(account,/href="\/help">SUPPORT/);
  assert.match(account,/Pending Vote NX/);
});

test("cms dashboard exposes direct management shortcuts",()=>{
  assert.match(admin,/Content Library/);
  assert.match(admin,/href="\/admin\/announcements"/);
  assert.match(admin,/href="\/admin\/downloads"/);
  assert.match(admin,/href="\/admin\/pages"/);
  assert.match(admin,/href="\/admin\/supporters"/);
  assert.match(admin,/href="\/admin\/recoveries"/);
});
