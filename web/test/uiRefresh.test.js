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
const wikiDataCss = read("public/css/wiki-data.css");
const uiux = read("public/css/uiux-2026.css");
const refero = read("public/css/refero-everleaf-2026.css");
const assertRgbaPng = relative => {
  const file=path.join(root,relative);
  assert.ok(fs.existsSync(file),`${relative} should exist`);
  const data=fs.readFileSync(file);
  assert.ok(data.length>5000,`${relative} should be a real image`);
  assert.equal(data[25],6,`${relative} should retain an RGBA alpha channel`);
};

test("global navigation loads the unified redesign system",()=>{
  for(const sheet of [
    "maple-remaster.css","maple-remaster-pages.css","maple-jobs.css","maple-final.css",
    "rankings-remaster.css","rankings-live.css","home-polish.css","wiki-remaster.css",
    "wiki-cms.css","wiki-player-2026.css","wiki-data.css","uiux-2026.css","refero-everleaf-2026.css?v=2"
  ]) assert.ok(header.includes(sheet),`header should load ${sheet}`);
  assert.match(header,/maple-remaster-admin\.css/);
  assert.match(header,/mobileMenu/);
  assert.match(header,/siteBanner/);
  assert.match(header,/terminalRibbon/);
  assert.match(header,/terminalNav/);
  assert.match(header,/class="skipLink" href="#main-content"/);
  assert.match(header,/id="main-content"/);
  assert.match(header,/{href:"\/wiki",label:"WIKI",index:"05"}/);
  assert.match(header,/route-admin/);
  assert.doesNotMatch(header,/design-v2\.css|home-v2\.css|cms-v2\.css/);
});

test("footer exposes the redesigned site navigation",()=>{
  assert.match(footer,/terminalFooterGrid/);
  assert.match(footer,/terminalFooterWord/);
  assert.match(footer,/\/downloads/);
  assert.match(footer,/\/rankings/);
  assert.match(footer,/\/wiki/);
  assert.match(footer,/\/help/);
  assert.match(footer,/\/login/);
});

test("homepage is fully restructured around the terminal world portal",()=>{
  for(const token of [
    "terminalHero","everleafArtifact","heroTelemetry","signalStrip","dossierSection",
    "entrySection","classSection","dataSection","wikiSignalSection","finalTransmission"
  ]) assert.ok(home.includes(token),`homepage should include ${token}`);

  assert.match(home,/hero-left\.webp/);
  assert.match(home,/hero-right\.webp/);
  assert.match(home,/id="live-dot"/);
  assert.match(home,/id="live-state-label"/);
  assert.match(home,/id="live-status"/);
  assert.match(home,/id="live-players"/);
  assert.match(home,/id="live-channels"/);
  assert.match(home,/id="live-refresh"/);
  assert.match(home,/topCharacters/);
  assert.match(home,/featuredWiki/);
  assert.match(remaster,/hero-forest\.webp/);

  assert.match(home,/\/assets\/jobs\/beginner\/beginner-clean\.png/);
  assertRgbaPng("public/assets/jobs/beginner/beginner-clean.png");
  for(const asset of ["warrior","magician","bowman","thief","pirate"]) {
    assert.match(home,new RegExp(`/assets/jobs/instructors/${asset}\\.png`));
    assert.ok(fs.statSync(path.join(root,`public/assets/jobs/instructors/${asset}.png`)).size>500);
  }
  assert.match(home,/CYGNUS KNIGHTS \/ ARAN \/ EVAN/);
  assert.match(home,/href="\/wiki"/);
  assert.match(home,/href="\/rankings"/);
  assert.match(home,/href="\/downloads"/);
});

