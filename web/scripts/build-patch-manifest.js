#!/usr/bin/env node
const fs = require("fs");
const fsp = require("fs/promises");
const path = require("path");
const crypto = require("crypto");

const patchRoot = path.resolve(process.env.LAUNCHER_PATCH_ROOT || "/opt/everleaf/patches");
const filesRoot = path.join(patchRoot, "files");
const baselinePath = path.resolve(process.env.LAUNCHER_BASELINE_PATH || path.join(patchRoot, "managed-client-baseline.json"));
const manifestPath = path.resolve(process.env.LAUNCHER_MANIFEST_PATH || path.join(patchRoot, "manifest.json"));
const version = process.argv[2] || process.env.PATCH_VERSION || new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 14);
const SHA256 = /^[a-f0-9]{64}$/;

function safeRelative(value, label) {
  if (typeof value !== "string" || !value || value.includes("\\") || path.posix.isAbsolute(value))
    throw new Error(`Unsafe ${label}: ${value}`);
  const parts = value.split("/");
  if (parts.some(part => !part || part === "." || part === ".."))
    throw new Error(`Unsafe ${label}: ${value}`);
  return parts.join("/");
}

async function sha256(file) {
  const hash = crypto.createHash("sha256");
  const stream = fs.createReadStream(file, {highWaterMark: 1024 * 1024});
  for await (const chunk of stream) hash.update(chunk);
  return hash.digest("hex");
}

async function walk(dir) {
  const out = [];
  for (const entry of await fsp.readdir(dir, {withFileTypes: true})) {
    const full = path.join(dir, entry.name);
    if (entry.isSymbolicLink()) throw new Error(`Symbolic links are not allowed in patch payload: ${full}`);
    if (entry.isDirectory()) out.push(...await walk(full));
    else if (entry.isFile()) out.push(full);
  }
  return out;
}

async function main() {
  const baseline = JSON.parse(await fsp.readFile(baselinePath, "utf8"));
  if (baseline.schemaVersion !== 1 || !Array.isArray(baseline.managedFiles) || baseline.managedFiles.length === 0)
    throw new Error("Managed-client baseline is empty or unsupported.");

  const allowed = new Map();
  for (const entry of baseline.managedFiles) {
    const relative = safeRelative(entry.path, "managed path");
    const key = relative.toLowerCase();
    if (allowed.has(key)) throw new Error(`Duplicate case-insensitive managed path: ${relative}`);
    if (entry.redistributable !== true) throw new Error(`Managed file lacks distribution approval: ${relative}`);
    allowed.set(key, relative);
  }

  const discovered = await walk(filesRoot);
  if (discovered.length === 0) throw new Error("Patch payload is empty.");
  const found = new Set();
  const files = [];
  for (const full of discovered.sort((a, b) => a.localeCompare(b))) {
    const relative = safeRelative(path.relative(filesRoot, full).split(path.sep).join("/"), "patch path");
    const key = relative.toLowerCase();
    if (!allowed.has(key)) throw new Error(`Patch payload contains a file outside the managed baseline: ${relative}`);
    if (found.has(key)) throw new Error(`Duplicate case-insensitive patch path: ${relative}`);
    found.add(key);
    const stat = await fsp.stat(full);
    if (!Number.isSafeInteger(stat.size) || stat.size <= 0) throw new Error(`Invalid patch size: ${relative}`);
    const digest = await sha256(full);
    if (!SHA256.test(digest)) throw new Error(`Malformed SHA-256 for ${relative}`);
    files.push({
      path: allowed.get(key),
      url: "/patches/" + allowed.get(key).split("/").map(encodeURIComponent).join("/"),
      sha256: digest,
      size: stat.size
    });
  }

  const missing = [...allowed].filter(([key]) => !found.has(key)).map(([, value]) => value);
  if (missing.length) throw new Error(`Patch payload is missing managed files: ${missing.join(", ")}`);
  if (!version || typeof version !== "string") throw new Error("Patch version is invalid.");

  const manifest = {version, files};
  const tmp = manifestPath + ".new";
  await fsp.mkdir(path.dirname(manifestPath), {recursive: true});
  await fsp.writeFile(tmp, JSON.stringify(manifest, null, 2) + "\n", {encoding: "utf8", mode: 0o644});
  await fsp.rename(tmp, manifestPath);
  console.log(`Published EverLeaf patch manifest ${version}: ${files.length}/${allowed.size} managed files`);
}

main().catch(error => { console.error(error.stack || error); process.exitCode = 1; });
