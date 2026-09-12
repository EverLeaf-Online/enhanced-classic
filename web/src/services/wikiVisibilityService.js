const { db } = require("../db/cms");
const data = require("./wikiDataService");

const VISIBILITY = new Set(["hidden", "visible"]);
const FILTERS = new Set(["all", "visible", "hidden", "automatic-hidden", "manual-hidden", "manual-visible"]);
let revision = 0;
let statsCache = null;

function cleanText(value = "") {
  return String(value)
    .replace(/\s+/g, " ")
    .replace(/^[\s\-–—:|]+|[\s\-–—:|]+$/g, "")
    .trim();
}

function normalizeText(value = "") {
  return cleanText(value)
    .toLowerCase()
    .replace(/#(?:[a-z]|[0-9a-f]{6})/gi, "")
    .replace(/[’'`]/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function automaticDecision(entity) {
  const name = cleanText(entity?.name);
  const description = cleanText(entity?.description);
  if (!name || name.length < 2) return { hidden: true, reason: "Missing or unusable display name" };
  if (/^\d+$/.test(name)) return { hidden: true, reason: "Numeric placeholder name" };
  if (/^[?*_.\-–—\[\](){}]+$/.test(name)) return { hidden: true, reason: "Placeholder punctuation name" };

  const combined = `${name} ${description}`.toLowerCase();
  if (/\[\[\s*frozen\s+content\s*\]\]|\bfrozen\s+content\b/i.test(combined)) {
    return { hidden: true, reason: "Frozen-content marker" };
  }
  if (/\b(?:dummy|placeholder|unused|not\s+used|do\s+not\s+use|dont\s+use|debug)\b/i.test(combined)) {
    return { hidden: true, reason: "Internal/debug marker" };
  }
  if (/^(?:test|sample|reserved)(?:\s+(?:item|mob|monster|npc|map|skill|quest|data))?$/i.test(name)) {
    return { hidden: true, reason: "Generic test/sample record" };
  }
  if (/^zz(?:z+)?\b/i.test(name)) return { hidden: true, reason: "ZZZ/internal naming marker" };
  if (/^(?:\[?gm\]?|game\s*master)(?:\s+(?:only|test|debug|item|scroll|equipment|equip))\b/i.test(name)) {
    return { hidden: true, reason: "GM/internal record" };
  }
  return { hidden: false, reason: "" };
}

function validType(type) {
  return Boolean(data.TYPE_META[String(type || "")]);
}

function validId(id) {
  const value = Number(id);
  return Number.isInteger(value) && value >= 0 ? value : null;
}

function getOverride(type, id) {
  const numericId = validId(id);
  if (!validType(type) || numericId == null) return null;
  try {
    return db.prepare(`
      SELECT entity_type,entity_id,visibility,reason,updated_by,created_at,updated_at
        FROM wiki_entity_visibility
       WHERE entity_type=? AND entity_id=?
       LIMIT 1
    `).get(String(type), numericId) || null;
  } catch (error) {
    if (String(error.message || "").includes("no such table")) return null;
    throw error;
  }
}

function overrideMap(type) {
  if (!validType(type)) return new Map();
  try {
    const rows = db.prepare(`
      SELECT entity_type,entity_id,visibility,reason,updated_by,created_at,updated_at
        FROM wiki_entity_visibility
       WHERE entity_type=?
    `).all(String(type));
    return new Map(rows.map(row => [Number(row.entity_id), row]));
  } catch (error) {
    if (String(error.message || "").includes("no such table")) return new Map();
    throw error;
  }
}

function decision(entity, overrides = null) {
  const auto = automaticDecision(entity);
  const override = overrides instanceof Map
    ? overrides.get(Number(entity?.id)) || null
    : getOverride(entity?.type, entity?.id);

  if (override?.visibility === "hidden") {
    return {
      visible: false,
      source: "manual-hidden",
      reason: cleanText(override.reason) || "Hidden by staff",
      automaticHidden: auto.hidden,
      automaticReason: auto.reason,
      override
    };
  }
  if (override?.visibility === "visible") {
    return {
      visible: true,
      source: "manual-visible",
      reason: cleanText(override.reason) || "Marked player-visible by staff",
      automaticHidden: auto.hidden,
      automaticReason: auto.reason,
      override
    };
  }
  if (auto.hidden) {
    return {
      visible: false,
      source: "automatic-hidden",
      reason: auto.reason,
      automaticHidden: true,
      automaticReason: auto.reason,
      override: null
    };
  }
  return {
    visible: true,
    source: "default-visible",
    reason: "",
    automaticHidden: false,
    automaticReason: "",
    override: null
  };
}

function decorate(entity, overrides = null) {
  const verdict = decision(entity, overrides);
  return {
    ...entity,
    publicVisible: verdict.visible,
    visibilitySource: verdict.source,
    visibilityReason: verdict.reason,
    automaticHidden: verdict.automaticHidden,
    automaticReason: verdict.automaticReason,
    visibilityOverride: verdict.override
  };
}

function filterPublic(rows = []) {
  const maps = new Map();
  return rows.filter(entity => {
    const type = String(entity?.type || "");
    if (!maps.has(type)) maps.set(type, overrideMap(type));
    return decision(entity, maps.get(type)).visible;
  });
}

function setOverride(type, id, visibility, reason = "", updatedBy = "") {
  const numericId = validId(id);
  const mode = String(visibility || "");
  if (!validType(type) || numericId == null || !VISIBILITY.has(mode)) throw new Error("Invalid Wiki visibility override");
  const entity = data.getBase(type, numericId);
  if (!entity) throw new Error("Wiki entity not found");
  const safeReason = cleanText(reason).slice(0, 300) || (mode === "hidden" ? "Hidden by staff" : "Marked player-visible by staff");
  const safeUser = cleanText(updatedBy).slice(0, 100);
  db.prepare(`
    INSERT INTO wiki_entity_visibility(entity_type,entity_id,visibility,reason,updated_by)
    VALUES(?,?,?,?,?)
    ON CONFLICT(entity_type,entity_id) DO UPDATE SET
      visibility=excluded.visibility,
      reason=excluded.reason,
      updated_by=excluded.updated_by,
      updated_at=CURRENT_TIMESTAMP
  `).run(String(type), numericId, mode, safeReason, safeUser);
  revision += 1;
  statsCache = null;
  return decorate(entity);
}

function clearOverride(type, id) {
  const numericId = validId(id);
  if (!validType(type) || numericId == null) throw new Error("Invalid Wiki visibility override");
  db.prepare("DELETE FROM wiki_entity_visibility WHERE entity_type=? AND entity_id=?").run(String(type), numericId);
  revision += 1;
  statsCache = null;
  const entity = data.getBase(type, numericId);
  return entity ? decorate(entity) : null;
}

function revisionToken() {
  return revision;
}

function score(entity, query) {
  const q = normalizeText(query);
  if (!q) return 0;
  const raw = String(query || "").trim();
  const id = String(entity.id);
  const name = normalizeText(entity.name);
  const description = normalizeText(entity.description);
  const subtype = normalizeText(entity.subtype);
  if (id === raw) return 1000;
  if (name === q) return 950;
  if (name.startsWith(q)) return 800;
  if (name.includes(q)) return 650;
  if (id.startsWith(raw)) return 500;
  if (subtype.includes(q)) return 300;
  if (description.includes(q)) return 200;
  return -1;
}

function matchesFilter(row, filter) {
  if (filter === "visible") return row.publicVisible;
  if (filter === "hidden") return !row.publicVisible;
  if (filter === "automatic-hidden") return row.visibilitySource === "automatic-hidden";
  if (filter === "manual-hidden") return row.visibilitySource === "manual-hidden";
  if (filter === "manual-visible") return row.visibilitySource === "manual-visible";
  return true;
}

function catalogList(type, { q = "", filter = "all", page = 1, limit = 50 } = {}) {
  const selectedType = validType(type) ? String(type) : "items";
  const selectedFilter = FILTERS.has(String(filter || "")) ? String(filter) : "all";
  const overrides = overrideMap(selectedType);
  let rows = data.all(selectedType).map(entity => decorate(entity, overrides));
  if (String(q).trim()) {
    rows = rows
      .map(entity => ({ entity, score: score(entity, q) }))
      .filter(row => row.score >= 0)
      .sort((a, b) => b.score - a.score || a.entity.name.localeCompare(b.entity.name) || Number(a.entity.id) - Number(b.entity.id))
      .map(row => row.entity);
  }
  rows = rows.filter(row => matchesFilter(row, selectedFilter));
  const safeLimit = Math.max(20, Math.min(100, Number(limit) || 50));
  const total = rows.length;
  const pages = Math.max(1, Math.ceil(total / safeLimit));
  const safePage = Math.max(1, Math.min(pages, Number(page) || 1));
  const offset = (safePage - 1) * safeLimit;
  return { rows: rows.slice(offset, offset + safeLimit), total, page: safePage, pages, limit: safeLimit, filter: selectedFilter, type: selectedType };
}

function stats() {
  const snapshot = data.ensureCatalog();
  if (statsCache && statsCache.builtAt === snapshot.builtAt && statsCache.revision === revision) return statsCache.value;
  const totalStats = { total: 0, visible: 0, hidden: 0, automaticHidden: 0, manualHidden: 0, manualVisible: 0, byType: {} };
  for (const type of Object.keys(data.TYPE_META)) {
    const overrides = overrideMap(type);
    const typeStats = { total: 0, visible: 0, hidden: 0, automaticHidden: 0, manualHidden: 0, manualVisible: 0 };
    for (const entity of data.all(type)) {
      const verdict = decision(entity, overrides);
      typeStats.total += 1;
      if (verdict.visible) typeStats.visible += 1;
      else typeStats.hidden += 1;
      if (verdict.source === "automatic-hidden") typeStats.automaticHidden += 1;
      if (verdict.source === "manual-hidden") typeStats.manualHidden += 1;
      if (verdict.source === "manual-visible") typeStats.manualVisible += 1;
    }
    totalStats.byType[type] = typeStats;
    for (const key of ["total", "visible", "hidden", "automaticHidden", "manualHidden", "manualVisible"]) totalStats[key] += typeStats[key];
  }
  statsCache = { builtAt: snapshot.builtAt, revision, value: totalStats };
  return totalStats;
}

module.exports = {
  automaticDecision,
  decision,
  decorate,
  filterPublic,
  getOverride,
  overrideMap,
  setOverride,
  clearOverride,
  revisionToken,
  catalogList,
  stats,
  _test: { cleanText, normalizeText, automaticDecision, decision, score, matchesFilter }
};
