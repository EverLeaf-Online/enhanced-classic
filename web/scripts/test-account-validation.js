const assert = require("assert");
const fs = require("fs");
const path = require("path");
const validation = require("../src/utils/accountValidation");

assert.strictEqual(validation.isGameCompatiblePassword("1234567"), false);
assert.strictEqual(validation.isGameCompatiblePassword("12345678"), true);
assert.strictEqual(validation.isGameCompatiblePassword("123456789012"), true);
assert.strictEqual(validation.isGameCompatiblePassword("1234567890123"), false);

for (const view of ["login.ejs", "register.ejs", "account.ejs"]) {
  const source = fs.readFileSync(path.join(__dirname, "..", "src", "views", view), "utf8");
  assert.match(source, /minlength="8"/);
  assert.match(source, /maxlength="12"/);
}

console.log("EverLeaf 8-12 character password validation tests passed.");
