const express=require("express");
const {settings}=require("../db/cms");
const guides=require("../services/wikiService");
const data=require("../services/wikiPublicCatalog");
const router=express.Router();

const dataTypes=new Set(Object.keys(data.TYPE_META));
const cleanQuery=value=>String(value||"").trim().slice(0,120);
const cleanPage=value=>Math.max(1,Math.min(100000,Number(value)||1));
const MAPLE_ART_MAX_BYTES=2*1024*1024;
const MAPLE_ART_TIMEOUT_MS=7000;

const mapleArtUrls=(type,id)=>{
  const value=Number(id);
  if(!Number.isInteger(value)||value<=0)return [];
  if(type==="items"){
    const urls=[`https://maplestory.io/api/GMS/83/item/${value}/icon`];
    // Some v83 face/hair entries do not expose an item icon even though the
    // character renderer can draw them correctly.
    if(value<1000000)urls.push(`https://maplestory.io/api/GMS/83/Character/2000/${value}/stand1/0`);
    urls.push(`https://maplestory.io/api/GMS/latest/item/${value}/icon`);
    if(value<1000000)urls.push(`https://maplestory.io/api/GMS/latest/Character/2000/${value}/stand1/0`);
    return urls;
  }
  if(type==="monsters")return [
    `https://maplestory.io/api/GMS/83/mob/${value}/icon`,
    `https://maplestory.io/api/GMS/latest/mob/${value}/icon`
  ];
  if(type==="maps")return [
    `https://maplestory.io/api/GMS/83/map/${value}/icon`,
    `https://maplestory.io/api/GMS/83/map/${value}/minimap`,
    `https://maplestory.io/api/GMS/latest/map/${value}/icon`,
    `https://maplestory.io/api/GMS/latest/map/${value}/minimap`
  ];
  if(type==="npcs")return [
    `https://maplestory.io/api/GMS/83/npc/${value}/icon`,
    `https://maplestory.io/api/GMS/latest/npc/${value}/icon`
  ];
  if(type==="quests")return [
    `https://maplestory.io/api/GMS/83/quest/${value}/icon`,
    `https://maplestory.io/api/GMS/latest/quest/${value}/icon`
  ];
  return [];
};

// Small in-process cache keeps catalog pagination from repeatedly hammering the
// upstream art service. The latest-version fallback is only used when v83 has
// no image, which lets intentional backports render without making modern data
// the source of truth for the Wiki catalog itself.
const MAPLE_ART_CACHE_MAX=800;
const mapleArtCache=new Map();
function cacheMapleArt(key,value){
  if(mapleArtCache.has(key))mapleArtCache.delete(key);
  mapleArtCache.set(key,value);
  while(mapleArtCache.size>MAPLE_ART_CACHE_MAX)mapleArtCache.delete(mapleArtCache.keys().next().value);
}

router.get("/wiki/art/:type/:id",async(req,res)=>{
  const type=String(req.params.type||"");
  const id=Number(req.params.id);
  const targets=mapleArtUrls(type,id);
  if(type!=="skills"&&!targets.length)return res.status(404).end();

  const cacheKey=`${type}:${id}`;
  const cached=mapleArtCache.get(cacheKey);
  if(cached&&cached.expiresAt>Date.now()){
    res.set("Content-Type",cached.contentType);
    res.set("Cache-Control","public, max-age=86400, stale-if-error=604800");
    res.set("X-Content-Type-Options","nosniff");
    return res.send(cached.body);
  }

  // Skill icons are returned as base64 in maplestory.io's skill JSON rather
  // than reliably through the generic WZ-image endpoint.
  if(type==="skills"){
    for(const version of ["83","latest"]){
      const controller=new AbortController();
      const timer=setTimeout(()=>controller.abort(),MAPLE_ART_TIMEOUT_MS);
      try {
        const upstream=await fetch(`https://maplestory.io/api/GMS/${version}/job/skill/${id}`,{
          redirect:"follow",
          signal:controller.signal,
          headers:{Accept:"application/json","User-Agent":"EverLeafWiki/1.1 (+https://everleafms.online)"}
        });
        if(!upstream.ok)continue;
        const payload=await upstream.json();
        const encoded=String(payload?.icon||payload?.iconRaw||"").trim();
        if(!encoded)continue;
        const body=Buffer.from(encoded,"base64");
        if(!body.length||body.length>MAPLE_ART_MAX_BYTES||body.subarray(0,8).toString("hex")!=="89504e470d0a1a0a")continue;
        cacheMapleArt(cacheKey,{contentType:"image/png",body,expiresAt:Date.now()+24*60*60_000});
        res.set("Content-Type","image/png");
        res.set("Cache-Control","public, max-age=86400, stale-if-error=604800");
        res.set("X-Content-Type-Options","nosniff");
        return res.send(body);
      } catch(error) {
        if(error&&error.name!=="AbortError")console.warn(`Wiki skill artwork proxy failed for ${id}:`,error.message);
      } finally {
        clearTimeout(timer);
      }
    }
    return res.status(404).end();
  }

  for(const target of targets){
    const controller=new AbortController();
    const timer=setTimeout(()=>controller.abort(),MAPLE_ART_TIMEOUT_MS);
    try {
      const upstream=await fetch(target,{
        redirect:"follow",
        signal:controller.signal,
        headers:{
          Accept:"image/avif,image/webp,image/png,image/*,*/*;q=0.8",
          "User-Agent":"EverLeafWiki/1.1 (+https://everleafms.online)"
        }
      });
      if(!upstream.ok)continue;

      const contentType=String(upstream.headers.get("content-type")||"").split(";")[0].trim().toLowerCase();
      if(!contentType.startsWith("image/"))continue;
      const advertisedLength=Number(upstream.headers.get("content-length")||0);
      if(advertisedLength>MAPLE_ART_MAX_BYTES)continue;

      const body=Buffer.from(await upstream.arrayBuffer());
      if(!body.length||body.length>MAPLE_ART_MAX_BYTES)continue;

      cacheMapleArt(cacheKey,{contentType,body,expiresAt:Date.now()+24*60*60_000});
      res.set("Content-Type",contentType);
      res.set("Cache-Control","public, max-age=86400, stale-if-error=604800");
      res.set("X-Content-Type-Options","nosniff");
      return res.send(body);
    } catch(error) {
      if(error&&error.name!=="AbortError")console.warn(`Wiki artwork proxy failed for ${type}/${id}:`,error.message);
    } finally {
      clearTimeout(timer);
    }
  }

  return res.status(404).end();
});

