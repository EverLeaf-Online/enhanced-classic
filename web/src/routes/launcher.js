const express = require("express");
const fs = require("fs");
const crypto = require("crypto");
const env = require("../config/env");
const game = require("../services/gameService");

const router = express.Router();

router.get("/status", async (req, res) => {
  let online = false;
  try {
    const status = await game.serverStatus();
    online = Boolean(status.online);
  } catch {}

  res.set("Cache-Control", "no-store");
  res.json({
    online,
    message: env.launcher.announcement,
    version: env.brand.version
  });
});

router.get("/manifest", (req, res) => {
  try {
    if (!fs.existsSync(env.launcher.manifestPath))
      return res.status(503).json({error:"Patch manifest is not published yet."});
    if (!fs.existsSync(env.launcher.signingKeyPath))
      return res.status(503).json({error:"Patch signing key is not provisioned."});

    // Sign the exact bytes served as the payload. The launcher verifies this
    // signature before parsing or acting on any file entry.
    const payload = fs.readFileSync(env.launcher.manifestPath);
    JSON.parse(payload.toString("utf8"));
    const privateKey = fs.readFileSync(env.launcher.signingKeyPath, "utf8");
    const signature = crypto.sign("sha256", payload, {
      key: privateKey,
      padding: crypto.constants.RSA_PKCS1_PSS_PADDING,
      saltLength: 32
    });

    res.set("Cache-Control", "no-store");
    res.json({
      payload: payload.toString("base64"),
      signature: signature.toString("base64")
    });
  } catch (error) {
    console.error("Launcher manifest error:", error.message);
    res.status(503).json({error:"Patch manifest is temporarily unavailable."});
  }
});

module.exports = router;
