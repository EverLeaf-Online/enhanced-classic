const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname,"..");
const header = fs.readFileSync(path.join(root,"src/views/partials/header.ejs"),"utf8");
const account = fs.readFileSync(path.join(root,"src/views/account.ejs"),"utf8");
const admin = fs.readFileSync(path.join(root,"src/views/admin.ejs"),"utf8");

test("logged-in account navigation remains available in desktop and mobile terminal chrome",()=>{
  assert.match(header,/accountNav/);
  assert.match(header,/href="\/account">ACCOUNT<\/a>/);
  assert.match(header,/terminalMobilePanel/);
});

test("account dashboard exposes the main player actions",()=>{
  assert.match(account,/PLAY \/ DOWNLOAD/);
  assert.match(account,/VOTE FOR NX/);
  assert.match(account,/href="\/help">SUPPORT/);
  assert.match(account,/PENDING NX/);
  assert.match(account,/terminalAccountPage/);
});

test("cms dashboard exposes direct management shortcuts in operations layout",()=>{
  assert.match(admin,/CONTENT LIBRARY/);
  assert.match(admin,/SERVER HEALTH/);
  assert.match(admin,/STAFF:\/\/CMS/);
  assert.match(admin,/href="\/admin\/announcements"/);
  assert.match(admin,/href="\/admin\/downloads"/);
  assert.match(admin,/href="\/admin\/pages"/);
  assert.match(admin,/href="\/admin\/supporters"/);
  assert.match(admin,/href="\/admin\/recoveries"/);
});
