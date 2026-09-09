const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const root=path.join(__dirname,'..');
const read=file=>fs.readFileSync(path.join(root,file),'utf8');
const exists=file=>fs.existsSync(path.join(root,file));

test('shared shell keeps local artwork but no longer loads the legacy visual skin',()=>{
  const header=read('src/views/partials/header.ejs');
  assert.doesNotMatch(header,/visuals-2026\.css/);
  assert.match(header,/refero-everleaf-2026\.css\?v=3/);
  assert.match(header,/unified-terminal-2026\.css\?v=1/);
  assert.match(header,/hero-left\.webp/);
  assert.match(header,/hero-right\.webp/);
  assert.match(header,/og:image[^\n]*hero-forest\.webp/);
  assert.match(header,/twitter:image[^\n]*hero-forest\.webp/);
});

test('visual art assets remain bundled for route content',()=>{
  for(const file of [
    'public/assets/visuals/hero-magic-overlay.svg',
    'public/assets/visuals/downloads-workshop.svg',
    'public/assets/visuals/help-guilddesk.svg',
    'public/assets/hero-left.webp',
    'public/assets/hero-right.webp',
    'public/assets/hero-forest.webp'
  ]) assert.ok(exists(file),`${file} should exist`);
});

test('downloads and help retain their local illustrations inside the unified shell',()=>{
  const downloads=read('src/views/downloads.ejs');
  const help=read('src/views/help.ejs');
  const css=read('public/css/unified-terminal-2026.css');
  assert.match(downloads,/downloads-workshop\.svg/);
  assert.match(help,/help-guilddesk\.svg/);
  assert.match(css,/\.pageHeroVisual/);
  assert.match(css,/body\.route-downloads/);
  assert.match(css,/body\.route-help/);
});
