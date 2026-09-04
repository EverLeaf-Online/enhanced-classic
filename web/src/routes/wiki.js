const express=require("express");
const {settings}=require("../db/cms");
const guides=require("../services/wikiService");
const data=require("../services/wikiPublicCatalog");
const router=express.Router();

const dataTypes=new Set(Object.keys(data.TYPE_META));
const cleanQuery=value=>String(value||"").trim().slice(0,120);
const cleanPage=value=>Math.max(1,Math.min(100000,Number(value)||1));

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
