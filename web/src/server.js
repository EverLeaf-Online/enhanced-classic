const express=require("express");
const session=require("express-session");
const helmet=require("helmet");
const compression=require("compression");
const rateLimit=require("express-rate-limit");
const path=require("path");
const env=require("./config/env");
const {initCms,settings}=require("./db/cms");

initCms();

const app=express();
if(env.trustProxy) app.set("trust proxy",env.trustProxy);
app.set("view engine","ejs");
app.set("views",path.join(__dirname,"views"));

app.use(helmet({contentSecurityPolicy:false}));
app.use(compression());
app.use(express.urlencoded({extended:false,limit:"50kb"}));
app.use(express.json({limit:"50kb"}));
app.use(express.static(path.join(__dirname,"../public"),{maxAge:env.nodeEnv==="production"?"1h":0}));
app.use(rateLimit({windowMs:60_000,max:120,standardHeaders:true,legacyHeaders:false}));

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

app.use("/",require("./routes/vote"));
app.use("/",require("./routes/public"));
app.use("/admin",require("./routes/admin"));

app.use((req,res)=>res.status(404).render("404",{settings:settings()}));

app.listen(env.port,()=>console.log(`EverLeaf web running on port ${env.port}`));