const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const testDir = fs.mkdtempSync(path.join(os.tmpdir(), "everleaf-discord-"));
process.env.CMS_DB_PATH = path.join(testDir, "cms.sqlite");
process.env.DISCORD_ENABLED = "true";
process.env.DISCORD_CLIENT_ID = "123456789012345678";
process.env.DISCORD_CLIENT_SECRET = "test-client-secret";
process.env.DISCORD_BOT_TOKEN = "test-bot-token";
process.env.DISCORD_GUILD_ID = "223456789012345678";
process.env.DISCORD_SUPPORTER_ROLE_ID = "323456789012345678";
process.env.DISCORD_REDIRECT_URI = "https://example.invalid/account/discord/callback";

let db, supporter, discord, nativeReady = true;
try {
  ({ db, initCms } = require("../src/db/cms"));
  initCms();
  supporter = require("../src/services/supporterService");
  discord = require("../src/services/discordService");
} catch (error) {
  if (!String(error.message).includes("bindings file")) throw error;
  nativeReady = false;
}

const originalFetch = global.fetch;
test.after(() => {
  global.fetch = originalFetch;
  if (db) db.close();
  fs.rmSync(testDir, { recursive: true, force: true });
});

test("Discord OAuth URL uses identify scope, redirect URI, and CSRF state", { skip: !nativeReady }, () => {
  const state = discord.newState();
  const url = new URL(discord.authorizationUrl(state));
  assert.equal(url.origin, "https://discord.com");
  assert.equal(url.searchParams.get("scope"), "identify");
  assert.equal(url.searchParams.get("state"), state);
  assert.equal(url.searchParams.get("redirect_uri"), process.env.DISCORD_REDIRECT_URI);
});

test("Discord identities can only be linked to one game account", { skip: !nativeReady }, () => {
  supporter.linkDiscordAccount(41, "LeafOne", "423456789012345678");
  assert.throws(() => supporter.linkDiscordAccount(42, "LeafTwo", "423456789012345678"), /UNIQUE/);
});

test("eligible linked supporters receive the configured role", { skip: !nativeReady }, async () => {
  db.prepare(`INSERT INTO supporter_profiles(game_account_id,game_account_name,discord_user_id,lifetime_cents,discord_role_status)
    VALUES(43,'LeafSupporter','523456789012345678',1000,'linked')`).run();
  let request;
  global.fetch = async (url, options) => {
    request = { url, options };
    return { ok: true, status: 204, json: async () => null };
  };
  assert.equal(await discord.syncAccount(43), true);
  assert.match(request.url, /\/guilds\/223456789012345678\/members\/523456789012345678\/roles\/323456789012345678$/);
  assert.equal(request.options.method, "PUT");
  assert.equal(supporter.accountSummary(43).profile.discord_role_status, "assigned");
});

test("missing Discord membership is retained as a retryable status", { skip: !nativeReady }, async () => {
  db.prepare(`INSERT INTO supporter_profiles(game_account_id,game_account_name,discord_user_id,lifetime_cents,discord_role_status)
    VALUES(44,'LeafMissing','623456789012345678',500,'linked')`).run();
  global.fetch = async () => ({ ok: false, status: 404, json: async () => ({}) });
  assert.equal(await discord.syncAccount(44), false);
  assert.equal(supporter.accountSummary(44).profile.discord_role_status, "not_member");
});

test("ineligible linked accounts have the supporter role removed", { skip: !nativeReady }, async () => {
  db.prepare(`INSERT INTO supporter_profiles(game_account_id,game_account_name,discord_user_id,lifetime_cents,discord_role_status)
    VALUES(45,'LeafRefunded','723456789012345678',0,'assigned')`).run();
  let request;
  global.fetch = async (url, options) => {
    request = { url, options };
    return { ok: true, status: 204, json: async () => null };
  };
  assert.equal(await discord.syncAccount(45), true);
  assert.equal(request.options.method, "DELETE");
  assert.equal(supporter.accountSummary(45).profile.discord_role_status, "linked");
});
