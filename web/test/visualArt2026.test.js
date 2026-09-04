const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const root=path.join(__dirname,'..');
const read=file=>fs.readFileSync(path.join(root,file),'utf8');
const exists=file=>fs.existsSync(path.join(root,file));

test('shared shell loads the dedicated visual-art layer',()=>{
  const header=read('src/views/partials/header.ejs');
  assert.match(header,/visuals-2026\.css/);
  assert.match(header,/hero-magic-overlay\.svg/);
  assert.match(header,/og:image[^\n]*hero-forest\.webp/);
  assert.match(header,/twitter:image[^\n]*hero-forest\.webp/);
});

test('visual art assets are bundled with the Oracle website',()=>{
  for(const file of [
    'public/assets/visuals/hero-magic-overlay.svg',
    'public/assets/visuals/downloads-workshop.svg',
    'public/assets/visuals/help-guilddesk.svg'
  ]) assert.ok(exists(file),`${file} should exist`);

  const hero=read('public/assets/visuals/hero-magic-overlay.svg');
  const downloads=read('public/assets/visuals/downloads-workshop.svg');
  const help=read('public/assets/visuals/help-guilddesk.svg');
  assert.match(hero,/portal/);
  assert.match(hero,/crystal/);
  assert.match(downloads,/launcher workshop/i);
  assert.match(help,/player help desk/i);
});

test('downloads and help use illustrated responsive mastheads',()=>{
  const downloads=read('src/views/downloads.ejs');
  const help=read('src/views/help.ejs');
  const css=read('public/css/visuals-2026.css');
  assert.match(downloads,/visualPageTitle/);
  assert.match(downloads,/downloads-workshop\.svg/);
  assert.match(help,/visualPageTitle/);
  assert.match(help,/help-guilddesk\.svg/);
  assert.match(css,/hero-magic-overlay\.svg/);
  assert.match(css,/\.pageHeroVisual/);
  assert.match(css,/@media \(max-width:760px\)/);
  assert.match(css,/prefers-reduced-motion/);
});
