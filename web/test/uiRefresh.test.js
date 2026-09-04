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
const final = read("public/css/maple-final.css");
const rankingsCss = read("public/css/rankings-remaster.css");
const wikiDataCss = read("public/css/wiki-data.css");
const uiux = read("public/css/uiux-2026.css");
const refero = read("public/css/refero-everleaf-2026.css");
const unified = read("public/css/unified-terminal-2026.css");
const innerClean = read("public/css/inner-app-clean-2026.css");

test("global shell has no top navigation or utility ribbon",()=>{
  for(const sheet of [
    "maple-remaster.css","maple-remaster-pages.css","maple-final.css",
    "rankings-remaster.css","rankings-live.css","wiki-remaster.css",
    "wiki-cms.css","wiki-player-2026.css","wiki-data.css","uiux-2026.css",
    "refero-everleaf-2026.css?v=3","unified-terminal-2026.css?v=1","inner-app-clean-2026.css?v=1"
  ]) assert.ok(header.includes(sheet),`header should load ${sheet}`);
  assert.match(header,/maple-remaster-admin\.css/);
  assert.match(header,/siteBanner/);
  assert.doesNotMatch(header,/mobileMenu|terminalRibbon|terminalNav|worldRibbon/);
  assert.match(header,/body class="siteRoute route-<%=routeKey%>/);
  assert.match(header,/class="skipLink" href="#main-content"/);
  assert.match(header,/id="main-content"/);
  assert.doesNotMatch(header,/{href:"\/wiki",label:"WIKI",index:"05"}/);
  assert.doesNotMatch(header,/game-portal-2026\.css|full-site-portal-2026\.css|visuals-2026\.css/);
});

test("shared footer partial closes the document without rendering a footer",()=>{
  assert.match(footer,/<\/body>/);
  assert.match(footer,/<\/html>/);
  assert.doesNotMatch(footer,/<footer|siteFooter|terminalFooter|terminalFooterGrid/);
  assert.doesNotMatch(footer,/\/downloads|\/rankings|\/wiki|\/help|\/login/);
});

test("homepage stops after the five-tile signal strip",()=>{
  for(const token of ["terminalHero","everleafArtifact","heroTelemetry","signalStrip"]) {
    assert.ok(home.includes(token),`homepage should include ${token}`);
  }
  for(const token of ["terminalHome","dossierSection","entrySection","dataSection","finalTransmission","topCharacters"]) {
    assert.ok(!home.includes(token),`homepage should not include removed ${token}`);
  }

  assert.doesNotMatch(home,/classSection|classMatrix|CHOOSE YOUR SIGNAL/i);
  assert.doesNotMatch(home,/wikiSignalSection|KNOW THE WORLD/i);
  assert.match(home,/hero-left\.webp/);
  assert.match(home,/hero-right\.webp/);
  assert.match(home,/id="live-dot"/);
  assert.match(home,/id="live-state-label"/);
  assert.match(home,/id="live-status"/);
  assert.match(home,/id="live-players"/);
  assert.match(home,/id="live-channels"/);
  assert.match(home,/id="live-refresh"/);
  assert.match(remaster,/hero-forest\.webp/);
  assert.match(home,/href="\/wiki"/);
  assert.match(home,/href="\/rankings"/);
  assert.match(home,/href="\/downloads"/);
});

test("terminal redesign uses one dark compact visual contract across routes",()=>{
  assert.match(refero,/--terminal-bg:#12130f/);
  assert.match(refero,/--terminal-text:#e4dfda/);
  assert.match(unified,/body\.siteRoute/);
  assert.match(unified,/body\.siteRoute:not\(\.route-home\) \.lightTitle/);
  assert.match(unified,/Kill every legacy scallop\/ribbon\/cloud decoration/);
  assert.match(unified,/\.nav::after/);
  assert.match(unified,/body\.route-news \.newsList/);
  assert.match(unified,/body\.route-downloads \.contentGrid/);
  assert.match(unified,/body\.route-rankings \.rankingStats/);
  assert.match(unified,/body\.route-wiki \.wikiShell/);
  assert.match(unified,/@media\(max-width:960px\)/);
  assert.match(unified,/@media\(max-width:640px\)/);
  assert.doesNotMatch(unified,/@import|https?:\/\//i);
});

test("inner public pages use the final app-clean layer",()=>{
  assert.match(innerClean,/body\.siteRoute:not\(\.route-home\):not\(\.route-admin\)/);
  assert.match(innerClean,/Compact the old marketing-style hero treatment/);
  assert.match(innerClean,/\.pageHeroVisual/);
  assert.match(innerClean,/display:none!important/);
  assert.match(innerClean,/body\.route-news \.newsStory/);
  assert.match(innerClean,/body\.route-downloads \.contentGrid/);
  assert.match(innerClean,/body\.route-rankings \.rankingPodium/);
  assert.match(innerClean,/body\.route-wiki \.wikiCatalogGrid/);
  assert.match(innerClean,/body\.route-login \.authGrid/);
  assert.match(innerClean,/body\.siteRoute \.siteFooter/);
  assert.doesNotMatch(innerClean,/@import|https?:\/\//i);
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

test("rankings preserve live saved character avatars",()=>{
  assert.match(rankings,/rankingPodium/);
  assert.match(rankings,/rankingTableV2/);
  assert.match(rankings,/rankPlayerIcon/);
  assert.match(rankings,/\/character-avatar\//);
  assert.match(rankings,/Live saved appearance/);
  assert.match(rankings,/rankingCharacterAvatar/);
  assert.match(rankingsCss,/\.rankingCharacterAvatar/);
});

test("account portal keeps working product surfaces",()=>{
  assert.match(account,/characterCards/);
  assert.match(account,/characterJobIcon/);
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

test("legacy functional CSS remains available beneath the unified shell",()=>{
  for (const token of [".lightPage",".pageHeroGrid",".newsList",".authWrap","@media(max-width:820px)"]) assert.match(remaster,new RegExp(token.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")));
  assert.match(pages,/\.accountShell/);
  assert.match(admin,/\.cmsManagerNav/);
  assert.match(admin,/\.cmsWorkspace/);
  assert.match(final,/\.rankingBoard/);
  assert.match(final,/\.characterCards/);
  for (const token of [".skipLink",":focus-visible","prefers-reduced-motion"]) {
    assert.match(uiux,new RegExp(token.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")));
  }
});
