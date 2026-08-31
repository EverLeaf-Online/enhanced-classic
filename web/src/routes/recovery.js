const express=require("express");
const {z}=require("zod");
const {db,settings}=require("../db/cms");

const router=express.Router();
const recoverySchema=z.object({
  username:z.string().trim().max(20).optional().default(""),
  email:z.string().trim().max(254).optional().default("")
}).refine(value=>value.username.length>=3||z.string().email().safeParse(value.email).success,{message:"Enter your username or account email."});

router.get("/recover",(req,res)=>res.render("recover",{error:"",submitted:false,settings:settings()}));
router.post("/recover",(req,res)=>{
  const parsed=recoverySchema.safeParse(req.body);
  if(!parsed.success) return res.status(400).render("recover",{error:"Enter a valid username or account email.",submitted:false,settings:settings()});
  const username=parsed.data.username.slice(0,20);
  const email=parsed.data.email.toLowerCase().slice(0,254);
  const duplicate=db.prepare(`SELECT id FROM account_recovery_requests
    WHERE status='pending' AND created_at>=datetime('now','-1 day')
      AND ((username<>'' AND username=?) OR (email<>'' AND email=?)) LIMIT 1`).get(username,email);
  if(!duplicate) db.prepare("INSERT INTO account_recovery_requests(username,email) VALUES(?,?)").run(username,email);
  // Always return the same response so the form cannot be used to enumerate accounts.
  res.render("recover",{error:"",submitted:true,settings:settings()});
});

module.exports=router;
