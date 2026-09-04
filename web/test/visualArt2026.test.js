const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const root=path.join(__dirname,'..');
const read=file=>fs.readFileSync(path.join(root,file),'utf8');
const exists=file=>fs.existsSync(path.join(root,file));

test('shared shell loads the terminal visual system and social artwork metadata',()=>{
  const header=read('src/views/partials/header.ejs');
  assert.match(header,/terminal-everleaf-2026\.css/);
  assert.match(header,/terminal-everleaf-final-2026\.css/);
  assert.match(header,/og:image[^\n]*hero-forest\.webp/);
  assert.match(header,/twitter:image[^\n]*hero-forest\.webp/);
});

test('EverLeaf local visual assets remain bundled with the Oracle website',()=>{
  for(const file of [
    'public/assets/hero-left.webp',
    'public/assets/hero-right.webp',
    'public/assets/hero-forest.webp',
    'public/assets/everleaf-remaster.svg',
    'public/assets/visuals/hero-magic-overlay.svg',
    'public/assets/visuals/downloads-workshop.svg',
    'public/assets/visuals/help-guilddesk.svg'
  ]) assert.ok(exists(file),`${file} should exist`);
});

test('central homepage artifact uses local Maple-world art while utility pages become terminal layouts',()=>{
  const home=read('src/views/home.ejs');
  const downloads=read('src/views/downloads.ejs');
  const help=read('src/views/help.ejs');
  const css=read('public/css/terminal-everleaf-2026.css');
  assert.match(home,/terminalHeroArtifact/);
  assert.match(home,/hero-left\.webp/);
  assert.match(home,/hero-right\.webp/);
  assert.match(downloads,/terminalDeployPage/);
  assert.match(help,/terminalHelpPage/);
  assert.match(css,/\.terminalHeroArtifact/);
  assert.match(css,/@media\(max-width:720px\)/);
  assert.match(css,/prefers-reduced-motion/);
});