router.get("/wiki",(req,res)=>{
  const q=cleanQuery(req.query.q);
  const requestedType=String(req.query.type||"all");
  const activeType=dataTypes.has(requestedType)?requestedType:"all";
  let status;
  let results=[];
  try {
    status=data.ensureCatalog();
    if(q)results=data.search(q,activeType,60);
  } catch(error) {
    console.warn("Wiki catalog build failed:",error.message);
    status={available:false,builtAt:Date.now(),counts:Object.fromEntries([...dataTypes].map(type=>[type,0])),errors:["The EverLeaf game-data catalog could not be indexed."]};
  }
  res.render("wiki",{
    settings:settings(),
    types:data.TYPE_META,
    status,
    results,
    q,
    activeType
  });
});

router.get("/wiki/guides",(req,res)=>{
  const q=cleanQuery(req.query.q);
  const category=guides.categoryKeys.has(String(req.query.category||""))?String(req.query.category):"all";
  const entries=guides.listPublished();
  const results=guides.searchEntries(q,category);
  res.render("wiki-guides",{
    settings:settings(),
    categories:guides.categories,
    entries,
    results,
    stats:guides.stats(),
    q,
    category
  });
});

router.get("/wiki/guides/:slug",(req,res,next)=>{
  const entry=guides.getBySlug(String(req.params.slug||""));
  if(!entry)return next();
  const related=guides.relatedEntries(entry,4);
  res.render("wiki-entry",{
    settings:settings(),
    entry,
    categories:guides.categories,
    related,
    guideBase:"/wiki/guides"
  });
});

router.get("/wiki/:type",(req,res,next)=>{
  const type=String(req.params.type||"");
  if(!dataTypes.has(type))return next();
  const q=cleanQuery(req.query.q);
  const itemCategory=type==="items"?String(req.query.itemCategory||"all"):"all";
  const itemCash=type==="items"?String(req.query.itemCash||"all"):"all";
  const result=data.list(type,{q,itemCategory,itemCash,page:cleanPage(req.query.page),limit:40});
  res.render("wiki-data-list",{
    settings:settings(),
    types:data.TYPE_META,
    type,
    meta:data.typeMeta(type),
    result,
    q,
    status:data.snapshot()
  });
});

router.get("/wiki/:type/:id",async(req,res,next)=>{
  const type=String(req.params.type||"");
  if(!dataTypes.has(type))return next();
  const id=Number(req.params.id);
  if(!Number.isInteger(id)||id<0)return next();
  try {
    const entry=await data.detail(type,id);
    if(!entry)return next();
    return res.render("wiki-data-entry",{
      settings:settings(),
      types:data.TYPE_META,
      meta:data.typeMeta(type),
      entry,
      detailWarning:""
    });
  } catch(error) {
    console.warn(`Wiki ${type} detail failed for ${id}:`,error.message);
    const base=data.getBase(type,id);
    if(!base)return next();
    return res.status(200).render("wiki-data-entry",{
      settings:settings(),
      types:data.TYPE_META,
      meta:data.typeMeta(type),
      entry:{...base,sections:{},partial:true},
      detailWarning:"Some linked server details are temporarily unavailable, but this record is still valid and searchable."
    });
  }
});

// Preserve old guide links from before the data-Wiki transition.
router.get("/wiki/:slug",(req,res,next)=>{
  const slug=String(req.params.slug||"");
  const entry=guides.getBySlug(slug);
  if(!entry)return next();
  return res.redirect(301,`/wiki/guides/${encodeURIComponent(slug)}`);
});

module.exports=router;
