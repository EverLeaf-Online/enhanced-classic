const express = require("express");
const fs = require("fs");
const path = require("path");
const env = require("../config/env");
const appearances = require("../services/avatarAppearanceService");
const jobName = require("../utils/jobs");

const router = express.Router();
const cache = new Map();
const MAX_CACHE_ENTRIES = 500;
const PUBLIC_ROOT = path.resolve(__dirname,"../../public");
const LOCAL_RENDERER_EQUIP_PREFIXES = new Set([
  100,101,102,103,104,105,106,107,108,109,110,170
]);

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

function wzId(value) {
  const n = Number(value);
  if (!Number.isInteger(n) || n <= 0) return null;
  return String(n).padStart(8,"0");
}

function localRenderableEquipmentId(value) {
  const n = Number(value);
  if (!Number.isInteger(n) || n <= 0) return false;
  const prefix = Math.trunc(n / 10000);
  return LOCAL_RENDERER_EQUIP_PREFIXES.has(prefix) || (prefix >= 121 && prefix <= 160);
}

function localRendererEquipmentIds(appearance) {
  return [...new Set((appearance.equipment || [])
    .map(Number)
    .filter(localRenderableEquipmentId))];
}

function localRendererIds(appearance, includeEquipment=true) {
  const skin = Math.max(0, Number(appearance.skincolor || 0));
  const ids = [
    2000 + skin,
    12000 + skin,
    Number(appearance.hair || 0),
    Number(appearance.face || 0)
  ];
  if (includeEquipment) ids.push(...localRendererEquipmentIds(appearance));
  return [...new Set(ids.map(wzId).filter(Boolean))];
}

function localRendererUrl(appearance, includeEquipment=true) {
  const params = new URLSearchParams({
    ids: localRendererIds(appearance,includeEquipment).join(","),
    pose: "stand1",
    frame: "0",
    scale: "2"
  });
  return `${env.avatar.localBaseUrl}/api/character/compose?${params.toString()}`;
}

function remoteRendererUrl(appearance, includeEquipment=true, version="83") {
  const skin = 2000 + Math.max(0, Number(appearance.skincolor || 0));
  const items = [Number(appearance.face || 0), Number(appearance.hair || 0)];
  if (includeEquipment) items.push(...(appearance.equipment || []).map(Number));
  const ids = [...new Set(items.filter(id => Number.isInteger(id) && id > 0))];
  return `${env.avatar.remoteBaseUrl}/api/${encodeURIComponent(env.avatar.region)}/${encodeURIComponent(version)}/Character/center/${skin}/${ids.join(",")}/stand1/0?resize=2&padding=6`;
}

function remoteRendererVersions() {
  return [...new Set(["83", String(env.avatar.version || "").trim()].filter(Boolean))];
}

async function fetchAvatar(url, source, timeoutMs=8000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(),timeoutMs);
  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: { "User-Agent": "EverLeafMS-Website/1.0" }
    });
    if (!response.ok) throw new Error(`${source} returned ${response.status}`);
    const type = String(response.headers.get("content-type") || "").toLowerCase();
    if (!type.startsWith("image/")) throw new Error(`${source} did not return an image`);
    const bytes = Buffer.from(await response.arrayBuffer());
    if (bytes.length < 100) throw new Error(`${source} returned an unexpectedly small image`);
    return { bytes, type, source };
  } finally {
    clearTimeout(timer);
  }
}

async function renderAppearance(appearance, includeEquipment) {
  let localError = null;
  const localSource = includeEquipment ? "local-wz" : "local-wz-base";
  try {
    const image = await fetchAvatar(localRendererUrl(appearance,includeEquipment),localSource,20_000);
    return {
      ...image,
      mode:includeEquipment ? "full" : "base-fallback",
      equipmentCount:includeEquipment ? localRendererEquipmentIds(appearance).length : 0
    };
  } catch (error) {
    localError = error;
  }

  // External rendering is intentionally opt-in only. Production normally has
  // no MAPLESTORY_IO_BASE_URL because EverLeaf renders from its own v83 WZ.
  if (env.avatar.remoteBaseUrl) {
    let remoteError = null;
    for (const version of remoteRendererVersions()) {
      try {
        const image = await fetchAvatar(remoteRendererUrl(appearance,includeEquipment,version),"external-renderer",8_000);
        return {
          ...image,
          mode:includeEquipment ? "full" : "base-fallback",
          equipmentCount:includeEquipment ? (appearance.equipment || []).length : 0
        };
      } catch (error) {
        remoteError = error;
      }
    }
    throw remoteError || localError || new Error("no character renderer is available");
  }

  throw localError || new Error("local WZ character renderer is unavailable");
}

function cacheSet(id, value) {
  if (cache.size >= MAX_CACHE_ENTRIES) {
    const oldest = cache.keys().next().value;
    if (oldest !== undefined) cache.delete(oldest);
  }
  cache.set(id, { ...value, expiresAt: Date.now() + env.avatar.cacheMs });
}

function setAvatarHeaders(res,image) {
  res.set("Content-Type",image.type);
  res.set("X-EverLeaf-Avatar-Source",image.source);
  res.set("X-EverLeaf-Avatar-Mode",image.mode || "unknown");
  res.set("X-EverLeaf-Avatar-Equipment-Count",String(Number(image.equipmentCount || 0)));
}

function sendFallback(res,job=0) {
  const asset = fallbackAsset(job);
  const file = path.resolve(PUBLIC_ROOT,asset.replace(/^\/+/,""));
  if (!file.startsWith(`${PUBLIC_ROOT}${path.sep}`) || !fs.existsSync(file)) {
    return res.status(503).end();
  }
  res.set("Cache-Control","public, max-age=60, stale-while-revalidate=300");
  res.set("X-EverLeaf-Avatar-Source","fallback");
  res.set("X-EverLeaf-Avatar-Mode","class-fallback");
  res.set("X-EverLeaf-Avatar-Equipment-Count","0");
  return res.sendFile(file);
}

router.get("/character-avatar/:id.png", async (req,res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id <= 0) return res.status(404).end();

  const cached = cache.get(id);
  if (cached && cached.expiresAt > Date.now()) {
    setAvatarHeaders(res,{ ...cached, source:`${cached.source}-cache` });
    res.set("Cache-Control","public, max-age=300, stale-while-revalidate=3600");
    return res.send(cached.bytes);
  }
  if (cached) cache.delete(id);

  let appearance;
  try {
    appearance = await appearances.characterAppearance(id);
  } catch (error) {
    console.warn(`Character avatar DB lookup failed for ${id}:`,error.message);
    return sendFallback(res,Number(req.query.job) || 0);
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

  if (!image) return sendFallback(res,appearance.job);
  cacheSet(id,image);
  setAvatarHeaders(res,image);
  res.set("Cache-Control","public, max-age=300, stale-while-revalidate=3600");
  return res.send(image.bytes);
});

module.exports = router;
module.exports._test = {
  fallbackAsset,
  wzId,
  localRenderableEquipmentId,
  localRendererEquipmentIds,
  localRendererIds,
  localRendererUrl,
  remoteRendererUrl,
  remoteRendererVersions
};
