const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const portal = read('public/css/full-site-portal-2026.css');
const siteJs = read('public/js/site.js');

const views = {
  news: read('src/views/news.ejs'),
  downloads: read('src/views/downloads.ejs'),
  rankings: read('src/views/rankings.ejs'),
  wiki: read('src/views/wiki.ejs'),
  help: read('src/views/help.ejs'),
  login: read('src/views/login.ejs'),
  register: read('src/views/register.ejs'),
  recover: read('src/views/recover.ejs'),
  account: read('src/views/account.ejs'),
  terms: read('src/views/terms.ejs'),
  page: read('src/views/page.ejs'),
  post: read('src/views/post.ejs'),
  notFound: read('src/views/404.ejs'),
  serverError: read('src/views/500.ejs')
};

test('full-site portal stylesheet is loaded on every route through the shared deferred client', () => {
  assert.match(siteJs, /full-site-portal-2026\.css\?v=1/);
  assert.match(siteJs, /site-\$\{routeSegment/);
  assert.match(siteJs, /document\.body\.classList\.add\(routeClass\)/);
  assert.match(siteJs, /data-everleaf-full-site-portal|everleafFullSitePortal/);
});

test('full-site portal covers every major public product surface', () => {
  for (const selector of [
    '.site-news .newsList',
    '.site-downloads .downloadCard',
    '.site-rankings .rankingPodiumCard',
    '.site-wiki .wikiDataHero',
    '.site-help .helpGrid',
    '.site-login .authWrap',
    '.site-register .authWrap',
    '.site-recover .authWrap',
    '.site-account .accountPage',
    '.site-404 .authWrap',
    '.site-500 .authWrap'
  ]) assert.ok(portal.includes(selector), `missing portal coverage for ${selector}`);

  assert.match(portal, /body\.innerRoute \.lightTitle/);
  assert.match(portal, /body\.innerRoute \.featurePanel/);
  assert.match(portal, /body\.innerRoute \.siteFooter/);
  assert.match(portal, /@media\(max-width:820px\)/);
  assert.match(portal, /prefers-reduced-motion/);
});

test('major routes retain their real functional page structures under the redesign', () => {
  assert.match(views.news, /newsList/);
  assert.match(views.downloads, /downloadCard/);
  assert.match(views.rankings, /rankingPodium/);
  assert.match(views.rankings, /data-live-avatar/);
  assert.match(views.wiki, /wikiDataHero/);
  assert.match(views.wiki, /wikiCatalogGrid/);
  assert.match(views.help, /helpGrid/);
  assert.match(views.login, /authWrap/);
  assert.match(views.register, /authWrap/);
  assert.match(views.recover, /authWrap/);
  assert.match(views.account, /accountPage/);
  assert.match(views.terms, /lightPage/);
  assert.match(views.page, /lightPage/);
  assert.match(views.post, /lightPage/);
  assert.match(views.notFound, /authWrap/);
  assert.match(views.serverError, /authWrap/);
});

test('the full-site redesign uses EverLeaf local art only', () => {
  assert.match(portal, /\/assets\/hero-forest\.webp/);
  assert.doesNotMatch(portal, /beyond-ms/i);
  assert.doesNotMatch(portal, /_next\//);
  assert.doesNotMatch(portal, /vercel/i);
  assert.doesNotMatch(portal, /https?:\/\//i);
});
