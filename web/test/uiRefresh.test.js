const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname,"..");
const read = file => fs.readFileSync(path.join(root,file),"utf8");
const header = read("src/views/partials/header.ejs");
const footer = read("src/views/partials/footer.ejs");
const home = read("src/views/home.ejs");
const wiki = read("src/views/wiki.ejs");
const rankings = read("src/views/rankings.ejs");
const account = read("src/views/account.ejs");
const downloads = read("src/views/downloads.ejs");
const help = read("src/views/help.ejs");
const remaster = read("public/css/maple-remaster.css");
const pages = read("public/css/maple-remaster-pages.css");
const admin = read("public/css/maple-remaster-admin.css");
const jobs = read("public/css/maple-jobs.css");
const final = read("public/css/maple-final.css");
const rankingsCss = read("public/css/rankings-remaster.css");
const homePolish = read("public/css/home-polish.css");
const assertRgbaPng = relative => {
  const file=path.join(root,relative);
  assert.ok(fs.existsSync(file),`${relative} should exist`);
  const data=fs.readFileSync(file);
  assert.ok(data.length>5000,`${relative} should be a real image`);
  assert.equal(data[25],6,`${relative} should retain an RGBA alpha channel`);
};

test("global navigation loads the unified Maple remaster design system",()=>{
  assert.match(header,/maple-remaster\.css/);
  assert.match(header,/maple-remaster-pages\.css/);
  assert.match(header,/maple-jobs\.css/);
  assert.match(header,/maple-final\.css/);
  assert.match(header,/rankings-remaster\.css/);
  assert.match(header,/home-polish\.css/);
  assert.match(header,/maple-remaster-admin\.css/);
  assert.doesNotMatch(header,/design-v2\.css/);
  assert.doesNotMatch(header,/home-v2\.css/);
  assert.doesNotMatch(header,/cms-v2\.css/);
  assert.match(header,/mobileMenu/);
  assert.match(header,/siteBanner/);
  assert.match(header,/worldRibbon/);
  assert.match(header,/{href:"\/wiki",label:"WIKI"}/);
  assert.doesNotMatch(header,/{href:"\/about",label:"WORLD"}/);
});

test("footer exposes useful site navigation",()=>{
  assert.match(footer,/footerGrid/);
  assert.match(footer,/\/downloads/);
  assert.match(footer,/\/rankings/);
  assert.match(footer,/\/recover/);
});

