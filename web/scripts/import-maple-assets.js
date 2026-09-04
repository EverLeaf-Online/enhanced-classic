#!/usr/bin/env node
"use strict";

const fs=require("node:fs");
const path=require("node:path");
const crypto=require("node:crypto");

function fail(message){
  console.error(`EverLeaf asset import: ${message}`);
  process.exit(1);
}

const args=process.argv.slice(2);
const sourceFlag=args.indexOf("--source");
const manifestFlag=args.indexOf("--manifest");
const outFlag=args.indexOf("--out");
if(sourceFlag<0||!args[sourceFlag+1]) fail("missing --source <export-directory>");
if(manifestFlag<0||!args[manifestFlag+1]) fail("missing --manifest <selection.json>");

const sourceRoot=path.resolve(args[sourceFlag+1]);
const manifestPath=path.resolve(args[manifestFlag+1]);
const outputRoot=path.resolve(outFlag>=0&&args[outFlag+1]?args[outFlag+1]:path.join(__dirname,"../public/assets/maple-v83"));
if(!fs.existsSync(sourceRoot)||!fs.statSync(sourceRoot).isDirectory()) fail(`source directory does not exist: ${sourceRoot}`);
if(!fs.existsSync(manifestPath)) fail(`selection manifest does not exist: ${manifestPath}`);

let selection;
try{selection=JSON.parse(fs.readFileSync(manifestPath,"utf8"));}catch(error){fail(`invalid JSON manifest: ${error.message}`);}
if(!selection||!Array.isArray(selection.assets)) fail("manifest must contain an assets array");

const allowedExt=new Set([".png",".gif",".webp",".jpg",".jpeg",".svg"]);
const imported=[];
const seenTargets=new Set();

function safeRelative(value,label){
  if(typeof value!=="string"||!value.trim()) fail(`${label} must be a non-empty string`);
  const normalized=value.replaceAll("\\","/").replace(/^\.\//,"");
  if(path.isAbsolute(normalized)||normalized.split("/").some(part=>part==="..")) fail(`${label} escapes its root: ${value}`);
  return normalized;
}

for(const entry of selection.assets){
  if(!entry||typeof entry!=="object") fail("every asset entry must be an object");
  const source=safeRelative(entry.source,"source");
  const target=safeRelative(entry.target,"target");
  const ext=path.extname(target).toLowerCase();
  if(!allowedExt.has(ext)) fail(`unsupported target extension for ${target}`);
  if(seenTargets.has(target)) fail(`duplicate target: ${target}`);
  seenTargets.add(target);

  const sourcePath=path.resolve(sourceRoot,source);
  const targetPath=path.resolve(outputRoot,target);
  if(!sourcePath.startsWith(sourceRoot+path.sep)&&sourcePath!==sourceRoot) fail(`source escapes export root: ${source}`);
  if(!targetPath.startsWith(outputRoot+path.sep)&&targetPath!==outputRoot) fail(`target escapes asset root: ${target}`);
  if(!fs.existsSync(sourcePath)||!fs.statSync(sourcePath).isFile()) fail(`missing exported asset: ${source}`);

  const bytes=fs.readFileSync(sourcePath);
  fs.mkdirSync(path.dirname(targetPath),{recursive:true});
  fs.writeFileSync(targetPath,bytes);
  imported.push({
    id:String(entry.id||path.basename(target,path.extname(target))),
    source,
    target,
    bytes:bytes.length,
    sha256:crypto.createHash("sha256").update(bytes).digest("hex")
  });
}

fs.mkdirSync(outputRoot,{recursive:true});
const generated={
  schema:1,
  generatedAt:new Date().toISOString(),
  sourceLabel:String(selection.sourceLabel||"local MapleStory asset export"),
  count:imported.length,
  assets:imported
};
fs.writeFileSync(path.join(outputRoot,"manifest.json"),JSON.stringify(generated,null,2)+"\n");
console.log(`Imported ${imported.length} Maple asset(s) into ${outputRoot}`);
