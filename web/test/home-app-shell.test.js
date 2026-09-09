const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const home = fs.readFileSync(path.join(root, 'src/views/home.ejs'), 'utf8');
const css = fs.readFileSync(path.join(root, 'public/css/home-app-shell-2026.css'), 'utf8');

test('homepage loads the dedicated app shell stylesheet', () => {
  assert.match(home, /home-app-shell-2026\.css/);
});

test('homepage app shell is fixed to the viewport and non-scrolling', () => {
  assert.match(css, /body\.route-home[\s\S]*height:100dvh/);
  assert.match(css, /body\.route-home[\s\S]*overflow:hidden!important/);
  assert.match(css, /\.route-home \.siteContent[\s\S]*grid-template-rows:minmax\(0,1fr\) auto/);
});

test('homepage app shell preserves responsive compact layouts', () => {
  assert.match(css, /@media \(max-width:900px\)/);
  assert.match(css, /@media \(max-width:620px\)/);
  assert.match(css, /@media \(max-height:560px\)/);
});
