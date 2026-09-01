const express=require("express");
const {settings}=require("../db/cms");
const {categories,entries,bySlug,searchEntries}=require("../data/wikiCatalog");
const router=express.Router();

router.get("/wiki",(req,res)=>{
  const q=String(req.query.q||"").trim();
  const category=String(req.query.category||"all");
  const results=searchEntries(q,category);
  res.render("wiki",{settings:settings(),categories,entries,results,q,category});
});

router.get("/wiki/:slug",(req,res,next)=>{
  const entry=bySlug.get(String(req.params.slug||""));
  if(!entry)return next();
  const related=entries.filter(item=>item.slug!==entry.slug&&item.category===entry.category).slice(0,4);
  res.render("wiki-entry",{settings:settings(),entry,categories,related});
});

module.exports=router;
