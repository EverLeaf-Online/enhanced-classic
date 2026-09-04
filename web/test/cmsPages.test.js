const assert = require("node:assert/strict");
const path = require("node:path");
const test = require("node:test");
const ejs = require("ejs");

const common = {
  brand: {name:"EverLeaf",discordUrl:"https://discord.gg/test",description:"test",siteUrl:"https://everleafms.online"},
  currentPath:"/rules",
  player:null,
  settings:{footer_note:"test"},
  year:2026,
  metaDescription:"test",
  canonicalUrl:"https://everleafms.online/rules"
};

test("public CMS page renders managed content safely", async () => {
  const html = await ejs.renderFile(path.join(__dirname,"../src/views/page.ejs"),{
    ...common,
    page:{title:"Server Rules",body:"First rule.\n\nSecond rule."}
  });
  assert.match(html,/Server Rules/);
  assert.match(html,/First rule\./);
  assert.match(html,/Second rule\./);
});

test("admin page manager exposes create and edit controls", async () => {
  const html = await ejs.renderFile(path.join(__dirname,"../src/views/admin-pages.ejs"),{
    ...common,
    currentPath:"/admin/pages",
    pages:[{id:1,slug:"terms",title:"Terms",published:1,updated_at:"2026-08-31"}]
  });
  assert.match(html,/Create Page/);
  assert.match(html,/\/admin\/pages\/1\/edit/);
  assert.match(html,/href="\/terms"/);
});
