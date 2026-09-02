const express=require('express');
const {requireAdmin}=require('../middleware/auth');
const {settings}=require('../db/cms');
const {categories,entries,searchEntries,sourceCoverage}=require('../services/wikiCatalog');
const router=express.Router();

router.get('/knowledge',requireAdmin,(req,res)=>{
  const q=String(req.query.q||'').trim();
  const category=String(req.query.category||'all');
  const results=searchEntries(q,category);
  const coverage=categories.map(cat=>({
    ...cat,
    count:entries.filter(entry=>entry.category===cat.key).length
  }));
  const sources=sourceCoverage();
  const verifiedCount=entries.filter(entry=>entry.verification).length;
  res.render('admin-knowledge',{settings:settings(),categories,entries,results,coverage,sources,verifiedCount,q,category});
});

module.exports=router;
