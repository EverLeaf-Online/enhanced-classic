const express=require("express");
const {db,settings}=require("../db/cms");
const {requireAdmin}=require("../middleware/auth");

const router=express.Router();
const logAdmin=(req,action,details="")=>db.prepare("INSERT INTO audit_log(admin_id,action,details) VALUES(?,?,?)").run(req.session.admin?.id||null,action,String(details).slice(0,500));

router.get("/news",requireAdmin,(req,res)=>{
  const posts=db.prepare("SELECT * FROM posts ORDER BY created_at DESC").all();
  res.render("admin-news",{posts,settings:settings()});
});

router.get("/settings-view",requireAdmin,(req,res)=>{
  res.render("admin-settings",{site:settings(),settings:settings()});
});

router.get("/audit",requireAdmin,(req,res)=>{
  const page=Math.max(1,Number(req.query.page||1));
  const pageSize=50;
  const total=Number(db.prepare("SELECT COUNT(*) count FROM audit_log").get().count||0);
  const totalPages=Math.max(1,Math.ceil(total/pageSize));
  const currentPage=Math.min(page,totalPages);
  const rows=db.prepare("SELECT audit_log.*,admins.username admin_name FROM audit_log LEFT JOIN admins ON admins.id=audit_log.admin_id ORDER BY audit_log.id DESC LIMIT ? OFFSET ?").all(pageSize,(currentPage-1)*pageSize);
  res.render("admin-audit",{rows,currentPage,totalPages,total,settings:settings()});
});

router.get("/recoveries",requireAdmin,(req,res)=>{
  const status=["pending","resolved","rejected"].includes(String(req.query.status||""))?String(req.query.status):"pending";
  const rows=db.prepare("SELECT * FROM account_recovery_requests WHERE status=? ORDER BY created_at DESC LIMIT 200").all(status);
  const counts=Object.fromEntries(db.prepare("SELECT status,COUNT(*) count FROM account_recovery_requests GROUP BY status").all().map(row=>[row.status,row.count]));
  res.render("admin-recoveries",{rows,status,counts,settings:settings()});
});

router.post("/recoveries/:id/status",requireAdmin,(req,res)=>{
  const id=Number(req.params.id);
  const status=["pending","resolved","rejected"].includes(String(req.body.status||""))?String(req.body.status):null;
  if(!Number.isInteger(id)||id<1||!status) return res.status(400).send("Invalid recovery update.");
  const item=db.prepare("SELECT id,username,email,status FROM account_recovery_requests WHERE id=?").get(id);
  if(!item) return res.redirect("/admin/recoveries");
  db.prepare("UPDATE account_recovery_requests SET status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?").run(status,id);
  logAdmin(req,"recovery.update",`${id}:${item.status}->${status}`);
  res.redirect(`/admin/recoveries?status=${encodeURIComponent(status==='pending'?'pending':status)}`);
});

module.exports=router;
