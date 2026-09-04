const express=require('express');
const {requireAdmin}=require('../middleware/auth');
const {db,settings}=require('../db/cms');
const wiki=require('../services/wikiService');
const router=express.Router();

const logAdmin=(req,action,details='')=>db.prepare('INSERT INTO audit_log(admin_id,action,details) VALUES(?,?,?)').run(req.session.admin?.id||null,action,String(details).slice(0,500));

function renderIndex(req,res){
  const q=String(req.query.q||'').trim().slice(0,120);
  const category=wiki.categoryKeys.has(String(req.query.category||''))?String(req.query.category):'all';
  const entries=wiki.listAll();
  const results=wiki.searchEntries(q,category,{includeUnpublished:true});
  const coverage=wiki.categories.map(cat=>({
    ...cat,
    count:entries.filter(entry=>entry.category===cat.key).length
  }));
  const sources=wiki.sourceCoverage(entries);
  const verifiedCount=entries.filter(entry=>entry.verification).length;
  res.render('admin-knowledge',{
    settings:settings(),
    categories:wiki.categories,
    entries,
    results,
    coverage,
    sources,
    stats:wiki.stats(),
    verifiedCount,
    q,
    category,
    saved:String(req.query.saved||'')==='1'
  });
}

router.get('/knowledge',requireAdmin,renderIndex);

router.get('/knowledge/new',requireAdmin,(req,res)=>{
  res.render('admin-knowledge-edit',{
    settings:settings(),
    categories:wiki.categories,
    fields:wiki.editorFields(),
    error:'',
    isNew:true
  });
});

router.get('/knowledge/:id/edit',requireAdmin,(req,res)=>{
  const id=Number(req.params.id);
  if(!Number.isInteger(id)||id<1)return res.redirect('/admin/knowledge');
  const entry=wiki.getById(id);
  if(!entry)return res.redirect('/admin/knowledge');
  res.render('admin-knowledge-edit',{
    settings:settings(),
    categories:wiki.categories,
    fields:wiki.editorFields(entry),
    error:'',
    isNew:false
  });
});

router.post('/knowledge/save',requireAdmin,(req,res)=>{
  const id=String(req.body.id||'').trim()?Number(req.body.id):null;
  const fields={
    id:id||'',
    slug:String(req.body.slug||'').trim().toLowerCase(),
    category:String(req.body.category||'systems'),
    title:String(req.body.title||'').trim(),
    eyebrow:String(req.body.eyebrow||'EVERLEAF WIKI').trim(),
    summary:String(req.body.summary||'').trim(),
    body:String(req.body.body||'').replace(/\r\n/g,'\n').trim(),
    status:String(req.body.status||'EverLeaf Guide').trim(),
    verification:String(req.body.verification||'').trim(),
    source:String(req.body.source||'EverLeaf').trim(),
    sourceDoc:String(req.body.sourceDoc||'EverLeaf CMS').trim(),
    tags:String(req.body.tags||'').trim(),
    facts:String(req.body.facts||'').trim(),
    published:String(req.body.published||'')==='1'
  };
  const validId=!id||(Number.isInteger(id)&&id>0&&wiki.getById(id));
  const validSlug=/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(fields.slug)&&fields.slug.length<=100;
  const validCategory=wiki.categoryKeys.has(fields.category);
  const validText=fields.title.length>=2&&fields.title.length<=140&&fields.summary.length>=10&&fields.summary.length<=700&&fields.body.length>=3&&fields.body.length<=30000;
  if(!validId||!validSlug||!validCategory||!validText){
    return res.status(400).render('admin-knowledge-edit',{
      settings:settings(),categories:wiki.categories,fields,
      error:'Check the slug, category, title, summary, and article body. Slugs use lowercase words and hyphens only.',
      isNew:!id
    });
  }
  try{
    const saved=wiki.saveArticle(fields);
    logAdmin(req,id?'wiki.update':'wiki.create',`${saved.id}:${saved.slug}:${saved.published?'published':'draft'}`);
    res.redirect('/admin/knowledge?saved=1');
  }catch(error){
    const message=String(error.message||'');
    const friendly=message.includes('UNIQUE')?'That Wiki slug is already in use.':'The Wiki article could not be saved.';
    res.status(400).render('admin-knowledge-edit',{
      settings:settings(),categories:wiki.categories,fields,error:friendly,isNew:!id
    });
  }
});

module.exports=router;
