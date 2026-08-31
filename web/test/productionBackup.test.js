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

test("production backup uses local admin socket without widening web DB privileges", () => {
  const script = read("scripts/backup-mysql.js");
  assert.match(script, /process\.getuid/);
  assert.match(script, /--protocol=socket/);
  assert.match(script, /--user=root/);
  assert.match(script, /local-root-socket/);
});

test("MySQL backup stays schema-neutral for isolated restore drills", () => {
  const script = read("scripts/backup-mysql.js");
  assert.doesNotMatch(script, /["']--databases["']/);
  assert.match(script, /values\.GAME_DB_NAME/);
});

test("daily backup timer is persistent", () => {
  const timer = read("ops/everleaf-backup.timer");
  assert.match(timer, /OnCalendar=\*-\*-\* 06:15:00 UTC/);
  assert.match(timer, /Persistent=true/);
});
