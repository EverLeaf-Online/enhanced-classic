const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const unified = read('public/css/unified-terminal-2026.css');
const siteJs = read('public/js/site.js');
const header = read('src/views/partials/header.ejs');

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

test('one unified terminal stylesheet is server-loaded on every route', () => {
  assert.match(header, /unified-terminal-2026\.css\?v=1/);
  assert.match(header, /body class="siteRoute route-<%=routeKey%>/);
  assert.match(siteJs, /site-\$\{routeSegment/);
  assert.match(siteJs, /document\.body\.classList\.add\(routeClass\)/);
  assert.doesNotMatch(siteJs, /full-site-portal-2026\.css/);
});

test('unified terminal shell covers every major public product surface', () => {
  for (const selector of [
    'body.route-news .newsList',
    'body.route-downloads .downloadCard',
    'body.route-rankings .rankingPodiumCard',
    'body.route-wiki .wikiShell',
    'body.route-help .helpGrid',
    'body.route-login .authWrap',
    'body.route-register .authWrap',
    'body.route-account .accountPage'
  ]) assert.ok(unified.includes(selector), `missing unified coverage for ${selector}`);

  assert.match(unified, /body\.siteRoute:not\(\.route-home\) \.lightTitle/);
  assert.match(unified, /body\.siteRoute \.featurePanel/);
  assert.match(unified, /body\.siteRoute \.siteFooter/);
  assert.match(unified, /@media\(max-width:960px\)/);
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

test('the unified redesign uses EverLeaf local art only', () => {
  assert.match(unified, /\/assets\/hero-forest\.webp/);
  assert.doesNotMatch(unified, /beyond-ms/i);
  assert.doesNotMatch(unified, /_next\//);
  assert.doesNotMatch(unified, /vercel/i);
  assert.doesNotMatch(unified, /https?:\/\//i);
});
