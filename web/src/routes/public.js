const express = require("express");
const { z } = require("zod");
const { db, settings } = require("../db/cms");
const game = require("../services/gameService");
const env = require("../config/env");
const jobName = require("../utils/jobs");

const router = express.Router();

router.get("/", async (req,res) => {
  const posts = db.prepare("SELECT * FROM posts WHERE published=1 ORDER BY created_at DESC LIMIT 5").all();
  let status={online:false,channels:0,totalChannels:env.game.channelPorts.length}, players=null, topCharacters=[];
  try { status=await game.serverStatus(); } catch {}
  try { players=await game.onlineCount(); } catch {}
  try { topCharacters=(await game.rankings(5)).map(r=>({...r,jobName:jobName(r.job)})); } catch {}
  res.render("home",{posts,status,players,topCharacters,settings:settings()});
});

router.get("/news", (req,res) => {
  const posts = db.prepare("SELECT * FROM posts WHERE published=1 ORDER BY created_at DESC").all();
  res.render("news",{posts,settings:settings()});
});

router.get("/news/:slug", (req,res) => {
  const post = db.prepare("SELECT * FROM posts WHERE slug=? AND published=1").get(req.params.slug);
  if (!post) return res.status(404).render("404",{settings:settings()});
  res.render("post",{post,settings:settings()});
});

const JOB_CLASSES = {
  overall: {label:"Overall", range:null},
  warrior: {label:"Warrior", range:[100,200]},
  magician: {label:"Magician", range:[200,300]},
  bowman: {label:"Bowman", range:[300,400]},
  thief: {label:"Thief", range:[400,500]},
  pirate: {label:"Pirate", range:[500,600]}
};
const RANKINGS_PAGE_SIZE = 10;

router.get("/rankings", async (req,res) => {
  let rows=[], error="";
  const cls = JOB_CLASSES[req.query.class] ? req.query.class : "overall";
  const page = Math.max(1, parseInt(req.query.page,10) || 1);
  try { rows = await game.rankings(100, JOB_CLASSES[cls].range); } catch(e) { error="Rankings are temporarily unavailable."; }
  rows=rows.map(r=>({...r,jobName:jobName(r.job)}));
  const totalPages = Math.max(1, Math.ceil(rows.length / RANKINGS_PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const pageRows = rows.slice((currentPage-1)*RANKINGS_PAGE_SIZE, currentPage*RANKINGS_PAGE_SIZE);
  res.render("rankings",{rows:pageRows,error,settings:settings(),classes:JOB_CLASSES,activeClass:cls,currentPage,totalPages,startRank:(currentPage-1)*RANKINGS_PAGE_SIZE});
});

router.get("/downloads", (req,res) => {
  const rows = db.prepare("SELECT * FROM downloads WHERE published=1 ORDER BY created_at DESC").all();
  res.render("downloads",{rows,settings:settings()});
});

router.get("/support", (req,res) => res.render("support",{settings:settings()}));
router.get("/community", (req,res) => res.render("community",{settings:settings()}));
router.get("/help", (req,res) => res.render("help",{settings:settings()}));
router.get("/terms", (req,res) => res.render("terms",{settings:settings()}));

router.get("/login", (req,res) => res.render("login",{error:"",settings:settings()}));
router.post("/login", async (req,res) => {
  const schema=z.object({username:z.string().min(3).max(20),password:z.string().min(4).max(100)});
  const parsed=schema.safeParse(req.body);
  if(!parsed.success) return res.status(400).render("login",{error:"Invalid username or password.",settings:settings()});
  try {
    const account=await game.login(parsed.data.username,parsed.data.password);
    if(!account) return res.status(401).render("login",{error:"Invalid username or password.",settings:settings()});
    req.session.player=account;
    res.redirect("/account");
  } catch {
    res.status(500).render("login",{error:"Login is temporarily unavailable.",settings:settings()});
  }
});

router.get("/register",(req,res)=>res.render("register",{error:"",enabled:env.registration.enabled,settings:settings()}));
router.post("/register",async(req,res)=>{
  const schema=z.object({
    username:z.string().regex(/^[A-Za-z0-9_]{4,13}$/),
    password:z.string().min(8).max(64),
    confirmPassword:z.string().min(8).max(64),
    email:z.string().email().max(45),
    agree:z.literal("yes")
  }).refine(v=>v.password===v.confirmPassword,{message:"Passwords do not match",path:["confirmPassword"]});
  const parsed=schema.safeParse(req.body);
  if(!parsed.success) return res.status(400).render("register",{error:"Please check the form fields and make sure the passwords match.",enabled:env.registration.enabled,settings:settings()});
  try {
    await game.register(parsed.data);
    res.redirect("/login");
  } catch(e) {
    res.status(400).render("register",{error:e.message.includes("disabled")?e.message:"That username or email may already exist.",enabled:env.registration.enabled,settings:settings()});
  }
});

router.get("/account",async(req,res)=>{
  if(!req.session.player) return res.redirect("/login");
  let characters=[],error="",success=String(req.query.updated||"")==="1"?"Password updated successfully.":"";
  try { characters=(await game.accountCharacters(req.session.player.id)).map(r=>({...r,jobName:jobName(r.job)})); }
  catch { error="Character data is temporarily unavailable."; }
  res.render("account",{account:req.session.player,characters,error,success,settings:settings()});
});

router.post("/account/password",async(req,res)=>{
  if(!req.session.player) return res.redirect("/login");
  const schema=z.object({currentPassword:z.string().min(1).max(100),newPassword:z.string().min(8).max(64),confirmPassword:z.string().min(8).max(64)})
    .refine(v=>v.newPassword===v.confirmPassword,{message:"Passwords do not match",path:["confirmPassword"]});
  const parsed=schema.safeParse(req.body);
  let characters=[];
  try { characters=(await game.accountCharacters(req.session.player.id)).map(r=>({...r,jobName:jobName(r.job)})); } catch {}
  if(!parsed.success) return res.status(400).render("account",{account:req.session.player,characters,error:"Please check the password fields.",success:"",settings:settings()});
  try {
    const ok=await game.changePassword(req.session.player.id,parsed.data.currentPassword,parsed.data.newPassword);
    if(!ok) return res.status(400).render("account",{account:req.session.player,characters,error:"Current password is incorrect.",success:"",settings:settings()});
    res.redirect("/account?updated=1");
  } catch {
    res.status(500).render("account",{account:req.session.player,characters,error:"Password update is temporarily unavailable.",success:"",settings:settings()});
  }
});

router.post("/logout",(req,res)=>req.session.destroy(()=>res.redirect("/")));
router.get("/api/status", async(req,res)=>{
  let status={online:false,channels:0,totalChannels:env.game.channelPorts.length};
  let players=null;
  try { status=await game.serverStatus(); } catch {}
  try { players=await game.onlineCount(); } catch {}
  res.json({...status,players,databaseOnline:players!==null});
});

router.get("/api/launcher/manifest",(req,res)=>{
  const rows=db.prepare("SELECT name,url,kind,version,created_at FROM downloads WHERE published=1 ORDER BY created_at DESC").all();
  res.json({server:env.brand.name,version:env.brand.version,downloads:rows});
});

module.exports = router;
