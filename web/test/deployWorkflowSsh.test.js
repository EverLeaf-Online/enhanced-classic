const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const workflow = fs.readFileSync(path.join(__dirname, '..', '..', '.github', 'workflows', 'deploy-web.yml'), 'utf8');

test('web deploy retries SSH host-key discovery before failing', () => {
  assert.match(workflow, /for attempt in 1 2 3 4 5 6/);
  assert.match(workflow, /ssh-keyscan -T 15 -H/);
  assert.match(workflow, /Unable to discover SSH host key/);
  assert.match(workflow, /sleep 5/);
});
