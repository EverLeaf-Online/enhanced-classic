const crypto = require("node:crypto");
function csrf(req,res,next) {
  if(!req.session.csrfToken) req.session.csrfToken=crypto.randomBytes(32).toString("hex");
  res.locals.csrfToken=req.session.csrfToken;
  if(["GET","HEAD","OPTIONS"].includes(req.method)) return next();
  const supplied=req.body?._csrf || req.get("X-CSRF-Token");
  const expected=req.session.csrfToken;
  if(typeof supplied!=="string" || !/^[a-f0-9]{64}$/.test(supplied) || supplied.length!==expected.length ||
      !crypto.timingSafeEqual(Buffer.from(supplied),Buffer.from(expected))) {
    return res.status(403).send("Your form expired. Reload the page and try again.");
  }
  next();
}
module.exports=csrf;
