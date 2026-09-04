const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');

const publicViews = [
  '404.ejs','500.ejs','account.ejs','downloads.ejs','help.ejs','home.ejs','login.ejs',
  'news.ejs','page.ejs','post.ejs','rankings.ejs','recover.ejs','register.ejs','terms.ejs','wiki.ejs'
];

test('all core public views use the shared header while the homepage intentionally ends at the signal strip', () => {
  for (const file of publicViews) {
    const source = read(`src/views/${file}`);
    assert.match(source, /include\("partials\/header"/i, `${file} should use shared portal header`);
    if (file === 'home.ejs') {
      assert.doesNotMatch(source, /include\("partials\/footer"/i, 'home.ejs should not render the shared footer');
    } else {
      assert.match(source, /include\("partials\/footer"/i, `${file} should use shared portal footer`);
    }
  }
});

test('full-site portal client derives a deterministic class from the first route segment', () => {
  const siteJs = read('public/js/site.js');
  assert.match(siteJs, /window\.location\.pathname/);
  assert.match(siteJs, /split\('\/'\)\.filter\(Boolean\)\[0\]/);
  assert.match(siteJs, /replace\(\/\[\^a-z0-9-\]\//);
});
