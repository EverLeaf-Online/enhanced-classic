const {db}=require("../db/cms");

module.exports=(req,res,next)=>{
  const player=req.session?.player||null;
  res.locals.player=player;
  res.locals.sessionPlayer=player;
  res.locals.currentPath=req.path;
  try {
    res.locals.activeAnnouncement=db.prepare("SELECT title,body FROM announcements WHERE active=1 ORDER BY id DESC LIMIT 1").get()||null;
  } catch {
    res.locals.activeAnnouncement=null;
  }
  next();
};
