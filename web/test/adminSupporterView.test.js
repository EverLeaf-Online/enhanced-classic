const assert = require("node:assert/strict");
const path = require("node:path");
const test = require("node:test");
const ejs = require("ejs");

test("supporter management renders payment filters without Discord identifiers", async () => {
  const html = await ejs.renderFile(path.join(__dirname, "../src/views/admin-supporters.ejs"), {
    payments: { rows: [{ id: "safe-order", game_account_name: "Leaf", provider: "stripe", status: "paid", amount_cents: 1000, refunded_cents: 0, created_at: "today" }], total: 1, page: 1, pages: 1 },
    supporters: [{ game_account_id: 1, game_account_name: "Leaf", lifetime_cents: 1000, discord_linked: 1, discord_role_status: "assigned" }],
    summary: { confirmedCents: 1000, paidCount: 1, pendingCount: 0, failedCount: 0 },
    filters: { search: "", provider: "", status: "", roleStatus: "" },
    syncStatus: "",
    brand: { name: "EverLeaf", discordUrl: "https://discord.gg/w9ED8vtxa7" },
    settings: { footer_note: "test" },
    currentPath: "/admin/supporters",
    player: null
  });

  assert.match(html, /Supporter Management/);
  assert.match(html, /safe-order/);
  assert.match(html, /Retry Role|No action needed/);
  assert.doesNotMatch(html, /123456789012345678/);
});
