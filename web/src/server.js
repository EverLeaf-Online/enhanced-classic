const express=require("express");
const session=require("express-session");
const helmet=require("helmet");
const compression=require("compression");
const rateLimit=require("express-rate-limit");
const path=require("path");
const fs=require("fs");
const env=require("./config/env");
const {initCms,settings}=require("./db/cms");

if(env.nodeEnv==="production"&&env.sessionSecret==="dev-only-change-me") {
  throw new Error("SESSION_SECRET must be configured in production.");
}

initCms();

const app=express();
app.disable("x-powered-by");
if(env.trustProxy) app.set("trust proxy",env.trustProxy);
app.set("view engine","ejs");
app.set("views",path.join(__dirname,"views"));

app.use(helmet({
  contentSecurityPolicy:{
    directives:{
      defaultSrc:["'self'"],
      baseUri:["'self'"],
      formAction:["'self'"],
      frameAncestors:["'none'"],
      objectSrc:["'none'"],
      scriptSrc:["'self'","'unsafe-inline'"],
      styleSrc:["'self'","'unsafe-inline'"],
      imgSrc:["'self'","data:"],
      connectSrc:["'self'"]
    }
  },
  referrerPolicy:{policy:"strict-origin-when-cross-origin"}
}));
app.use(compression());
app.use("/webhooks",require("./routes/webhooks"));
app.use(express.urlencoded({extended:false,limit:"50kb"}));
app.use(express.json({limit:"50kb"}));
app.use(express.static(path.join(__dirname,"../public"),{maxAge:env.nodeEnv==="production"?"1h":0}));
app.use(rateLimit({windowMs:60_000,max:120,standardHeaders:true,legacyHeaders:false}));

const authLimiter=rateLimit({
  windowMs:15*60_000,
  max:12,
  standardHeaders:true,
  legacyHeaders:false,
  skip:req=>req.method!=="POST",
  message:"Too many authentication or recovery attempts. Please wait a few minutes and try again."
});
app.use(["/login","/register","/recover","/admin/login"],authLimiter);

app.use("/v1/launcher",require("./routes/launcher"));
app.get("/patches/manifest.json",(req,res,next)=>{
  res.setHeader("Cache-Control","no-cache");
  res.sendFile(env.launcher.manifestPath,error=>{
    if(error) next(error);
  });
});
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

// Isolated compatibility package for the Yuna-based EverLeaf client migration.
// Keep this outside the signed production patch manifest until Windows runtime QA
// proves login -> world -> character -> channel -> map on the EverLeaf server.
app.get("/client-tests/yuna-runtime",(req,res)=>{
  const testPackage=path.join(path.dirname(env.launcher.portablePath),"EverLeaf-YunaRuntime-Test.zip");
  if(!fs.existsSync(testPackage))
    return res.status(503).send("EverLeaf Yuna runtime test package is not published yet.");
  res.set("Cache-Control","no-cache");
  res.download(testPackage,"EverLeaf-YunaRuntime-Test.zip");
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

app.use((req,res,next)=>{
  const sensitive=req.path==="/login"||req.path==="/register"||req.path==="/recover"||req.path.startsWith("/account")||req.path.startsWith("/admin");
  if(sensitive) res.set("Cache-Control","no-store");
  next();
});

app.locals.brand=env.brand;
app.locals.siteUrl=env.payments.publicBaseUrl;
app.locals.siteDescription="EverLeaf is an Enhanced Classic MapleStory v83 server focused on nostalgia, thoughtful quality-of-life improvements, long-term progression, and no pay-to-win.";
app.locals.year=new Date().getFullYear();
app.use(require("./middleware/viewLocals"));

app.use("/",require("./routes/avatar"));
app.use("/",require("./routes/vote"));
app.use("/",require("./routes/recovery"));
app.use("/",require("./routes/wiki"));
app.use("/",require("./routes/public"));
app.use("/admin",require("./routes/admin-knowledge"));
app.use("/admin",require("./routes/admin-content"));
app.use("/admin",require("./routes/admin"));

app.use((req,res)=>res.status(404).render("404",{settings:settings()}));
app.use((error,req,res,next)=>{
  console.error("Unhandled web request error:",error);
  if(res.headersSent) return next(error);
  res.status(500).render("500",{settings:settings()});
});

app.listen(env.port,()=>console.log(`EverLeaf web running on port ${env.port}`));
