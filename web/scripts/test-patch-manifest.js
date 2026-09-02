#!/usr/bin/env node
const fs = require("fs");
const os = require("os");
const path = require("path");
const {spawnSync} = require("child_process");

const generator = path.resolve(__dirname, "build-patch-manifest.js");

function runCase(name, managedFiles, payload, shouldPass, launcher = null) {
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
  const portable = path.join(root, "downloads", "EverLeafLauncher-portable.zip");
  const launcherVersion = path.join(root, "downloads", "EverLeafLauncher-version.txt");
  if (launcher) {
    fs.mkdirSync(path.dirname(portable), {recursive: true});
    if (launcher.archive !== undefined) fs.writeFileSync(portable, launcher.archive);
    if (launcher.version !== undefined) fs.writeFileSync(launcherVersion, launcher.version);
  }
  const manifest = path.join(root, "manifest.json");
  const result = spawnSync(process.execPath, [generator, "test"], {
    encoding: "utf8",
    env: {...process.env, LAUNCHER_PATCH_ROOT: root, LAUNCHER_BASELINE_PATH: baseline,
      LAUNCHER_MANIFEST_PATH: manifest, LAUNCHER_PORTABLE_PATH: portable,
      LAUNCHER_VERSION_PATH: launcherVersion}
  });
  if ((result.status === 0) !== shouldPass) {
    fs.rmSync(root, {recursive: true, force: true});
    throw new Error(`${name}: expected pass=${shouldPass}, exit=${result.status}\n${result.stdout}\n${result.stderr}`);
  }
  if (shouldPass && launcher) {
    const output = JSON.parse(fs.readFileSync(manifest, "utf8"));
    if (output.launcher?.version !== launcher.version
        || output.launcher?.url !== "/launcher/download"
        || !/^[a-f0-9]{64}$/.test(output.launcher?.sha256 || "")
        || output.launcher?.size !== Buffer.byteLength(launcher.archive))
      throw new Error(`${name}: signed launcher metadata was not generated correctly`);
  }
  fs.rmSync(root, {recursive: true, force: true});
}

runCase("valid", [{path: "Data/a.bin", redistributable: true}], {"Data/a.bin": "data"}, true);
runCase("valid-launcher", [{path: "a.bin", redistributable: true}], {"a.bin": "data"}, true,
  {archive: "portable launcher", version: "0123456789abcdef0123456789abcdef01234567"});
runCase("missing-launcher-version", [{path: "a.bin", redistributable: true}], {"a.bin": "data"}, false,
  {archive: "portable launcher"});
runCase("unsafe-launcher-version", [{path: "a.bin", redistributable: true}], {"a.bin": "data"}, false,
  {archive: "portable launcher", version: "bad version/../../"});
runCase("empty", [], {}, false);
runCase("traversal", [{path: "../a.bin", redistributable: true}], {"a.bin": "data"}, false);
runCase("duplicate-case", [
  {path: "Data/a.bin", redistributable: true},
  {path: "data/A.bin", redistributable: true}
], {"Data/a.bin": "data"}, false);
runCase("extra", [{path: "a.bin", redistributable: true}], {"a.bin": "data", "extra.bin": "extra"}, false);
runCase("not-approved", [{path: "a.bin", redistributable: false}], {"a.bin": "data"}, false);
console.log("Patch manifest invariant tests passed.");
