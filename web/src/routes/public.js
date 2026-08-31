const express = require("express");
const crypto = require("crypto");
const { z } = require("zod");
const { db, settings } = require("../db/cms");
const game = require("../services/gameService");
const env = require("../config/env");
const jobName = require("../utils/jobs");
const passwordPolicy = require("../utils/playerPasswordPolicy");
const supporter = require("../services/supporterService");
const stripe = require("../services/stripeService");
const discord = require("../services/discordService");
const paypal = require("../services/paypalService");

const router = express.Router();
const siteUrl = env.payments.publicBaseUrl;
const xmlEscape = (value) => String(value).replace(/[<>&'\"]/g, ch => ({"<":"&lt;",">":"&gt;","&":"&amp;","'":"&apos;",'\"':"&quot;"}[ch]));

router.get("/robots.txt",(req,res)=>{
  res.type("text/plain").set("Cache-Control","public, max-age=3600").send(`User-agent: *\nAllow: /\nDisallow: /admin\nDisallow: /account\nSitemap: ${siteUrl}/sitemap.xml\n`);
});

router.get("/sitemap.xml",(req,res)=>{
  const staticPaths=["/","/news","/downloads","/rankings","/donate","/help","/terms","/login","/register"];
  const posts=db.prepare("SELECT slug,created_at FROM posts WHERE published=1 ORDER BY created_at DESC").all();
  const entries=staticPaths.map(path=>({loc:`${siteUrl}${path}`,lastmod:null})).concat(posts.map(post=>({loc:`${siteUrl}/news/${encodeURIComponent(post.slug)}`,lastmod:post.created_at?String(post.created_at).slice(0,10):null})));
  const body=entries.map(entry=>`<url><loc>${xmlEscape(entry.loc)}</loc>${entry.lastmod?`<lastmod>${xmlEscape(entry.lastmod)}</lastmod>`:""}</url>`).join("");
  res.type("application/xml").set("Cache-Control","public, max-age=900").send(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${body}</urlset>`);
});

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

router.get("/support", (req,res) => res.redirect(301,"/donate"));
const paymentProviders = () => ({
  stripe: supporter.providerReady("stripe"),
  paypal: supporter.providerReady("paypal"),
  stripeLabel: env.payments.stripe.environment === "live" ? "Stripe secure checkout" : "Stripe sandbox",
  paypalLabel: env.payments.paypal.environment === "live" ? "PayPal secure checkout" : "PayPal sandbox",
});
router.get("/donate", (req,res) => {
  const summary=req.session.player?supporter.accountSummary(req.session.player.id):{profile:null,orders:[]};
  const notices={success:"Stripe checkout completed. Confirmation is processing.",processing:"PayPal payment submitted. Confirmation is processing.",canceled:"Checkout was canceled; no payment was taken."};
  const notice=notices[String(req.query.checkout||"")]||"";
  const error=String(req.query.checkout||"")==="failed"?"Payment confirmation failed. No supporter credit was applied.":"";
  res.render("support",{settings:settings(),player:req.session.player||null,summary,amounts:supporter.AMOUNTS,providers:paymentProviders(),error,notice});
});
router.post("/donate/checkout", async (req,res) => {
  if(!req.session.player) return res.redirect("/login");
  try {
    const input={provider:String(req.body.provider||""),amountCents:Number(req.body.amountCents),accountId:req.session.player.id,accountName:req.session.player.name};
    supporter.validateCheckout(input);
    const checkout=input.provider==="stripe"?await stripe.createCheckout(input):await paypal.createCheckout(input);
    return res.redirect(303,checkout.url);
  } catch(error) {
    console.warn("Checkout initialization failed:",error.message);
    res.status(503).render("support",{settings:settings(),player:req.session.player,summary:supporter.accountSummary(req.session.player.id),amounts:supporter.AMOUNTS,providers:paymentProviders(),error:"Checkout is temporarily unavailable. No payment was taken.",notice:""});
  }
});
router.get("/donate/paypal/return",async(req,res)=>{
  if(!req.session.player) return res.redirect("/login");
  try {
    await paypal.captureCheckout(String(req.query.token||""),req.session.player.id);
    res.redirect("/donate?checkout=processing");
  } catch(error) {
    console.warn("PayPal capture failed:",error.message);
    res.redirect("/donate?checkout=failed");
  }
});
router.get("/community", (req,res) => res.redirect(302,env.brand.discordUrl));
router.get("/help", (req,res) => res.render("help",{settings:settings()}));
router.get("/terms", (req,res) => res.render("terms",{settings:settings()}));

router.get("/login", (req,res) => res.render("login",{error:"",settings:settings()}));
router.post("/login", async (req,res) => {
  const schema=z.object({username:z.string().min(3).max(20),password:passwordPolicy.loginPassword});
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
  const parsed=passwordPolicy.registrationSchema.safeParse(req.body);
  if(!parsed.success) return res.status(400).render("register",{error:`${passwordPolicy.REQUIREMENT} Please also check that the passwords match and all other fields are valid.`,enabled:env.registration.enabled,settings:settings()});
  try {
    await game.register(parsed.data);
    res.redirect("/login");
  } catch(e) {
    res.status(400).render("register",{error:e.message.includes("disabled")?e.message:"That username or email may already exist.",enabled:env.registration.enabled,settings:settings()});
  }
});

router.get("/account",async(req,res)=>{
  if(!req.session.player) return res.redirect("/login");
  let characters=[],rewards={nxCredit:0,pendingVoteNx:0},error="",success=String(req.query.updated||"")==="1"?"Password updated successfully.":"";
  const discordMessages={linked:"Discord account linked successfully.",invalid:"Discord authorization expired or was invalid.",failed:"Discord account linking failed. Please try again.",unavailable:"Discord account linking is not available yet."};
  if(req.query.discord&&discordMessages[req.query.discord]) success=req.query.discord==="linked"?discordMessages[req.query.discord]:"";
  if(req.query.discord&&req.query.discord!=="linked"&&discordMessages[req.query.discord]) error=discordMessages[req.query.discord];
  try { characters=(await game.accountCharacters(req.session.player.id)).map(r=>({...r,jobName:jobName(r.job)})); }
  catch { error="Character data is temporarily unavailable."; }
  try { rewards=await game.nxRewardStatus(req.session.player.id); }
  catch { if(!error) error="NX reward data is temporarily unavailable."; }
  const discordProfile=supporter.accountSummary(req.session.player.id).profile;
  res.render("account",{account:req.session.player,characters,rewards,error,success,discordProfile,discordReady:discord.oauthReady(),settings:settings()});
});

router.get("/account/discord/connect",(req,res)=>{
  if(!req.session.player) return res.redirect("/login");
  try {
    const state=discord.newState();
    req.session.discordOauthState=state;
    req.session.discordOauthCreatedAt=Date.now();
    res.redirect(discord.authorizationUrl(state));
  } catch {
    res.redirect("/account?discord=unavailable");
  }
});

router.get("/account/discord/callback",async(req,res)=>{
  if(!req.session.player) return res.redirect("/login");
  const expected=req.session.discordOauthState;
  const created=Number(req.session.discordOauthCreatedAt||0);
  delete req.session.discordOauthState;
  delete req.session.discordOauthCreatedAt;
  const expectedBuffer=Buffer.from(String(expected||""));
  const receivedBuffer=Buffer.from(String(req.query.state||""));
  if(!expected||expectedBuffer.length!==receivedBuffer.length||!crypto.timingSafeEqual(expectedBuffer,receivedBuffer)||Date.now()-created>10*60*1000) {
    return res.redirect("/account?discord=invalid");
  }
  try {
    const user=await discord.exchangeCode(String(req.query.code||""));
    supporter.linkDiscordAccount(req.session.player.id,req.session.player.name,user.id);
    await discord.syncAccount(req.session.player.id);
    res.redirect("/account?discord=linked");
  } catch(error) {
    console.warn("Discord account linking failed:",error.message);
    res.redirect("/account?discord=failed");
  }
});

router.post("/account/password",async(req,res)=>{
  if(!req.session.player) return res.redirect("/login");
  const parsed=passwordPolicy.passwordChangeSchema.safeParse(req.body);
  let characters=[];
  try { characters=(await game.accountCharacters(req.session.player.id)).map(r=>({...r,jobName:jobName(r.job)})); } catch {}
  if(!parsed.success) return res.status(400).render("account",{account:req.session.player,characters,error:`${passwordPolicy.REQUIREMENT} Please also check that the new passwords match.`,success:"",settings:settings()});
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
