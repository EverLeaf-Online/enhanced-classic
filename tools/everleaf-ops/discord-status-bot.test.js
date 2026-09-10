const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const {
  StabilityGate,
  buildComponents,
  buildEmbed,
  normalizeApiStatus,
} = require("./discord-status-bot");

function status(overrides = {}) {
  return {
    statusApiOnline: true,
    loginOnline: true,
    databaseOnline: true,
    onlineChannels: 20,
    totalChannels: 20,
    players: 0,
    ...overrides,
  };
}

test("uses the API channel total instead of a hardcoded eight-channel list", () => {
  const normalized = normalizeApiStatus({
    channels: 20,
    totalChannels: 20,
    databaseOnline: true,
    players: 3,
  }, true);
  const embed = buildEmbed(normalized);
  const channelField = embed.fields.find((field) => field.name === "Channels");
  assert.equal(channelField.value, "**20/20 Online**");
});

test("requires three matching health checks before accepting an outage", () => {
  const gate = new StabilityGate(3);
  const healthy = status();
  const offline = status({
    statusApiOnline: false,
    loginOnline: false,
    databaseOnline: false,
    onlineChannels: 0,
  });

  assert.equal(gate.observe(healthy).onlineChannels, 20);
  assert.equal(gate.observe(offline).onlineChannels, 20);
  assert.equal(gate.observe(offline).onlineChannels, 20);
  assert.equal(gate.observe(offline).onlineChannels, 0);
});

test("a recovered check cancels a pending outage", () => {
  const gate = new StabilityGate(3);
  gate.observe(status());
  gate.observe(status({ loginOnline: false, onlineChannels: 0 }));
  assert.equal(gate.observe(status({ players: 2 })).onlineChannels, 20);
  assert.equal(gate.observe(status({ loginOnline: false, onlineChannels: 0 })).onlineChannels, 20);
});

test("updates the existing Discord message without creating alert posts", () => {
  const source = fs.readFileSync(require.resolve("./discord-status-bot"), "utf8");
  assert.doesNotMatch(source, /method:\s*["']POST["']/);
  assert.match(source, /method:\s*["']PATCH["']/);
});

test("adds safe official navigation buttons to the status post", () => {
  const components = buildComponents()[0].components;
  assert.deepEqual(components.map((button) => button.label), ["Website", "Download", "Account", "Vote"]);
  assert.ok(components.every((button) => button.style === 5 && button.url.startsWith("https://everleafms.online")));
});

test("status fetch retries transient failures and parses the successful body", async () => {
  const {readStatus}=require("./discord-status-bot");
  let attempts=0;
  const result=await readStatus("http://localhost/status",async()=>{
    if(++attempts===1)throw new Error("transient timeout");
    return {ok:true,json:async()=>({channels:20})};
  });
  assert.equal(attempts,2);
  assert.equal(result.channels,20);
});
