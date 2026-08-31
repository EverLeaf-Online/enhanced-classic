const express=require("express");
const bcrypt=require("bcryptjs");
const {db,settings}=require("../db/cms");
const {requireAdmin}=require("../middleware/auth");
const game=require("../services/gameService");
const {getPool,safeIdent:I}=require("../db/game");
const env=require("../config/env");
const adminSupporter=require("../services/adminSupporterService");
const router=express.Router();

const CORE_PAGES=new Set(["about","rules","terms"]);
const cleanSlug=value=>String(value||"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"").slice(0,80);
const logAdmin=(req,action,details="")=>db.prepare("INSERT INTO audit_log(admin_id,action,details) VALUES(?,?,?)").run(req.session.admin?.id||null,action,String(details).slice(0,500));

router.get("/login",(req,res)=>res.render("admin-login",{error:"",settings:settings()}));
router.post("/login",async(req,res)=>{
  const admin=db.prepare("SELECT * FROM admins WHERE username=?").get(String(req.body.username||""));
  if(!admin || !(await bcrypt.compare(String(req.body.password||""),admin.password_hash)))
    return res.status(401).render("admin-login",{error:"Invalid credentials.",settings:settings()});
  req.session.admin={id:admin.id,username:admin.username};
  res.redirect("/admin");
});
router.post("/logout",(req,res)=>req.session.destroy(()=>res.redirect("/admin/login")));

router.get("/supporters",requireAdmin,(req,res)=>{
  const filters={status:String(req.query.status||""),provider:String(req.query.provider||""),search:String(req.query.search||""),roleStatus:String(req.query.roleStatus||""),page:Number(req.query.page||1)};
  const payments=adminSupporter.listPayments(filters);
  const supporters=adminSupporter.listSupporters(filters);
  const syncStatus=String(req.query.supporterSync||"");
  res.render("admin-supporters",{payments,supporters,summary:adminSupporter.dashboardSummary(),filters,syncStatus,settings:settings()});
});

router.get("/",requireAdmin,async(req,res)=>{
  const posts=db.prepare("SELECT * FROM posts ORDER BY created_at DESC").all();
  const downloads=db.prepare("SELECT * FROM downloads ORDER BY created_at DESC").all();
  const announcements=db.prepare("SELECT * FROM announcements ORDER BY created_at DESC LIMIT 10").all();
  const pages=db.prepare("SELECT * FROM pages ORDER BY slug").all();
  const donations=db.prepare("SELECT * FROM donations ORDER BY created_at DESC LIMIT 10").all();
  const donationTotal=db.prepare("SELECT COALESCE(SUM(amount_cents),0) total FROM donations WHERE status='completed'").get().total;
  const paymentOrders=db.prepare("SELECT * FROM payment_orders ORDER BY created_at DESC LIMIT 20").all();
  const supporterProfiles=db.prepare("SELECT * FROM supporter_profiles ORDER BY lifetime_cents DESC,created_at DESC LIMIT 20").all();
  const supporterSummary=adminSupporter.dashboardSummary();
  const auditLog=db.prepare("SELECT action,details,created_at FROM audit_log ORDER BY id DESC LIMIT 20").all();
  let players=0,accounts=0,recentAccounts=[],status={online:false,channels:0,totalChannels:env.game.channelPorts.length};
  try{
    const pool=getPool(),g=env.gameDb;
    const [accountRows]=await pool.query(`SELECT COUNT(*) count FROM ${I(g.accountsTable)}`);
    accounts=Number(accountRows[0]?.count||0);
    const [recentRows]=await pool.query(`SELECT ${I(g.accountName)} name, createdat, ${I(g.accountBanned)} banned FROM ${I(g.accountsTable)} ORDER BY ${I(g.accountId)} DESC LIMIT 8`);
    recentAccounts=recentRows;
    [players,status]=await Promise.all([game.onlineCount(),game.serverStatus()]);
  }catch{}
  const syncStatus=String(req.query.supporterSync||"");
  res.render("admin",{posts,downloads,announcements,pages,donations,donationTotal,paymentOrders,supporterProfiles,supporterSummary,auditLog,syncStatus,players,accounts,recentAccounts,status,site:settings(),settings:settings()});
});

router.post("/supporters/:accountId/sync-discord",requireAdmin,async(req,res)=>{
  try {
    const status=await adminSupporter.retryDiscordRole(req.params.accountId,req.session.admin.id);
    if(req.get("referer")?.includes("/admin/supporters")) res.redirect(`/admin/supporters?supporterSync=${encodeURIComponent(status)}`);
    else res.redirect(`/admin?supporterSync=${encodeURIComponent(status)}#donations`);
  } catch(error) {
    console.warn("Admin Discord role sync failed:",error.message);
    if(req.get("referer")?.includes("/admin/supporters")) res.redirect("/admin/supporters?supporterSync=failed");
    else res.redirect("/admin?supporterSync=failed#donations");
  }
});

router.post("/posts",requireAdmin,(req,res)=>{
  const slug=cleanSlug(req.body.slug||req.body.title||"post");
  db.prepare(`INSERT INTO posts(slug,title,excerpt,body,type,published) VALUES(?,?,?,?,?,?)`).run(slug,String(req.body.title||""),String(req.body.excerpt||""),String(req.body.body||""),String(req.body.type||"news"),req.body.published?1:0);
  logAdmin(req,"post.create",slug);
  res.redirect("/admin");
});
router.get("/posts/:id/edit",requireAdmin,(req,res)=>{
  const post=db.prepare("SELECT * FROM posts WHERE id=?").get(Number(req.params.id));
  if(!post) return res.redirect("/admin");
  res.render("admin-edit-post",{post,settings:settings()});
});
router.post("/posts/:id/edit",requireAdmin,(req,res)=>{
  const slug=cleanSlug(req.body.slug||req.body.title||"post");
  db.prepare(`UPDATE posts SET slug=?,title=?,excerpt=?,body=?,type=?,published=?,updated_at=CURRENT_TIMESTAMP WHERE id=?`).run(slug,String(req.body.title||""),String(req.body.excerpt||""),String(req.body.body||""),String(req.body.type||"news"),req.body.published==="1"?1:0,Number(req.params.id));
  logAdmin(req,"post.update",slug);
  res.redirect("/admin");
});
router.post("/posts/:id/delete",requireAdmin,(req,res)=>{
  const post=db.prepare("SELECT slug FROM posts WHERE id=?").get(Number(req.params.id));
  db.prepare("DELETE FROM posts WHERE id=?").run(Number(req.params.id));
  logAdmin(req,"post.delete",post?.slug||req.params.id);
  res.redirect("/admin");
});

router.get("/downloads",requireAdmin,(req,res)=>{
  const downloads=db.prepare("SELECT * FROM downloads ORDER BY created_at DESC").all();
  res.render("admin-downloads",{downloads,settings:settings()});
});
router.post("/downloads",requireAdmin,(req,res)=>{
  const name=String(req.body.name||"").trim();
  const url=String(req.body.url||"").trim();
  if(!name||!url) return res.status(400).send("Download name and URL are required.");
  db.prepare(`INSERT INTO downloads(name,description,url,kind,version,published) VALUES(?,?,?,?,?,?)`).run(name,String(req.body.description||""),url,String(req.body.kind||"client"),String(req.body.version||""),req.body.published?1:0);
  logAdmin(req,"download.create",name);
  res.redirect(req.get("referer")?.includes("/admin/downloads")?"/admin/downloads":"/admin#downloads");
});
router.get("/downloads/:id/edit",requireAdmin,(req,res)=>{
  const item=db.prepare("SELECT * FROM downloads WHERE id=?").get(Number(req.params.id));
  if(!item) return res.redirect("/admin/downloads");
  res.render("admin-edit-download",{item,settings:settings()});
});
router.post("/downloads/:id/edit",requireAdmin,(req,res)=>{
  const name=String(req.body.name||"").trim();
  const url=String(req.body.url||"").trim();
  if(!name||!url) return res.status(400).send("Download name and URL are required.");
  db.prepare("UPDATE downloads SET name=?,description=?,url=?,kind=?,version=?,published=? WHERE id=?")
    .run(name,String(req.body.description||""),url,String(req.body.kind||"client"),String(req.body.version||""),req.body.published==="1"?1:0,Number(req.params.id));
  logAdmin(req,"download.update",name);
  res.redirect("/admin/downloads");
});
router.post("/downloads/:id/delete",requireAdmin,(req,res)=>{
  const item=db.prepare("SELECT name FROM downloads WHERE id=?").get(Number(req.params.id));
  db.prepare("DELETE FROM downloads WHERE id=?").run(Number(req.params.id));
  logAdmin(req,"download.delete",item?.name||req.params.id);
  res.redirect(req.get("referer")?.includes("/admin/downloads")?"/admin/downloads":"/admin#downloads");
});

router.post("/settings",requireAdmin,(req,res)=>{
  const allowed=["hero_title","hero_subtitle","announcement","maintenance_message","footer_note"];
  const up=db.prepare("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value");
  for(const key of allowed) up.run(key,String(req.body[key]||""));
  logAdmin(req,"settings.update",allowed.join(","));
  res.redirect("/admin");
});

router.post("/announcements",requireAdmin,(req,res)=>{
  db.prepare("INSERT INTO announcements(title,body,active) VALUES(?,?,?)").run(String(req.body.title||""),String(req.body.body||""),req.body.active?1:0);
  logAdmin(req,"announcement.create",String(req.body.title||""));
  res.redirect("/admin");
});
router.post("/announcements/:id/delete",requireAdmin,(req,res)=>{
  const item=db.prepare("SELECT title FROM announcements WHERE id=?").get(Number(req.params.id));
  db.prepare("DELETE FROM announcements WHERE id=?").run(Number(req.params.id));
  logAdmin(req,"announcement.delete",item?.title||req.params.id);
  res.redirect("/admin");
});

router.get("/pages",requireAdmin,(req,res)=>{
  const pages=db.prepare("SELECT * FROM pages ORDER BY slug").all();
  res.render("admin-pages",{pages,settings:settings()});
});
router.post("/pages",requireAdmin,(req,res)=>{
  const title=String(req.body.title||"").trim();
  const slug=cleanSlug(req.body.slug||title);
  if(!title||!slug) return res.status(400).send("Page title and slug are required.");
  try {
    db.prepare("INSERT INTO pages(slug,title,body,published) VALUES(?,?,?,?)").run(slug,title,String(req.body.body||""),req.body.published?1:0);
    logAdmin(req,"page.create",slug);
    res.redirect("/admin/pages");
  } catch(error) {
    if(String(error.message).includes("UNIQUE")) return res.status(409).send("A page with that slug already exists.");
    throw error;
  }
});
router.get("/pages/:id/edit",requireAdmin,(req,res)=>{
  const page=db.prepare("SELECT * FROM pages WHERE id=?").get(Number(req.params.id));
  if(!page) return res.redirect("/admin/pages");
  res.render("admin-edit-page",{page,settings:settings()});
});
router.post("/pages/:id/edit",requireAdmin,(req,res)=>{
  const id=Number(req.params.id);
  const existing=db.prepare("SELECT slug FROM pages WHERE id=?").get(id);
  if(!existing) return res.redirect("/admin/pages");
  const title=String(req.body.title||"").trim();
  const slug=cleanSlug(req.body.slug||title);
  if(!title||!slug) return res.status(400).send("Page title and slug are required.");
  if(CORE_PAGES.has(existing.slug)&&slug!==existing.slug) return res.status(400).send("Core page slugs cannot be renamed.");
  try {
    db.prepare("UPDATE pages SET slug=?,title=?,body=?,published=?,updated_at=CURRENT_TIMESTAMP WHERE id=?").run(slug,title,String(req.body.body||""),req.body.published==="1"?1:0,id);
    logAdmin(req,"page.update",slug);
    res.redirect("/admin/pages");
  } catch(error) {
    if(String(error.message).includes("UNIQUE")) return res.status(409).send("A page with that slug already exists.");
    throw error;
  }
});
router.post("/pages/:id/delete",requireAdmin,(req,res)=>{
  const page=db.prepare("SELECT slug FROM pages WHERE id=?").get(Number(req.params.id));
  if(page&&CORE_PAGES.has(page.slug)) return res.status(400).send("Core pages cannot be deleted; unpublish them instead.");
  db.prepare("DELETE FROM pages WHERE id=?").run(Number(req.params.id));
  logAdmin(req,"page.delete",page?.slug||req.params.id);
  res.redirect("/admin/pages");
});

module.exports=router;
