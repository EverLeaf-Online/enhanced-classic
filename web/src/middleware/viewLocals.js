module.exports=(req,res,next)=>{res.locals.sessionPlayer=req.session?.player||null;res.locals.currentPath=req.path;next();};
