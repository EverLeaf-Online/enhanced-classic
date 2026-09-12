#!/usr/bin/env node
const fs=require('fs');
const path=require('path');

const wzRoot=path.resolve(process.env.WIKI_WZ_ROOT||'/opt/everleaf/server/wz');
const characterRoot=path.join(wzRoot,'Character.wz');
const output=path.resolve(__dirname,'../src/generated/wiki-cash-equip-ids.json');
const cashMarker=Buffer.from('name="cash" value="1"');
const cashEquipIds=[];

function walk(dir){
  for(const entry of fs.readdirSync(dir,{withFileTypes:true})){
    const full=path.join(dir,entry.name);
    if(entry.isDirectory()){
      walk(full);
      continue;
    }
    const match=entry.name.match(/^(\d{8})\.img\.xml$/i);
    if(!match)continue;
    const itemId=Number(match[1]);
    if(itemId<1_000_000||itemId>=2_000_000)continue;

    const fd=fs.openSync(full,'r');
    try{
      const head=Buffer.allocUnsafe(16*1024);
      const bytes=fs.readSync(fd,head,0,head.length,0);
      if(head.subarray(0,bytes).includes(cashMarker))cashEquipIds.push(itemId);
    }finally{
      fs.closeSync(fd);
    }
  }
}

if(!fs.existsSync(characterRoot))throw new Error(`Character WZ XML root not found: ${characterRoot}`);
walk(characterRoot);
cashEquipIds.sort((a,b)=>a-b);
fs.mkdirSync(path.dirname(output),{recursive:true});
fs.writeFileSync(output,JSON.stringify({
  source:characterRoot,
  rule:'Mirrors ItemInformationProvider.isCash: type-5 items are cash; type-1 equips use info/cash=1.',
  cashEquipIds
})+'\n');
console.log(`Wrote ${cashEquipIds.length} cash equipment IDs to ${output}`);
