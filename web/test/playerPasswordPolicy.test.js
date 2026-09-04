const test = require("node:test");
const assert = require("node:assert/strict");
const policy = require("../src/utils/playerPasswordPolicy");

const registration = password => ({
  username: "Player_1",
  email: "player@example.invalid",
  password,
  confirmPassword: password,
  agree: "yes"
});

test("registration accepts the inclusive 8-12 character range", () => {
  assert.equal(policy.registrationSchema.safeParse(registration("12345678")).success, true);
  assert.equal(policy.registrationSchema.safeParse(registration("123456789012")).success, true);
});

test("registration rejects passwords outside the game-client-compatible range", () => {
  assert.equal(policy.registrationSchema.safeParse(registration("1234567")).success, false);
  assert.equal(policy.registrationSchema.safeParse(registration("1234567890123")).success, false);
});

test("password changes enforce 8-12 only for the new password", () => {
  const result = policy.passwordChangeSchema.safeParse({
    currentPassword: "an-existing-password-longer-than-twelve",
    newPassword: "123456789012",
    confirmPassword: "123456789012"
  });
  assert.equal(result.success, true);
});

test("login continues accepting existing longer passwords", () => {
  assert.equal(policy.loginPassword.safeParse("an-existing-password-longer-than-twelve").success, true);
});

test("confirmation must match for registration and password changes", () => {
  assert.equal(policy.registrationSchema.safeParse({...registration("12345678"), confirmPassword:"87654321"}).success, false);
  assert.equal(policy.passwordChangeSchema.safeParse({currentPassword:"existing",newPassword:"12345678",confirmPassword:"87654321"}).success, false);
});
