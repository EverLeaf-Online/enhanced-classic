const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");

const server = fs.readFileSync(path.join(__dirname,"../src/server.js"),"utf8");

test("production web server does not allow default session secret", () => {
  assert.match(server,/SESSION_SECRET must be configured in production/);
  assert.match(server,/app\.disable\("x-powered-by"\)/);
});

test("web server enables a restrictive CSP", () => {
  assert.match(server,/contentSecurityPolicy/);
  assert.match(server,/frameAncestors:\["'none'"\]/);
  assert.match(server,/objectSrc:\["'none'"\]/);
  assert.match(server,/formAction:\["'self'"\]/);
});
