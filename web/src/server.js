const express=require("express");
const session=require("express-session");
const helmet=require("helmet");
const compression=require("compression");
const rateLimit=require("express-rate-limit");
const path=require("path");
const fs=require("fs");
const env=require("./config/env");
const {initCms,settings}=require("./db/cms");

initCms();

const app=express();
if(env.trustProxy) app.set("trust proxy",env.trustProxy);
app.set("view engine","ejs");
app.set("views",path.join(__dirname,"views"));

app.use(helmet({contentSecurityPolicy:false}));
app.use(compression());
// Provider signatures must be verified against the exact request bytes.
app.use("/webhooks",require("./routes/webhooks"));
app.use(express.urlencoded({extended:false,limit:"50kb"}));
app.use(express.json({limit:"50kb"}));
app.use(express.static(path.join(__dirname,"../public"),{maxAge:env.nodeEnv==="production"?"1h":0}));
app.use(rateLimit({windowMs:60_000,max:120,standardHeaders:true,legacyHeaders:false}));

// Launcher endpoints are intentionally session-free. The manifest is signed and
// patch payloads are SHA-256 verified by the launcher before replacement.
app.use("/v1/launcher",require("./routes/launcher"));
app.use("/patches",express.static(env.launcher.filesRoot,{
  fallthrough:false,
  index:false,
  etag:true,
  lastModified:true,
  setHeaders(res){res.setHeader("Cache-Control","no-cache");}
}));
app.get("/launcher/download",(req,res)=>{
  if(!fs.existsSync(env.launcher.portablePath))
    return res.status(503).send("EverLeaf portable launcher is not published yet.");
  res.set("Cache-Control","no-cache");
  res.download(env.launcher.portablePath,"EverLeafLauncher-portable.zip");
});

app.use(session({
  secret:env.sessionSecret,
  resave:false,
  saveUninitialized:false,
  cookie:{
    httpOnly:true,
    secure:env.cookieSecure,
    sameSite:"lax",
    maxAge:1000*60*60*12
  }
}));

app.locals.brand=env.brand;
app.locals.year=new Date().getFullYear();
app.use(require("./middleware/viewLocals"));

app.use("/",require("./routes/public"));
app.use("/admin",require("./routes/admin"));

app.use((req,res)=>res.status(404).render("404",{settings:settings()}));

app.listen(env.port,()=>console.log(`EverLeaf web running on port ${env.port}`));
