#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
require("dotenv").config({path:path.resolve(__dirname,"../.env")});

const patchRoot = path.resolve(process.env.LAUNCHER_PATCH_ROOT || "/opt/everleaf/patches");
const filesRoot = path.join(patchRoot, "files");
const manifestPath = path.resolve(process.env.LAUNCHER_MANIFEST_PATH || path.join(patchRoot, "manifest.json"));
const version = process.argv[2] || process.env.PATCH_VERSION || new Date().toISOString().replace(/[-:TZ.]/g,"").slice(0,14);

function walk(dir) {
  if (!fs.existsSync(dir)) return [];
  const out=[];
  for (const entry of fs.readdirSync(dir,{withFileTypes:true})) {
    const full=path.join(dir,entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else if (entry.isFile()) out.push(full);
  }
  return out;
}

function sha256(file) {
  const hash=crypto.createHash("sha256");
  hash.update(fs.readFileSync(file));
  return hash.digest("hex");
}

fs.mkdirSync(filesRoot,{recursive:true});
const files=walk(filesRoot).sort((a,b)=>a.localeCompare(b)).map(full=>{
  const relative=path.relative(filesRoot,full).split(path.sep).join("/");
  if (!relative || relative.startsWith("../") || path.isAbsolute(relative))
    throw new Error(`Unsafe patch path: ${relative}`);
  return {
    path:relative,
    url:"/patches/"+relative.split("/").map(encodeURIComponent).join("/"),
    sha256:sha256(full),
    size:fs.statSync(full).size
  };
});

const manifest={version,files};
const tmp=manifestPath+".new";
fs.mkdirSync(path.dirname(manifestPath),{recursive:true});
fs.writeFileSync(tmp,JSON.stringify(manifest,null,2)+"\n",{encoding:"utf8",mode:0o644});
fs.renameSync(tmp,manifestPath);
console.log(`Published EverLeaf patch manifest ${version}: ${files.length} files`);
console.log(manifestPath);