test("terminal redesign uses the selected dark compact visual contract",()=>{
  assert.match(refero,/--terminal-bg:#12130f/);
  assert.match(refero,/--terminal-text:#e4dfda/);
  assert.match(refero,/--terminal-line:#3c3c38/);
  assert.match(refero,/--terminal-glow:#f5c2c8/);
  assert.match(refero,/\.terminalHero\{/);
  assert.match(refero,/\.classMatrix\{/);
  assert.match(refero,/\.authGrid\{/);
  assert.match(refero,/\.terminalFooterGrid\{/);
  assert.match(refero,/@media \(max-width:960px\)/);
  assert.match(refero,/@media \(max-width:640px\)/);
  assert.match(refero,/prefers-reduced-motion/);
  assert.doesNotMatch(refero,/@import|https?:\/\//i);
});

test("wiki is a live WZ and MySQL server-data encyclopedia",()=>{
  assert.match(wiki,/EVERLEAF DATA WIKI/);
  for(const key of ["items","monsters","maps","skills","npcs","quests"]) assert.match(wiki,new RegExp(`${key}:`));
  assert.match(wiki,/WZ \+ MySQL/);
  assert.match(wiki,/BROWSE CATALOG/);
  assert.match(wiki,/\/wiki\/guides/);
  assert.match(wikiDataCss,/\.wikiCatalogGrid/);
  assert.match(wikiDataCss,/\.wikiEntityPage/);
  assert.match(wikiDataCss,/\.wikiDataTable/);
});

test("rankings preserve live saved character avatars with local class-art fallback",()=>{
  assert.match(rankings,/rankingPodium/);
  assert.match(rankings,/rankingTableV2/);
  assert.match(rankings,/rankPlayerIcon/);
  assert.match(rankings,/rankingJobBadge/);
  assert.match(rankings,/\/character-avatar\//);
  assert.match(rankings,/Live saved appearance/);
  assert.match(rankings,/rankingCharacterAvatar/);
  assert.match(rankings,/\/assets\/jobs\/beginner\/beginner-clean\.png/);
  assert.match(rankings,/\/assets\/jobs\/special\/cygnus-clean\.png/);
  assert.match(rankings,/\/assets\/jobs\/special\/aran\.png/);
  assert.match(rankings,/\/assets\/jobs\/special\/evan\.png/);
  for(const asset of ["warrior","magician","bowman","thief","pirate"]) assert.match(rankings,new RegExp(`/assets/jobs/instructors/${asset}\\.png`));
  for(const asset of ["dawn-warrior","blaze-wizard","wind-archer","night-walker","thunder-breaker"]) {
    assert.match(rankings,new RegExp(`/assets/jobs/cygnus/${asset}\\.png`));
    const file=path.join(root,`public/assets/jobs/cygnus/${asset}.png`);
    assert.ok(fs.existsSync(file),`${asset} fallback artwork should exist`);
    assert.ok(fs.statSync(file).size>10000,`${asset} fallback artwork should be a real image`);
  }
  assert.match(rankingsCss,/\.rankingCharacterAvatar/);
});

test("account portal keeps local job identity and working product surfaces",()=>{
  assert.match(account,/characterCards/);
  assert.match(account,/characterJobIcon/);
  assert.match(account,/\/assets\/jobs\/warrior\.svg/);
  assert.match(account,/\/account\/password/);
  assert.match(account,/\/account\/discord\/connect/);
});

test("downloads and help retain local UI assets",()=>{
  assert.match(downloads,/\/assets\/ui\/launcher\.svg/);
  assert.match(downloads,/\/assets\/ui\/patch\.svg/);
  assert.match(downloads,/\/assets\/ui\/tool\.svg/);
  assert.match(help,/\/assets\/ui\/launcher\.svg/);
  assert.match(help,/\/assets\/ui\/account\.svg/);
  assert.match(help,/\/assets\/ui\/recovery\.svg/);
  assert.match(help,/\/assets\/ui\/community\.svg/);
});

test("legacy functional CSS remains present beneath the terminal override",()=>{
  for (const token of [".lightPage",".pageHeroGrid",".newsList",".authWrap","@media(max-width:820px)"]) assert.match(remaster,new RegExp(token.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")));
  assert.match(pages,/\.accountShell/);
  assert.match(pages,/\.helpGrid/);
  assert.match(admin,/\.cmsManagerNav/);
  assert.match(admin,/\.cmsWorkspace/);
  assert.match(jobs,/\.mapleSpecialJobs/);
  assert.match(final,/\.rankingBoard/);
  assert.match(final,/\.characterCards/);
  for (const token of [".skipLink",":focus-visible","prefers-reduced-motion"]) {
    assert.match(uiux,new RegExp(token.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")));
  }
});
