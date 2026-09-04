const express = require("express");
const env = require("../config/env");
const appearances = require("../services/avatarAppearanceService");
const jobName = require("../utils/jobs");

const router = express.Router();
const cache = new Map();
const MAX_CACHE_ENTRIES = 500;

function fallbackAsset(job=0) {
  const n = String(jobName(Number(job) || 0) || "").toLowerCase();
  if (/beginner|legend/.test(n)) return "/assets/jobs/beginner/beginner-clean.png";
  if (/aran/.test(n)) return "/assets/jobs/special/aran.png";
  if (/evan/.test(n)) return "/assets/jobs/special/evan.png";
  if (/dawn warrior/.test(n)) return "/assets/jobs/cygnus/dawn-warrior.png";
  if (/blaze wizard/.test(n)) return "/assets/jobs/cygnus/blaze-wizard.png";
  if (/wind archer/.test(n)) return "/assets/jobs/cygnus/wind-archer.png";
  if (/night walker/.test(n)) return "/assets/jobs/cygnus/night-walker.png";
  if (/thunder breaker/.test(n)) return "/assets/jobs/cygnus/thunder-breaker.png";
  if (/cygnus|noblesse/.test(n)) return "/assets/jobs/special/cygnus-clean.png";
  if (/warrior|fighter|crusader|hero|page|white knight|paladin|spearman|dragon knight|dark knight/.test(n)) return "/assets/jobs/instructors/warrior.png";
  if (/magician|wizard|mage|cleric|priest|bishop/.test(n)) return "/assets/jobs/instructors/magician.png";
  if (/bowman|archer|hunter|ranger|bowmaster|crossbow|sniper|marksman/.test(n)) return "/assets/jobs/instructors/bowman.png";
  if (/thief|rogue|assassin|hermit|night lord|bandit|chief bandit|shadower/.test(n)) return "/assets/jobs/instructors/thief.png";
  if (/pirate|brawler|marauder|buccaneer|gunslinger|outlaw|corsair/.test(n)) return "/assets/jobs/instructors/pirate.png";
  return "/assets/everleaf-remaster.svg";
}

function rendererUrl(appearance, includeEquipment=true, version="83") {
  const skin = 2000 + Math.max(0, Number(appearance.skincolor || 0));
  const items = [Number(appearance.face || 0), Number(appearance.hair || 0)];
  if (includeEquipment) items.push(...(appearance.equipment || []).map(Number));
  const ids = [...new Set(items.filter(id => Number.isInteger(id) && id > 0))];
  return `${env.avatar.baseUrl}/api/${encodeURIComponent(env.avatar.region)}/${encodeURIComponent(version)}/Character/center/${skin}/${ids.join(",")}/stand1/0?resize=2&padding=6`;
}

function rendererVersions() {
  return [...new Set(["83", String(env.avatar.version || "").trim()].filter(Boolean))];
}

async function fetchAvatar(url) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 5000);
  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: { "User-Agent": "EverLeafMS-Website/1.0" }
    });
    if (!response.ok) throw new Error(`renderer returned ${response.status}`);
    const type = String(response.headers.get("content-type") || "").toLowerCase();
    if (!type.startsWith("image/")) throw new Error("renderer did not return an image");
    const bytes = Buffer.from(await response.arrayBuffer());
    if (!bytes.length) throw new Error("renderer returned an empty image");
    return { bytes, type };
  } finally {
    clearTimeout(timer);
  }
}

async function renderAppearance(appearance, includeEquipment) {
  let lastError = null;
  for (const version of rendererVersions()) {
    try {
      return await fetchAvatar(rendererUrl(appearance,includeEquipment,version));
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError || new Error("no character renderer version is configured");
}

function cacheSet(id, value) {
  if (cache.size >= MAX_CACHE_ENTRIES) {
    const oldest = cache.keys().next().value;
    if (oldest !== undefined) cache.delete(oldest);
  }
  cache.set(id, { ...value, expiresAt: Date.now() + env.avatar.cacheMs });
}

function redirectFallback(res,job=0) {
  res.set("Cache-Control","public, max-age=60, stale-while-revalidate=300");
  res.set("X-EverLeaf-Avatar-Source","fallback");
  return res.redirect(302,fallbackAsset(job));
}

router.get("/character-avatar/:id.png", async (req,res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id <= 0) return res.status(404).end();

  const cached = cache.get(id);
  if (cached && cached.expiresAt > Date.now()) {
    res.set("Content-Type",cached.type);
    res.set("Cache-Control","public, max-age=300, stale-while-revalidate=3600");
    res.set("X-EverLeaf-Avatar-Source","renderer-cache");
    return res.send(cached.bytes);
  }
  if (cached) cache.delete(id);

  let appearance;
  try {
    appearance = await appearances.characterAppearance(id);
  } catch (error) {
    console.warn(`Character avatar DB lookup failed for ${id}:`,error.message);
    return redirectFallback(res,Number(req.query.job) || 0);
  }
  if (!appearance) return res.status(404).end();

  let image = null;
  try {
    image = await renderAppearance(appearance,true);
  } catch (fullError) {
    try {
      image = await renderAppearance(appearance,false);
    } catch (baseError) {
      console.warn(`Character avatar render failed for ${id}:`,fullError.message,"/",baseError.message);
    }
  }

  if (!image) return redirectFallback(res,appearance.job);
  cacheSet(id,image);
  res.set("Content-Type",image.type);
  res.set("Cache-Control","public, max-age=300, stale-while-revalidate=3600");
  res.set("X-EverLeaf-Avatar-Source","renderer");
  return res.send(image.bytes);
});

module.exports = router;
module.exports._test = { fallbackAsset, rendererUrl, rendererVersions };
