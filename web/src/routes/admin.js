const express=require("express");
const bcrypt=require("bcryptjs");
const {db,settings}=require("../db/cms");
const {requireAdmin}=require("../middleware/auth");
const game=require("../services/gameService");
const {getPool,safeIdent:I}=require("../db/game");
const env=require("../config/env");
const router=express.Router();

router.get("/login",(req,res)=>res.render("admin-login",{error:"",settings:settings()}));
router.post("/login",async(req,res)=>{
  const admin=db.prepare("SELECT * FROM admins WHERE username=?").get(String(req.body.username||""));
  if(!admin || !(await bcrypt.compare(String(req.body.password||""),admin.password_hash)))
    return res.status(401).render("admin-login",{error:"Invalid credentials.",settings:settings()});
  req.session.admin={id:admin.id,username:admin.username};
  res.redirect("/admin");
});
router.post("/logout",(req,res)=>req.session.destroy(()=>res.redirect("/admin/login")));

router.get("/",requireAdmin,async(req,res)=>{
  const posts=db.prepare("SELECT * FROM posts ORDER BY created_at DESC").all();
  const downloads=db.prepare("SELECT * FROM downloads ORDER BY created_at DESC").all();
  const announcements=db.prepare("SELECT * FROM announcements ORDER BY created_at DESC LIMIT 10").all();
  const donations=db.prepare("SELECT * FROM donations ORDER BY created_at DESC LIMIT 10").all();
  const donationTotal=db.prepare("SELECT COALESCE(SUM(amount_cents),0) total FROM donations WHERE status='completed'").get().total;
  let players=0,accounts=0,recentAccounts=[],status={online:false,channels:0,totalChannels:env.game.channelPorts.length};
  try{
    const pool=getPool(),g=env.gameDb;
    const [accountRows]=await pool.query(`SELECT COUNT(*) count FROM ${I(g.accountsTable)}`);
    accounts=Number(accountRows[0]?.count||0);
    const [recentRows]=await pool.query(`SELECT ${I(g.accountName)} name, createdat, ${I(g.accountBanned)} banned FROM ${I(g.accountsTable)} ORDER BY ${I(g.accountId)} DESC LIMIT 8`);
    recentAccounts=recentRows;
    [players,status]=await Promise.all([game.onlineCount(),game.serverStatus()]);
  }catch{}
  res.render("admin",{posts,downloads,announcements,donations,donationTotal,players,accounts,recentAccounts,status,site:settings(),settings:settings()});
});

router.post("/posts",requireAdmin,(req,res)=>{
  const slug=String(req.body.slug||req.body.title||"post").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"").slice(0,80);
  db.prepare(`INSERT INTO posts(slug,title,excerpt,body,type,published) VALUES(?,?,?,?,?,?)`)
    .run(slug,String(req.body.title||""),String(req.body.excerpt||""),String(req.body.body||""),String(req.body.type||"news"),req.body.published?1:0);
  res.redirect("/admin");
});

router.get("/posts/:id/edit",requireAdmin,(req,res)=>{
  const post=db.prepare("SELECT * FROM posts WHERE id=?").get(Number(req.params.id));
  if(!post) return res.redirect("/admin");
  res.render("admin-edit-post",{post,settings:settings()});
});
router.post("/posts/:id/edit",requireAdmin,(req,res)=>{
  const slug=String(req.body.slug||req.body.title||"post").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"").slice(0,80);
  db.prepare(`UPDATE posts SET slug=?,title=?,excerpt=?,body=?,type=?,published=?,updated_at=CURRENT_TIMESTAMP WHERE id=?`)
    .run(slug,String(req.body.title||""),String(req.body.excerpt||""),String(req.body.body||""),String(req.body.type||"news"),req.body.published==="1"?1:0,Number(req.params.id));
  res.redirect("/admin");
});

router.post("/posts/:id/delete",requireAdmin,(req,res)=>{
  db.prepare("DELETE FROM posts WHERE id=?").run(Number(req.params.id));
  res.redirect("/admin");
});

router.post("/downloads",requireAdmin,(req,res)=>{
  db.prepare(`INSERT INTO downloads(name,description,url,kind,version,published) VALUES(?,?,?,?,?,?)`)
    .run(String(req.body.name||""),String(req.body.description||""),String(req.body.url||""),String(req.body.kind||"client"),String(req.body.version||""),req.body.published?1:0);
  res.redirect("/admin");
});

router.post("/downloads/:id/delete",requireAdmin,(req,res)=>{
  db.prepare("DELETE FROM downloads WHERE id=?").run(Number(req.params.id));
  res.redirect("/admin");
});

router.post("/settings",requireAdmin,(req,res)=>{
  const allowed=["hero_title","hero_subtitle","announcement","maintenance_message","footer_note"];
  const up=db.prepare("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value");
  for(const key of allowed) up.run(key,String(req.body[key]||""));
  res.redirect("/admin");
});

router.post("/announcements",requireAdmin,(req,res)=>{
  db.prepare("INSERT INTO announcements(title,body,active) VALUES(?,?,?)")
    .run(String(req.body.title||""),String(req.body.body||""),req.body.active?1:0);
  res.redirect("/admin");
});
router.post("/announcements/:id/delete",requireAdmin,(req,res)=>{
  db.prepare("DELETE FROM announcements WHERE id=?").run(Number(req.params.id));
  res.redirect("/admin");
});

module.exports=router;
