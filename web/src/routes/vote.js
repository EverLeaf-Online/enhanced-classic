const crypto = require("crypto");
const net = require("net");
const express = require("express");
const env = require("../config/env");
const game = require("../services/gameService");

const router = express.Router();

function secretEqual(received, expected) {
  const left = Buffer.from(String(received || ""), "utf8");
  const right = Buffer.from(String(expected || ""), "utf8");
  if (!left.length || left.length !== right.length) return false;
  return crypto.timingSafeEqual(left, right);
}

function flattenBatchEntry(entry) {
  if (!Array.isArray(entry)) return entry && typeof entry === "object" ? entry : {};
  return Object.assign({}, ...entry.filter(value => value && typeof value === "object"));
}

function normalizeVote(entry, batch=false) {
  const successRaw = batch ? entry.success : entry.Successful;
  const success = Number.isFinite(Number(successRaw)) ? Math.abs(Number(successRaw)) : 1;
  const username = String(batch ? (entry.pb_name || "") : (entry.pingUsername || "")).trim();
  const rawIp = String(batch ? (entry.ip || "") : (entry.VoterIP || "")).trim();
  return {
    username,
    voterIp: net.isIP(rawIp) ? rawIp : null,
    success,
    reason: String(batch ? (entry.reason || "") : (entry.Reason || "")).slice(0, 255)
  };
}

function parsePingback(body) {
  if (!body || typeof body !== "object") return { key:"", votes:[] };
  if (Array.isArray(body.Common)) {
    return {
      key: body.pingbackkey || "",
      votes: body.Common.map(flattenBatchEntry).map(entry => normalizeVote(entry, true))
    };
  }
  return { key: body.pingbackkey || "", votes:[normalizeVote(body, false)] };
}

function verifiedVoteUrl(username) {
  const url = new URL(env.vote.gtopVoteUrl);
  const host = url.hostname.toLowerCase();
  if (url.protocol !== "https:" || !["gtop100.com", "www.gtop100.com"].includes(host)) {
    throw new Error("GTOP100_VOTE_URL must be an HTTPS gtop100.com URL");
  }
  url.searchParams.set("pingUsername", username);
  return url.toString();
}

router.get("/vote", (req,res) => {
  if (!req.session.player) return res.redirect("/login");
  try {
    return res.redirect(302, verifiedVoteUrl(req.session.player.name));
  } catch (error) {
    console.error("Vote URL configuration error:", error.message);
    return res.status(503).send("Voting is temporarily unavailable.");
  }
});

router.get("/api/vote/pingback", (req,res) => {
  res.json({
    status: env.vote.gtopPingbackKey ? "configured" : "not_configured",
    provider: env.vote.provider,
    reward: { votePoints: env.vote.rewardPoints },
    nxReward: false
  });
});

router.post("/api/vote/pingback", async (req,res) => {
  if (!env.vote.gtopPingbackKey) {
    console.error("GTop100 pingback rejected: GTOP100_PINGBACK_KEY is not configured");
    return res.status(503).json({ ok:false, error:"vote_pingback_not_configured" });
  }

  const parsed = parsePingback(req.body);
  if (!secretEqual(parsed.key, env.vote.gtopPingbackKey)) {
    return res.status(403).json({ ok:false, error:"invalid_pingback_key" });
  }
  if (!parsed.votes.length) {
    return res.status(400).json({ ok:false, error:"empty_pingback" });
  }

  const results = [];
  try {
    for (const vote of parsed.votes) {
      // GTop100 uses Successful=0 for a completed vote. Failed/error callbacks
      // are acknowledged but never rewarded.
      if (vote.success !== 0) {
        results.push({ username:vote.username || null, status:"provider_rejected", rewarded:false });
        continue;
      }
      const result = await game.rewardVerifiedVote({
        username: vote.username,
        provider: env.vote.provider,
        voterIp: vote.voterIp,
        reason: vote.reason,
        rewardPoints: env.vote.rewardPoints,
        votedAt: new Date()
      });
      results.push({ username:vote.username || null, status:result.status, rewarded:result.rewarded, amount:result.amount || 0 });
    }
  } catch (error) {
    console.error("GTop100 Vote Point reward error:", error.message);
    return res.status(500).json({ ok:false, error:"vote_reward_failed" });
  }

  return res.status(200).json({
    ok:true,
    processed:results.length,
    rewarded:results.filter(result => result.rewarded).length,
    results
  });
});

module.exports = router;
module.exports._test = { secretEqual, flattenBatchEntry, normalizeVote, parsePingback, verifiedVoteUrl };
