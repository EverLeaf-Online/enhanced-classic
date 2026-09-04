const express=require("express");
const {settings}=require("../db/cms");
const wiki=require("../services/wikiService");
const router=express.Router();

router.get("/wiki",(req,res)=>{
  const q=String(req.query.q||"").trim().slice(0,120);
  const category=wiki.categoryKeys.has(String(req.query.category||""))?String(req.query.category):"all";
  const entries=wiki.listPublished();
  const results=wiki.searchEntries(q,category);
  res.render("wiki",{
    settings:settings(),
    categories:wiki.categories,
    entries,
    results,
    stats:wiki.stats(),
    q,
    category
  });
});

router.get("/wiki/:slug",(req,res,next)=>{
  const entry=wiki.getBySlug(String(req.params.slug||""));
  if(!entry)return next();
  const related=wiki.relatedEntries(entry,4);
  res.render("wiki-entry",{
    settings:settings(),
    entry,
    categories:wiki.categories,
    related
  });
});

module.exports=router;