test("homepage class guide uses clean centered local artwork",()=>{
  assert.match(home,/everleaf-remaster\.svg/);
  assert.match(home,/homeV2Hero/);
  assert.match(home,/homeV2Status/);
  assert.match(home,/homeFeatureGrid/);
  assert.match(home,/homeCta/);
  assert.match(home,/hero-left\.webp/);
  assert.match(home,/hero-right\.webp/);
  assert.match(remaster,/hero-forest\.webp/);
  assert.match(home,/mapleJobsGridSix/);
  assert.match(home,/beginnerJobCard/);
  assert.match(home,/\/assets\/jobs\/beginner\/beginner-clean\.png/);
  assert.doesNotMatch(home,/\/assets\/jobs\/beginner\/beginner\.png/);
  assertRgbaPng("public/assets/jobs/beginner/beginner-clean.png");

  for(const asset of ["warrior","magician","bowman","thief","pirate"]) {
    assert.match(home,new RegExp(`/assets/jobs/instructors/${asset}\\.png`));
    assert.ok(fs.statSync(path.join(root,`public/assets/jobs/instructors/${asset}.png`)).size>500);
    assert.doesNotMatch(home,new RegExp(`/assets/jobs/${asset}\\.svg`));
  }
  assert.doesNotMatch(home,/mapleJobBadge/);
  assert.doesNotMatch(homePolish,/content:\s*"NEW"/);
  assert.match(homePolish,/\.mapleJobsGridSix \.mapleJobPortrait\{height:164px/);
  assert.match(homePolish,/align-items:center;justify-content:center/);

  assert.match(home,/\/assets\/jobs\/special\/cygnus-clean\.png/);
  assert.doesNotMatch(home,/\/assets\/jobs\/special\/cygnus\.png/);
  assertRgbaPng("public/assets/jobs/special/cygnus-clean.png");
  for(const asset of ["aran","evan"]) {
    assert.match(home,new RegExp(`/assets/jobs/special/${asset}\\.png`));
    assert.ok(fs.statSync(path.join(root,`public/assets/jobs/special/${asset}.png`)).size>5000);
    assert.doesNotMatch(home,new RegExp(`/assets/jobs/${asset}\\.svg`));
  }
  assert.match(home,/cygnusFeature/);
  assert.match(home,/specialCompact aranFeature/);
  assert.match(home,/specialCompact evanFeature/);
  assert.match(homePolish,/\.cygnusFeatureArt img\{max-width:300px/);
  assert.match(homePolish,/radial-gradient/);
  assert.match(homePolish,/\.siteFooter:before\{display:none!important/);
  assert.match(home,/Dances with Balrog/);
  assert.match(home,/Grendel the Really Old/);
  assert.match(home,/Athena Pierce/);
  assert.match(home,/Dark Lord/);
  assert.match(home,/Kyrin/);
  assert.match(home,/Ereve · Knights of Cygnus/);
  assert.match(home,/Rien · Legendary Polearm Warrior/);
  assert.match(home,/Dragon Master · Mir/);
  assert.match(home,/href="\/wiki"/);
  for(const asset of ["launcher","trophy","journal","community","account"]) assert.match(home,new RegExp(`/assets/ui/${asset}\\.svg`));
});

test("wiki placeholder is wired for future database work",()=>{
  assert.match(wiki,/EVERLEAF WIKI/);
  assert.match(wiki,/Jobs & Skills/);
  assert.match(wiki,/World Database/);
  assert.match(wiki,/Server Guide/);
  assert.match(homePolish,/\.wikiHeroCard/);
});

test("rankings render a Maple-style leaderboard with individual local Cygnus and clean Beginner artwork",()=>{
  assert.match(rankings,/rankingPodium/);
  assert.match(rankings,/rankingTableV2/);
  assert.match(rankings,/rankPlayerIcon/);
  assert.match(rankings,/rankingJobBadge/);
  assert.match(rankings,/\/assets\/jobs\/beginner\/beginner-clean\.png/);
  assert.match(rankings,/\/assets\/jobs\/special\/cygnus-clean\.png/);
  assert.match(rankings,/\/assets\/jobs\/special\/aran\.png/);
  assert.match(rankings,/\/assets\/jobs\/special\/evan\.png/);
  for(const asset of ["warrior","magician","bowman","thief","pirate"]) assert.match(rankings,new RegExp(`/assets/jobs/instructors/${asset}\\.png`));
  for(const asset of ["dawn-warrior","blaze-wizard","wind-archer","night-walker","thunder-breaker"]) {
    assert.match(rankings,new RegExp(`/assets/jobs/cygnus/${asset}\\.png`));
    const file=path.join(root,`public/assets/jobs/cygnus/${asset}.png`);
    assert.ok(fs.existsSync(file),`${asset} ranking artwork should exist`);
    assert.ok(fs.statSync(file).size>10000,`${asset} ranking artwork should be a real image`);
  }
  for(const asset of ["cygnus","aran","evan"]) assert.doesNotMatch(rankings,new RegExp(`/assets/jobs/${asset}\\.svg`));
  assert.match(rankingsCss,/\.rankingPodium/);
  assert.match(rankingsCss,/\.rankPlayerIcon/);
  assert.match(rankingsCss,/@media\(max-width:600px\)/);
});

test("account portal renders local job identity",()=>{
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
  assert.match(final,/\.mapleJobPortrait/);
});
