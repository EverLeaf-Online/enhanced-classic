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

const mapleArtUrl=(type,id)=>{
  const value=Number(id);
  if(!Number.isInteger(value)||value<=0)return "";
  const root="https://maplestory.io/api/GMS/83";
  if(type==="items")return `${root}/item/${value}/icon`;
  if(type==="monsters")return `${root}/mob/${value}/icon`;
  if(type==="maps")return `${root}/map/${value}/icon`;
  if(type==="npcs")return `${root}/npc/${value}/icon`;
  if(type==="quests")return `${root}/quest/${value}/icon`;
  if(type==="skills"){
    const book=String(Math.floor(value/10000)).padStart(3,"0");
    return `https://maplestory.io/api/wz/img/GMS/83/Skill.wz/${book}.img/skill/${value}/icon`;
  }
  return "";
};

router.get("/wiki/art/:type/:id",async(req,res)=>{
  const type=String(req.params.type||"");
  const id=Number(req.params.id);
  const target=mapleArtUrl(type,id);
  if(!target)return res.status(404).end();

  const controller=new AbortController();
  const timer=setTimeout(()=>controller.abort(),MAPLE_ART_TIMEOUT_MS);
  try {
    const upstream=await fetch(target,{
      redirect:"follow",
      signal:controller.signal,
      headers:{
        Accept:"image/avif,image/webp,image/png,image/*,*/*;q=0.8",
        "User-Agent":"EverLeafWiki/1.0 (+https://everleafms.online)"
      }
    });
    if(!upstream.ok)return res.status(404).end();

    const contentType=String(upstream.headers.get("content-type")||"").split(";")[0].trim().toLowerCase();
    if(!contentType.startsWith("image/"))return res.status(404).end();
    const advertisedLength=Number(upstream.headers.get("content-length")||0);
    if(advertisedLength>MAPLE_ART_MAX_BYTES)return res.status(413).end();

    const body=Buffer.from(await upstream.arrayBuffer());
    if(!body.length||body.length>MAPLE_ART_MAX_BYTES)return res.status(body.length?413:404).end();

    res.set("Content-Type",contentType);
    res.set("Cache-Control","public, max-age=86400, stale-if-error=604800");
    res.set("X-Content-Type-Options","nosniff");
    return res.send(body);
  } catch(error) {
    if(error&&error.name!=="AbortError")console.warn(`Wiki artwork proxy failed for ${type}/${id}:`,error.message);
    return res.status(404).end();
  } finally {
    clearTimeout(timer);
  }
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
  const result=data.list(type,{q,page:cleanPage(req.query.page),limit:40});
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
