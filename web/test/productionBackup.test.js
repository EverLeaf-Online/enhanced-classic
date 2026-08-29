const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");

const webRoot = path.resolve(__dirname, "..");
const read = relative => fs.readFileSync(path.join(webRoot, relative), "utf8");

test("production backup covers CMS, MySQL, checksums, and retention", () => {
  const script = read("scripts/backup-production.sh");
  assert.match(script, /backup-cms\.js/);
  assert.match(script, /backup-mysql\.js/);
  assert.match(script, /gzip -t/);
  assert.match(script, /sha256sum/);
  assert.match(script, /-mtime \+14/);
  assert.match(script, /umask 077/);
});

test("database credentials stay out of mysqldump command arguments", () => {
  const script = read("scripts/backup-mysql.js");
  assert.match(script, /MYSQL_PWD/);
  assert.doesNotMatch(script, /--password=/);
  assert.match(script, /--single-transaction/);
});

test("daily backup timer is persistent", () => {
  const timer = read("ops/everleaf-backup.timer");
  assert.match(timer, /OnCalendar=\*-\*-\* 06:15:00 UTC/);
  assert.match(timer, /Persistent=true/);
});
