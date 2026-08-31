const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.join(__dirname,"..");
const read=file=>fs.readFileSync(path.join(root,file),"utf8");

const publicViews=["news.ejs","downloads.ejs","rankings.ejs","help.ejs","account.ejs","login.ejs","register.ejs","recover.ejs","support.ejs","page.ejs","post.ejs","404.ejs","500.ejs"];
const cmsViews=["admin-news.ejs","admin-announcements.ejs","admin-downloads.ejs","admin-pages.ejs","admin-recoveries.ejs","admin-settings.ejs","admin-audit.ejs","admin-edit-post.ejs","admin-edit-page.ejs","admin-edit-download.ejs"];

test("every major public view participates in the v2 visual system",()=>{
  for(const file of publicViews){
    const source=read(`src/views/${file}`);
    assert.match(source,/(lightPage|authWrap)/,`${file} should use the redesigned public shell`);
  }
});

test("all dedicated cms managers use the shared cms workspace navigation",()=>{
  for(const file of cmsViews){
    const source=read(`src/views/${file}`);
    assert.match(source,/partials\/admin-manager-nav/,`${file} should expose consistent CMS navigation`);
    assert.match(source,/(cmsPanel|cmsWorkspace)/,`${file} should use the redesigned CMS workspace`);
  }
});

test("cms dashboard and supporter manager keep the redesigned persistent sidebar",()=>{
  for(const file of ["admin.ejs","admin-supporters.ejs"]){
    const source=read(`src/views/${file}`);
    assert.match(source,/adminShell/);
    assert.match(source,/sideLink/);
    assert.match(source,/pageEyebrow/);
  }
});
