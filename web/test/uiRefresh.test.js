const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname,"..");
const read = file => fs.readFileSync(path.join(root,file),"utf8");
const header = read("src/views/partials/header.ejs");
const footer = read("src/views/partials/footer.ejs");
const home = read("src/views/home.ejs");
const rankings = read("src/views/rankings.ejs");
const account = read("src/views/account.ejs");
const downloads = read("src/views/downloads.ejs");
const help = read("src/views/help.ejs");
const remaster = read("public/css/maple-remaster.css");
const pages = read("public/css/maple-remaster-pages.css");
const admin = read("public/css/maple-remaster-admin.css");
const jobs = read("public/css/maple-jobs.css");
const final = read("public/css/maple-final.css");

test("global navigation loads the unified Maple remaster design system",()=>{
  assert.match(header,/maple-remaster\.css/);
  assert.match(header,/maple-remaster-pages\.css/);
  assert.match(header,/maple-jobs\.css/);
  assert.match(header,/maple-final\.css/);
  assert.match(header,/maple-remaster-admin\.css/);
  assert.doesNotMatch(header,/design-v2\.css/);
  assert.doesNotMatch(header,/home-v2\.css/);
  assert.doesNotMatch(header,/cms-v2\.css/);
  assert.match(header,/mobileMenu/);
  assert.match(header,/siteBanner/);
  assert.match(header,/worldRibbon/);
});

test("footer exposes useful site navigation",()=>{
  assert.match(footer,/footerGrid/);
  assert.match(footer,/\/downloads/);
  assert.match(footer,/\/rankings/);
  assert.match(footer,/\/recover/);
});

test("homepage uses a materially different EverLeaf Maple layout while preserving local world art",()=>{
  assert.match(home,/everleaf-remaster\.svg/);
  assert.match(home,/homeV2Hero/);
  assert.match(home,/homeV2Status/);
  assert.match(home,/homeFeatureGrid/);
  assert.match(home,/homeCta/);
  assert.match(home,/hero-left\.webp/);
  assert.match(home,/hero-right\.webp/);
  assert.match(remaster,/hero-forest\.webp/);
  assert.match(home,/mapleJobsGrid/);
  assert.match(home,/mapleSpecialJobs/);
  for(const asset of ["warrior","magician","bowman","thief","pirate","cygnus","aran","evan"]) assert.match(home,new RegExp(`/assets/jobs/${asset}\\.svg`));
  for(const asset of ["launcher","trophy","journal","community","account"]) assert.match(home,new RegExp(`/assets/ui/${asset}\\.svg`));
});

test("rankings and account portal render local job identity",()=>{
  assert.match(rankings,/rankingTable/);
  assert.match(rankings,/jobCell/);
  assert.match(rankings,/\/assets\/jobs\/cygnus\.svg/);
  assert.match(rankings,/\/assets\/jobs\/aran\.svg/);
  assert.match(rankings,/\/assets\/jobs\/evan\.svg/);
  assert.match(account,/characterCards/);
  assert.match(account,/characterJobIcon/);
  assert.match(account,/\/assets\/jobs\/warrior\.svg/);
});

test("downloads and help use local UI art instead of letter or number placeholders",()=>{
  assert.match(downloads,/\/assets\/ui\/launcher\.svg/);
  assert.match(downloads,/\/assets\/ui\/patch\.svg/);
  assert.match(downloads,/\/assets\/ui\/tool\.svg/);
  assert.doesNotMatch(downloads,/<div class="downloadIcon">(?:EL|UP|TL)<\/div>/);
  assert.match(help,/\/assets\/ui\/launcher\.svg/);
  assert.match(help,/\/assets\/ui\/account\.svg/);
  assert.match(help,/\/assets\/ui\/recovery\.svg/);
  assert.match(help,/\/assets\/ui\/community\.svg/);
  assert.doesNotMatch(help,/<div class="helpIcon">0[1-4]<\/div>/);
});

test("remaster styles cover public pages, authentication, CMS and mobile layouts",()=>{
  for (const token of [".lightPage",".pageHeroGrid",".newsList",".authWrap","@media(max-width:820px)"]) assert.match(remaster,new RegExp(token.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")));
  assert.match(pages,/\.accountShell/);
  assert.match(pages,/\.helpGrid/);
  assert.match(admin,/\.cmsManagerNav/);
  assert.match(admin,/\.cmsWorkspace/);
  assert.match(admin,/@media\(max-width:600px\)/);
  assert.match(jobs,/\.mapleSpecialJobs/);
  assert.match(final,/\.rankingBoard/);
  assert.match(final,/\.characterCards/);
  assert.match(final,/\.mapleQuickIcon img/);
});
