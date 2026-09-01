const express=require("express");
const {settings}=require("../db/cms");
const router=express.Router();

router.get("/wiki",(req,res)=>res.render("wiki",{settings:settings()}));

module.exports=router;
