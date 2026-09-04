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
const terminal = read("public/css/terminal-everleaf-2026.css");
const finish = read("public/css/terminal-everleaf-final-2026.css");
const assertAsset = relative => {
  const file=path.join(root,relative);
  assert.ok(fs.existsSync(file),`${relative} should exist`);
  assert.ok(fs.statSync(file).size>500,`${relative} should contain a real asset`);
};

test("global navigation uses the structural EverLeaf terminal shell",()=>{
  assert.match(header,/terminal-everleaf-2026\.css/);
  assert.match(header,/terminal-everleaf-final-2026\.css/);
  assert.match(header,/terminalHeader/);
  assert.match(header,/terminalNav/);
  assert.match(header,/terminalMode/);
  assert.match(header,/mobileMenu/);
  assert.match(header,/siteBanner/);
  assert.match(header,/worldRibbon/);
  assert.match(header,/class="skipLink" href="#main-content"/);
  assert.match(header,/id="main-content"/);
  assert.match(header,/{href:"\/wiki",label:"DATA"}/);
});

test("footer is a compact terminal status/navigation strip",()=>{
  assert.match(footer,/terminalFooter/);
  assert.match(footer,/EVERLEAF\/\/MS/);
  assert.match(footer,/\/downloads/);
  assert.match(footer,/\/rankings/);
  assert.match(footer,/\/help/);
});

test("homepage is rebuilt as a world terminal using local EverLeaf artwork",()=>{
  for(const marker of ["terminalHero","terminalHeroArtifact","terminalWorldReadout","terminalHeroActions","terminalSection","terminalJobGrid","terminalRankingPreview"]) assert.match(home,new RegExp(marker));
  assert.match(home,/everleaf-remaster\.svg/);
  assert.match(home,/hero-left\.webp/);
  assert.match(home,/hero-right\.webp/);
  assert.match(home,/data-live-avatar/);
  for(const asset of ["warrior","magician","bowman","thief","pirate"]) {
    assert.match(home,new RegExp(`/assets/jobs/instructors/${asset}\\.png`));
    assertAsset(`public/assets/jobs/instructors/${asset}.png`);
  }
  for(const asset of ["beginner/beginner-clean","special/cygnus-clean","special/aran","special/evan"]) assert.match(home,new RegExp(`/assets/jobs/${asset.replace('/','\\/')}\\.png`));
  assertAsset("public/assets/jobs/beginner/beginner-clean.png");
  assertAsset("public/assets/jobs/special/cygnus-clean.png");
});

test("wiki is a live WZ and MySQL server-data explorer",()=>{
  assert.match(wiki,/EVERLEAF DATA WIKI/);
  assert.match(wiki,/WORLD<br>DATA/);
  assert.match(wiki,/WZ \+ MySQL/);
  assert.match(wiki,/wikiCatalogGrid/);
  assert.match(wiki,/\/wiki\/guides/);
  assert.doesNotMatch(wiki,/EVERLEAF PLAYER WIKI/);
});

test("rankings keep live saved character avatars and class fallback art",()=>{
  assert.match(rankings,/rankingPodium/);
  assert.match(rankings,/rankingTableV2/);
  assert.match(rankings,/rankPlayerIcon/);
  assert.match(rankings,/rankingJobBadge/);
  assert.match(rankings,/\/character-avatar\//);
  assert.match(rankings,/data-live-avatar/);
  assert.match(rankings,/rankingCharacterAvatar/);
  assert.match(rankings,/\/assets\/jobs\/beginner\/beginner-clean\.png/);
  assert.match(rankings,/\/assets\/jobs\/special\/cygnus-clean\.png/);
  for(const asset of ["dawn-warrior","blaze-wizard","wind-archer","night-walker","thunder-breaker"]) assertAsset(`public/assets/jobs/cygnus/${asset}.png`);
});

test("account portal keeps character and security integrations under the new layout",()=>{
  assert.match(account,/terminalAccountPage/);
  assert.match(account,/characterCards/);
  assert.match(account,/characterJobIcon/);
  assert.match(account,/\/account\/password/);
  assert.match(account,/\/account\/discord\/connect/);
});

test("downloads and help are structurally rebuilt rather than icon-card skins",()=>{
  assert.match(downloads,/terminalDeployPage/);
  assert.match(downloads,/terminalDeployGrid/);
  assert.match(downloads,/terminalManifest/);
  assert.match(help,/terminalHelpPage/);
  assert.match(help,/terminalHelpGrid/);
  assert.match(help,/terminalHelpModule/);
});

test("terminal styles cover public pages, authentication, CMS and mobile layouts",()=>{
  for (const token of [".terminalHero",".terminalLogPage",".terminalDeployPage",".terminalAuthPage",".terminalAccountPage",".adminShell",".cmsManagerNav",".cmsWorkspace","@media(max-width:720px)","prefers-reduced-motion"]) assert.ok(terminal.includes(token),`missing ${token}`);
  assert.match(finish,/terminalArticlePage/);
  assert.match(finish,/terminalErrorPage/);
  assert.match(finish,/wikiEditorBodyGrid/);
});
