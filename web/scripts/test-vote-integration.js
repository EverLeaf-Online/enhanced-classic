const assert = require("assert");

process.env.GTOP100_PINGBACK_KEY = "ci-secret";
process.env.GTOP100_VOTE_URL = "https://gtop100.com/MapleStory/server-106444?vote=1";
process.env.VOTE_NX_REWARD = "1500";

const env = require("../src/config/env");
const vote = require("../src/routes/vote")._test;

assert.strictEqual(vote.secretEqual("ci-secret", "ci-secret"), true);
assert.strictEqual(vote.secretEqual("wrong", "ci-secret"), false);
assert.strictEqual(vote.secretEqual("", "ci-secret"), false);

const form = vote.parsePingback({
  pingbackkey: "ci-secret",
  VoterIP: "203.0.113.5",
  Successful: "0",
  Reason: "Successful vote",
  pingUsername: "Alpha_1"
});
assert.strictEqual(form.key, "ci-secret");
assert.strictEqual(form.votes.length, 1);
assert.deepStrictEqual(form.votes[0], {
  username: "Alpha_1",
  voterIp: "203.0.113.5",
  success: 0,
  reason: "Successful vote"
});

const batch = vote.parsePingback({
  pingbackkey: "ci-secret",
  Common: [[
    { ip: "2001:db8::1" },
    { success: "0" },
    { reason: "ok" },
    { pb_name: "Beta_2" }
  ]]
});
assert.strictEqual(batch.votes.length, 1);
assert.strictEqual(batch.votes[0].username, "Beta_2");
assert.strictEqual(batch.votes[0].voterIp, "2001:db8::1");
assert.strictEqual(batch.votes[0].success, 0);

const failed = vote.parsePingback({
  pingbackkey: "ci-secret",
  Successful: "1",
  pingUsername: "Alpha_1"
});
assert.strictEqual(failed.votes[0].success, 1);

const url = new URL(vote.verifiedVoteUrl("Alpha_1"));
assert.strictEqual(url.protocol, "https:");
assert.strictEqual(url.hostname, "gtop100.com");
assert.strictEqual(url.searchParams.get("vote"), "1");
assert.strictEqual(url.searchParams.get("pingUsername"), "Alpha_1");

const originalUrl = env.vote.gtopVoteUrl;
env.vote.gtopVoteUrl = "https://example.com/not-allowed";
assert.throws(() => vote.verifiedVoteUrl("Alpha_1"), /gtop100\.com/);
env.vote.gtopVoteUrl = originalUrl;

assert.strictEqual(env.vote.rewardNx, 1500);
console.log("EverLeaf NX vote web integration tests passed.");
