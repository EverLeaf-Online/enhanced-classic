#!/usr/bin/env node
const fs = require("fs");
const os = require("os");
const path = require("path");
const {spawnSync} = require("child_process");

const generator = path.resolve(__dirname, "build-patch-manifest.js");

function runCase(name, managedFiles, payload, shouldPass) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), `everleaf-${name}-`));
  const files = path.join(root, "files");
  fs.mkdirSync(files, {recursive: true});
  for (const [relative, contents] of Object.entries(payload)) {
    const target = path.join(files, relative);
    fs.mkdirSync(path.dirname(target), {recursive: true});
    fs.writeFileSync(target, contents);
  }
  const baseline = path.join(root, "baseline.json");
  fs.writeFileSync(baseline, JSON.stringify({schemaVersion: 1, managedFiles}));
  const result = spawnSync(process.execPath, [generator, "test"], {
    encoding: "utf8",
    env: {...process.env, LAUNCHER_PATCH_ROOT: root, LAUNCHER_BASELINE_PATH: baseline,
      LAUNCHER_MANIFEST_PATH: path.join(root, "manifest.json")}
  });
  fs.rmSync(root, {recursive: true, force: true});
  if ((result.status === 0) !== shouldPass)
    throw new Error(`${name}: expected pass=${shouldPass}, exit=${result.status}\n${result.stdout}\n${result.stderr}`);
}

runCase("valid", [{path: "Data/a.bin", redistributable: true}], {"Data/a.bin": "data"}, true);
runCase("empty", [], {}, false);
runCase("traversal", [{path: "../a.bin", redistributable: true}], {"a.bin": "data"}, false);
runCase("duplicate-case", [
  {path: "Data/a.bin", redistributable: true},
  {path: "data/A.bin", redistributable: true}
], {"Data/a.bin": "data"}, false);
runCase("extra", [{path: "a.bin", redistributable: true}], {"a.bin": "data", "extra.bin": "extra"}, false);
runCase("not-approved", [{path: "a.bin", redistributable: false}], {"a.bin": "data"}, false);
console.log("Patch manifest invariant tests passed.");
