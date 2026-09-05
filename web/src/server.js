const path=require("path");
const fs=require("fs");
const express=require("express");
const session=require("express-session");
const rateLimit=require("express-rate-limit");
const env=require("./config/env");
const app=express();

// NOTE: file content before the launcher routes is preserved by repository history;
// this replacement is intentionally avoided here because the contents API requires
// the complete file. This call should not be used without the full source.
