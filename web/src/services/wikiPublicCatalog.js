const data=require("./wikiDataService");

const cache={builtAt:0,types:new Map()};

function cleanText(value=""){
  return String(value)
    .replace(/\s+/g," ")
    .replace(/^[\s\-–—:|]+|[\s\-–—:|]+$/g,"")
    .trim();
}

function normalizeText(value=""){
  return cleanText(value)
    .toLowerCase()
    .replace(/#(?:[a-z]|[0-9a-f]{6})/gi,"")
    .replace(/[’'`]/g,"")
    .replace(/[^a-z0-9]+/g," ")
    .trim();
}

function looksInternal(entity){
  const name=cleanText(entity?.name);
  const description=cleanText(entity?.description);
  if(!name||name.length<2)return true;
  if(/^\d+$/.test(name))return true;
  if(/^[?*_.\-–—]+$/.test(name))return true;
  const combined=`${name} ${description}`.toLowerCase();
  if(/\b(?:dummy|placeholder|unused|not\s+used|do\s+not\s+use|dont\s+use|debug)\b/i.test(combined))return true;
  if(/^(?:test|sample|reserved)(?:\s+(?:item|mob|monster|npc|map|skill|quest|data))?$/i.test(name))return true;
  if(/^zz(?:z+)?\b/i.test(name))return true;
  return false;
}

function quality(entity){
  let score=0;
  if(cleanText(entity?.description))score+=4;
  if(cleanText(entity?.subtype))score+=2;
  if(Number.isInteger(Number(entity?.id))&&Number(entity.id)>0)score+=1;
  return score;
}

function identityKey(entity){
  return [
    entity?.type||"",
    normalizeText(entity?.name),
    normalizeText(entity?.subtype),
    normalizeText(entity?.description)
  ].join("|");
}

function dedupeEntities(rows=[]){
  const groups=new Map();
  for(const raw of rows){
    if(!raw||looksInternal(raw))continue;
    const entity={...raw,name:cleanText(raw.name),description:cleanText(raw.description),subtype:cleanText(raw.subtype)};
    const key=identityKey(entity);
    if(!key||key.endsWith("|||"))continue;
    const existing=groups.get(key);
    if(!existing){
      groups.set(key,{...entity,variantIds:[Number(entity.id)]});
      continue;
    }
    existing.variantIds.push(Number(entity.id));
    const currentQuality=quality(entity);
    const existingQuality=quality(existing);
    if(currentQuality>existingQuality||(currentQuality===existingQuality&&Number(entity.id)<Number(existing.id))){
      const variantIds=existing.variantIds;
      groups.set(key,{...entity,variantIds});
    }
  }
  return [...groups.values()]
    .map(entity=>({
      ...entity,
      variantIds:[...new Set(entity.variantIds.filter(Number.isInteger))].sort((a,b)=>a-b),
      variantCount:new Set(entity.variantIds.filter(Number.isInteger)).size
    }))
    .sort((a,b)=>a.name.localeCompare(b.name)||Number(a.id)-Number(b.id));
}

function syncCache(){
  data.ensureCatalog();
  const status=data.snapshot();
  if(cache.builtAt!==status.builtAt){
    cache.builtAt=status.builtAt;
    cache.types.clear();
  }
  return status;
}

function loadType(type){
  syncCache();
  if(!data.TYPE_META[type])return [];
  if(cache.types.has(type))return cache.types.get(type);
  const rows=[];
  let page=1;
  let pages=1;
  do{
    const batch=data.list(type,{page,limit:100});
    rows.push(...batch.rows);
    pages=batch.pages;
    page+=1;
  }while(page<=pages);
  const cleaned=dedupeEntities(rows);
  cache.types.set(type,cleaned);
  return cleaned;
}

function scoreEntity(entity,query){
  const q=normalizeText(query);
  if(!q)return 0;
  const id=String(entity.id);
  const name=normalizeText(entity.name);
  const description=normalizeText(entity.description);
  const subtype=normalizeText(entity.subtype);
  if(id===String(query).trim())return 1000;
  if(name===q)return 950;
  if(name.startsWith(q))return 800;
  if(name.includes(q))return 650;
  if(id.startsWith(String(query).trim()))return 500;
  if(subtype.includes(q))return 300;
  if(description.includes(q))return 200;
  return -1;
}

function withExactId(rows,type,q){
  const value=String(q||"").trim();
  if(!/^\d+$/.test(value))return rows;
  const raw=data.getBase(type,Number(value));
  if(!raw)return rows;
  if(rows.some(row=>Number(row.id)===Number(raw.id)))return rows;
  return [{...raw,variantIds:[Number(raw.id)],variantCount:1},...rows];
}

function list(type,{q="",page=1,limit=40}={}){
  if(!data.TYPE_META[type])return {rows:[],total:0,page:1,pages:1,limit:40};
  const safeLimit=Math.max(10,Math.min(100,Number(limit)||40));
  let rows=loadType(type);
  if(String(q).trim()){
    rows=rows
      .map(entity=>({entity,score:scoreEntity(entity,q)}))
      .filter(row=>row.score>=0)
      .sort((a,b)=>b.score-a.score||a.entity.name.localeCompare(b.entity.name)||Number(a.entity.id)-Number(b.entity.id))
      .map(row=>row.entity);
    rows=withExactId(rows,type,q);
  }
  const total=rows.length;
  const pages=Math.max(1,Math.ceil(total/safeLimit));
  const safePage=Math.max(1,Math.min(pages,Number(page)||1));
  const offset=(safePage-1)*safeLimit;
  return {rows:rows.slice(offset,offset+safeLimit),total,page:safePage,pages,limit:safeLimit};
}

function search(query,type="all",limit=60){
  const q=String(query||"").trim();
  if(!q)return [];
  const types=data.TYPE_META[type]?[type]:Object.keys(data.TYPE_META);
  let rows=types
    .flatMap(kind=>loadType(kind).map(entity=>({entity,score:scoreEntity(entity,q)})))
    .filter(row=>row.score>=0)
    .sort((a,b)=>b.score-a.score||a.entity.name.localeCompare(b.entity.name)||Number(a.entity.id)-Number(b.entity.id))
    .map(row=>row.entity);
  if(/^\d+$/.test(q)){
    for(const kind of types){
      const raw=data.getBase(kind,Number(q));
      if(raw&&!rows.some(row=>row.type===kind&&Number(row.id)===Number(raw.id))){
        rows.unshift({...raw,variantIds:[Number(raw.id)],variantCount:1});
      }
    }
  }
  const seen=new Set();
  return rows.filter(entity=>{
    const key=`${entity.type}:${entity.id}`;
    if(seen.has(key))return false;
    seen.add(key);
    return true;
  }).slice(0,Math.max(1,Math.min(100,Number(limit)||60)));
}

function snapshot(){
  const raw=syncCache();
  const counts=Object.fromEntries(Object.keys(data.TYPE_META).map(type=>[type,loadType(type).length]));
  return {...raw,counts};
}

module.exports={
  TYPE_META:data.TYPE_META,
  typeMeta:data.typeMeta,
  list,
  search,
  snapshot,
  ensureCatalog:snapshot,
  getBase:data.getBase,
  detail:data.detail,
  _test:{cleanText,normalizeText,looksInternal,identityKey,dedupeEntities,scoreEntity}
};
