const test = require("node:test");
const assert = require("node:assert/strict");
const jobName = require("../src/utils/jobs");

test("rankings display names for advanced Cygnus, Aran, and Evan jobs", () => {
  assert.equal(jobName(1110), "Dawn Warrior");
  assert.equal(jobName(1310), "Wind Archer");
  assert.equal(jobName(1412), "Night Walker");
  assert.equal(jobName(1512), "Thunder Breaker");
  assert.equal(jobName(2112), "Aran");
  assert.equal(jobName(2218), "Evan");
});

test("unknown job ids remain visibly identifiable", () => {
  assert.equal(jobName(9999), "Job 9999");
});
