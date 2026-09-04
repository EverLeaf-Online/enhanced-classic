const fs = require("fs");
const path = require("path");
const env = require("../config/env");
const { getPool } = require("../db/game");

const TYPE_META = Object.freeze({
  items: { label: "Items", singular: "Item", description: "Equipment, consumables, chairs, ETC, cash items, pets and other server items." },
  monsters: { label: "Monsters", singular: "Monster", description: "Monster stats, spawn locations and the live server drop table." },
  maps: { label: "Maps", singular: "Map", description: "Map names, monsters, NPCs and portal connections from EverLeaf's WZ data." },
  skills: { label: "Skills", singular: "Skill", description: "Skill names and per-level data from the server's Skill.wz files." },
  npcs: { label: "NPCs", singular: "NPC", description: "NPC names, spawn locations and shop inventory." },
  quests: { label: "Quests", singular: "Quest", description: "Quest metadata, checks and rewards from the server quest data." }
});

const state = {
  root: null,
  available: false,
  builtAt: 0,
  entities: Object.fromEntries(Object.keys(TYPE_META).map(type => [type, []])),
  byType: Object.fromEntries(Object.keys(TYPE_META).map(type => [type, new Map()])),
  parsedFiles: new Map(),
  numericFileIndexes: new Map(),
  worldRelations: null,
  errors: []
};

function entityKey(type, id) {
  return `${type}:${Number(id)}`;
}

function decodeXml(value = "") {
  return String(value)
    .replace(/&#x([0-9a-f]+);/gi, (_, hex) => String.fromCodePoint(parseInt(hex, 16)))
    .replace(/&#(\d+);/g, (_, dec) => String.fromCodePoint(Number(dec)))
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&");
}

function parseAttributes(raw = "") {
  const attrs = {};
  const re = /([A-Za-z0-9_:-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')/g;
  let match;
  while ((match = re.exec(raw))) attrs[match[1]] = decodeXml(match[2] ?? match[3] ?? "");
  return attrs;
}

function parseWzXmlText(text = "") {
  const documentNode = { tag: "root", name: "root", attrs: {}, children: [] };
  const stack = [documentNode];
  const token = /<(\/?)(imgdir|string|int|short|long|float|double|vector|uol|canvas|sound)\b([^>]*)>/gi;
  let match;
  while ((match = token.exec(text))) {
    const closing = match[1] === "/";
    const tag = match[2].toLowerCase();
    const raw = match[3] || "";
    if (closing) {
      for (let i = stack.length - 1; i > 0; i--) {
        const node = stack.pop();
        if (node.tag === tag) break;
      }
      continue;
    }
    const attrs = parseAttributes(raw);
    const node = {
      tag,
      name: attrs.name == null ? "" : String(attrs.name),
      value: attrs.value == null ? null : attrs.value,
      attrs,
      children: []
    };
    stack[stack.length - 1].children.push(node);
    const selfClosing = /\/\s*$/.test(raw) || ["string", "int", "short", "long", "float", "double", "vector", "uol"].includes(tag);
    if (!selfClosing) stack.push(node);
  }
  return documentNode;
}

function resolveWzRoot() {
  const configured = process.env.WIKI_WZ_ROOT || env.wikiData?.wzRoot;
  const candidates = [
    configured,
    "/opt/everleaf/current/wz",
    "/opt/everleaf/server/wz",
    path.resolve(process.cwd(), "wz"),
    path.resolve(process.cwd(), "../wz")
  ].filter(Boolean);
  for (const candidate of candidates) {
    try {
      const resolved = path.resolve(candidate);
      if (fs.statSync(resolved).isDirectory() && fs.existsSync(path.join(resolved, "String.wz"))) return resolved;
    } catch {}
  }
  return null;
}

function readXml(file) {
  const full = path.resolve(file);
  let stat;
  try { stat = fs.statSync(full); } catch { return null; }
  const cached = state.parsedFiles.get(full);
  if (cached && cached.mtimeMs === stat.mtimeMs && cached.size === stat.size) return cached.document;
  const document = parseWzXmlText(fs.readFileSync(full, "utf8"));
  state.parsedFiles.set(full, { mtimeMs: stat.mtimeMs, size: stat.size, document });
  return document;
}

function firstImgdir(node) {
  return (node?.children || []).find(child => child.tag === "imgdir") || null;
}

function directChild(node, name, tag = null) {
  return (node?.children || []).find(child => (!tag || child.tag === tag) && String(child.name) === String(name)) || null;
}

function directImgdir(node, name) {
  return directChild(node, name, "imgdir");
}

function directValue(node, name, fallback = null) {
  const child = (node?.children || []).find(entry => entry.name === String(name) && entry.value != null);
  return child ? child.value : fallback;
}

function directText(node, ...names) {
  for (const name of names) {
    const value = directValue(node, name, null);
    if (value != null && String(value).trim()) return String(value).trim();
  }
  return "";
}

function numericName(value) {
  const str = String(value || "");
  return /^0*\d{1,10}$/.test(str) ? Number(str) : null;
}

function walkImgdirs(node, parents, callback) {
  for (const child of node?.children || []) {
    if (child.tag !== "imgdir") continue;
    callback(child, parents);
    walkImgdirs(child, [...parents, child.name], callback);
  }
}

function addEntity(type, id, name, extra = {}) {
  const numericId = Number(id);
  if (!Number.isInteger(numericId) || numericId < 0 || !name || !TYPE_META[type]) return;
  const existing = state.byType[type].get(numericId);
  const entity = {
    type,
    id: numericId,
    name: String(name).trim(),
    description: String(extra.description || existing?.description || "").trim(),
    subtype: String(extra.subtype || existing?.subtype || "").trim(),
    meta: { ...(existing?.meta || {}), ...(extra.meta || {}) }
  };
  state.byType[type].set(numericId, entity);
}

function collectCatalogFile(relative, type, options = {}) {
  if (!state.root) return 0;
  const file = path.join(state.root, relative);
  const document = readXml(file);
  if (!document) return 0;
  let added = 0;
  walkImgdirs(document, [], (node, parents) => {
    const id = numericName(node.name);
    if (id == null) return;
    const name = directText(node, ...(options.nameFields || ["name"]));
    if (!name) return;
    const description = directText(node, ...(options.descriptionFields || ["desc", "description", "info"]));
    let subtype = options.subtype || "";
    if (typeof options.subtypeFromParents === "function") subtype = options.subtypeFromParents(parents, node) || subtype;
    addEntity(type, id, name, { description, subtype, meta: options.meta?.(node, parents) || {} });
    added++;
  });
  return added;
}

function scanSkillNames() {
  if (!state.root) return 0;
  let added = collectCatalogFile("String.wz/Skill.img.xml", "skills", {
    nameFields: ["name"],
    descriptionFields: ["desc", "h", "bookName"]
  });
  if (added) return added;
  const base = path.join(state.root, "Skill.wz");
  if (!fs.existsSync(base)) return 0;
  for (const file of walkFiles(base).filter(file => file.endsWith(".img.xml"))) {
    const document = readXml(file);
    if (!document) continue;
    walkImgdirs(document, [], node => {
      const id = numericName(node.name);
      if (id == null || id < 100000) return;
      const name = directText(node, "name");
      if (!name) return;
      addEntity("skills", id, name, { description: directText(node, "desc") });
      added++;
    });
  }
  return added;
}

function buildCatalog() {
  state.root = resolveWzRoot();
  state.errors = [];
  state.entities = Object.fromEntries(Object.keys(TYPE_META).map(type => [type, []]));
  state.byType = Object.fromEntries(Object.keys(TYPE_META).map(type => [type, new Map()]));
  state.worldRelations = null;
  if (!state.root) {
    state.available = false;
    state.builtAt = Date.now();
    state.errors.push("EverLeaf WZ data directory was not found on this host.");
    return snapshot();
  }

  const itemFiles = [
    ["String.wz/Eqp.img.xml", "Equipment"],
    ["String.wz/Consume.img.xml", "Consumable"],
    ["String.wz/Ins.img.xml", "Install / Chair"],
    ["String.wz/Etc.img.xml", "ETC"],
    ["String.wz/Cash.img.xml", "Cash"],
    ["String.wz/Pet.img.xml", "Pet"]
  ];
  for (const [file, subtype] of itemFiles) {
    collectCatalogFile(file, "items", {
      subtype,
      nameFields: ["name"],
      descriptionFields: ["desc", "autodesc"]
    });
  }
  collectCatalogFile("String.wz/Mob.img.xml", "monsters", { nameFields: ["name"], descriptionFields: ["desc"] });
  collectCatalogFile("String.wz/Npc.img.xml", "npcs", { nameFields: ["name"], descriptionFields: ["func", "desc"] });
  collectCatalogFile("String.wz/Map.img.xml", "maps", {
    nameFields: ["mapName", "streetName", "name"],
    descriptionFields: ["streetName", "mapName"],
    subtypeFromParents: parents => parents.filter(Boolean).slice(-2).join(" / ")
  });
  collectCatalogFile("Quest.wz/QuestInfo.img.xml", "quests", {
    nameFields: ["name"],
    descriptionFields: ["info", "summary", "parent"]
  });
  scanSkillNames();

  for (const type of Object.keys(TYPE_META)) {
    state.entities[type] = [...state.byType[type].values()].sort((a, b) => a.name.localeCompare(b.name) || a.id - b.id);
  }
  state.available = Object.values(state.entities).some(rows => rows.length > 0);
  state.builtAt = Date.now();
  return snapshot();
}

function ensureCatalog() {
  const ttl = Math.max(60_000, Number(env.wikiData?.catalogTtlMs || 900_000));
  if (!state.builtAt || Date.now() - state.builtAt > ttl) return buildCatalog();
  return snapshot();
}

function snapshot() {
  return {
    available: state.available,
    root: state.root,
    builtAt: state.builtAt,
    errors: [...state.errors],
    counts: Object.fromEntries(Object.keys(TYPE_META).map(type => [type, state.entities[type].length]))
  };
}

function scoreEntity(entity, query) {
  const q = String(query || "").trim().toLowerCase();
  if (!q) return 0;
  const id = String(entity.id);
  const name = entity.name.toLowerCase();
  const description = entity.description.toLowerCase();
  const subtype = entity.subtype.toLowerCase();
  if (id === q) return 1000;
  if (name === q) return 950;
  if (name.startsWith(q)) return 800;
  if (name.includes(q)) return 650;
  if (id.startsWith(q)) return 500;
  if (subtype.includes(q)) return 300;
  if (description.includes(q)) return 200;
  return -1;
}

function list(type, { q = "", page = 1, limit = 40 } = {}) {
  ensureCatalog();
  if (!TYPE_META[type]) return { rows: [], total: 0, page: 1, pages: 1 };
  const safeLimit = Math.max(10, Math.min(100, Number(limit) || 40));
  let rows = state.entities[type];
  if (String(q).trim()) {
    rows = rows
      .map(entity => ({ entity, score: scoreEntity(entity, q) }))
      .filter(row => row.score >= 0)
      .sort((a, b) => b.score - a.score || a.entity.name.localeCompare(b.entity.name))
      .map(row => row.entity);
  }
  const total = rows.length;
  const pages = Math.max(1, Math.ceil(total / safeLimit));
  const safePage = Math.max(1, Math.min(pages, Number(page) || 1));
  const offset = (safePage - 1) * safeLimit;
  return { rows: rows.slice(offset, offset + safeLimit), total, page: safePage, pages, limit: safeLimit };
}

function search(query, type = "all", limit = 60) {
  ensureCatalog();
  const q = String(query || "").trim();
  if (!q) return [];
  const types = TYPE_META[type] ? [type] : Object.keys(TYPE_META);
  return types
    .flatMap(kind => state.entities[kind].map(entity => ({ entity, score: scoreEntity(entity, q) })))
    .filter(row => row.score >= 0)
    .sort((a, b) => b.score - a.score || a.entity.name.localeCompare(b.entity.name) || a.entity.id - b.entity.id)
    .slice(0, Math.max(1, Math.min(100, Number(limit) || 60)))
    .map(row => row.entity);
}

function getBase(type, id) {
  ensureCatalog();
  if (!TYPE_META[type]) return null;
  return state.byType[type].get(Number(id)) || null;
}

function walkFiles(root) {
  const result = [];
  const stack = [root];
  while (stack.length) {
    const current = stack.pop();
    let entries;
    try { entries = fs.readdirSync(current, { withFileTypes: true }); } catch { continue; }
    for (const entry of entries) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) stack.push(full);
      else result.push(full);
    }
  }
  return result;
}

function numericFileIndex(relativeRoot) {
  ensureCatalog();
  const key = String(relativeRoot);
  if (state.numericFileIndexes.has(key)) return state.numericFileIndexes.get(key);
  const index = new Map();
  if (!state.root) return index;
  const base = path.join(state.root, relativeRoot);
  if (fs.existsSync(base)) {
    for (const file of walkFiles(base)) {
      const match = path.basename(file).match(/^(\d+)\.img\.xml$/i);
      if (match) index.set(Number(match[1]), file);
    }
  }
  state.numericFileIndexes.set(key, index);
  return index;
}

function findNodeByNumericName(node, id) {
  const wanted = Number(id);
  let found = null;
  walkImgdirs(node, [], child => {
    if (found) return;
    if (numericName(child.name) === wanted) found = child;
  });
  return found;
}

function scalarFields(node) {
  if (!node) return {};
  const result = {};
  for (const child of node.children || []) {
    if (child.value == null || !child.name) continue;
    if (["int", "short", "long", "float", "double", "string"].includes(child.tag)) result[child.name] = child.value;
  }
  return result;
}

function nodeSummary(node, depth = 2) {
  if (!node || depth < 0) return null;
  const values = scalarFields(node);
  const groups = [];
  if (depth > 0) {
    for (const child of node.children || []) {
      if (child.tag !== "imgdir") continue;
      groups.push({ name: child.name, values: scalarFields(child), groups: nodeSummary(child, depth - 1)?.groups || [] });
    }
  }
  return { values, groups };
}

function itemDataNode(id) {
  if (!state.root) return null;
  const numericId = Number(id);
  if (numericId >= 1000000 && numericId < 2000000) {
    const file = numericFileIndex("Character.wz").get(numericId);
    if (!file) return null;
    const doc = readXml(file);
    return firstImgdir(doc);
  }
  const padded = String(numericId).padStart(8, "0");
  const prefix = `${padded.slice(0, 4)}.img.xml`;
  const category = Math.floor(numericId / 1000000);
  const preferred = category === 2 ? ["Consume"] : category === 3 ? ["Install"] : category === 4 ? ["Etc"] : category === 5 ? ["Cash", "Pet"] : [];
  for (const directory of [...preferred, "Consume", "Install", "Etc", "Cash", "Pet"]) {
    const file = path.join(state.root, "Item.wz", directory, prefix);
    if (!fs.existsSync(file)) continue;
    const doc = readXml(file);
    const node = findNodeByNumericName(doc, numericId);
    if (node) return node;
  }
  const fallbackFile = numericFileIndex("Item.wz").get(numericId);
  if (!fallbackFile) return null;
  const doc = readXml(fallbackFile);
  return findNodeByNumericName(doc, numericId) || firstImgdir(doc);
}

function mobDataNode(id) {
  const file = numericFileIndex("Mob.wz").get(Number(id));
  return file ? firstImgdir(readXml(file)) : null;
}

function npcDataNode(id) {
  const file = numericFileIndex("Npc.wz").get(Number(id));
  return file ? firstImgdir(readXml(file)) : null;
}

function mapDataNode(id) {
  const file = numericFileIndex("Map.wz/Map").get(Number(id));
  return file ? firstImgdir(readXml(file)) : null;
}

function skillDataNode(id) {
  const numericId = Number(id);
  const job = Math.floor(numericId / 10000);
  const index = numericFileIndex("Skill.wz");
  const likely = index.get(job);
  if (likely) {
    const node = findNodeByNumericName(readXml(likely), numericId);
    if (node) return node;
  }
  for (const file of index.values()) {
    const node = findNodeByNumericName(readXml(file), numericId);
    if (node) return node;
  }
  return null;
}

function questDataNodes(id) {
  const result = {};
  if (!state.root) return result;
  for (const [key, relative] of [["info", "Quest.wz/QuestInfo.img.xml"], ["check", "Quest.wz/Check.img.xml"], ["act", "Quest.wz/Act.img.xml"]]) {
    const document = readXml(path.join(state.root, relative));
    if (document) result[key] = findNodeByNumericName(document, Number(id));
  }
  return result;
}

async function safeQuery(sql, params = []) {
  try {
    const [rows] = await getPool().query(sql, params);
    return rows;
  } catch (error) {
    console.warn("Wiki data query failed:", error.message);
    return [];
  }
}

function enrich(type, id) {
  return state.byType[type]?.get(Number(id)) || { type, id: Number(id), name: `${TYPE_META[type]?.singular || type} ${Number(id)}`, description: "", subtype: "", meta: {} };
}

async function itemSources(id) {
  const [drops, shops] = await Promise.all([
    safeQuery("SELECT dropperid, chance, minimum_quantity, maximum_quantity, questid FROM drop_data WHERE itemid=? ORDER BY chance DESC, dropperid ASC LIMIT 250", [Number(id)]),
    safeQuery("SELECT s.npcid, si.price, si.pitch FROM shopitems si INNER JOIN shops s ON s.shopid=si.shopid WHERE si.itemid=? AND (si.price>0 OR si.pitch>0) ORDER BY si.price ASC, s.npcid ASC LIMIT 100", [Number(id)])
  ]);
  return {
    drops: drops.map(row => ({ ...row, monster: enrich("monsters", row.dropperid) })),
    shops: shops.map(row => ({ ...row, npc: enrich("npcs", row.npcid) }))
  };
}

async function monsterDrops(id) {
  const rows = await safeQuery("SELECT itemid, chance, minimum_quantity, maximum_quantity, questid FROM drop_data WHERE dropperid=? ORDER BY chance DESC, itemid ASC LIMIT 500", [Number(id)]);
  return rows.map(row => ({ ...row, item: enrich("items", row.itemid) }));
}

async function npcShop(id) {
  const rows = await safeQuery("SELECT si.itemid, si.price, si.pitch, si.position FROM shops s INNER JOIN shopitems si ON si.shopid=s.shopid WHERE s.npcid=? AND (si.price>0 OR si.pitch>0) ORDER BY si.position DESC, si.itemid ASC LIMIT 500", [Number(id)]);
  return rows.map(row => ({ ...row, item: enrich("items", row.itemid) }));
}

function buildWorldRelations() {
  ensureCatalog();
  if (state.worldRelations) return state.worldRelations;
  const relations = { maps: new Map(), mobMaps: new Map(), npcMaps: new Map() };
  for (const [mapId, file] of numericFileIndex("Map.wz/Map").entries()) {
    const mapNode = firstImgdir(readXml(file));
    if (!mapNode) continue;
    const info = directImgdir(mapNode, "info");
    const life = directImgdir(mapNode, "life");
    const portal = directImgdir(mapNode, "portal");
    const mapEntry = {
      id: mapId,
      info: scalarFields(info),
      mobs: [],
      npcs: [],
      portals: []
    };
    for (const entry of life?.children || []) {
      if (entry.tag !== "imgdir") continue;
      const values = scalarFields(entry);
      const lifeId = Number(values.id || directValue(entry, "id", 0));
      const type = String(values.type || directValue(entry, "type", ""));
      if (!lifeId) continue;
      const record = { id: lifeId, x: Number(values.x || 0), y: Number(values.y || 0), fh: Number(values.fh || 0) };
      if (type === "m") {
        record.entity = enrich("monsters", lifeId);
        mapEntry.mobs.push(record);
        if (!relations.mobMaps.has(lifeId)) relations.mobMaps.set(lifeId, []);
        relations.mobMaps.get(lifeId).push(mapId);
      } else if (type === "n") {
        record.entity = enrich("npcs", lifeId);
        mapEntry.npcs.push(record);
        if (!relations.npcMaps.has(lifeId)) relations.npcMaps.set(lifeId, []);
        relations.npcMaps.get(lifeId).push(mapId);
      }
    }
    for (const entry of portal?.children || []) {
      if (entry.tag !== "imgdir") continue;
      const values = scalarFields(entry);
      const targetMap = Number(values.tm ?? directValue(entry, "tm", -1));
      mapEntry.portals.push({
        name: String(values.pn || directValue(entry, "pn", "")),
        targetName: String(values.tn || directValue(entry, "tn", "")),
        targetMap,
        target: targetMap >= 0 ? enrich("maps", targetMap) : null,
        x: Number(values.x || 0),
        y: Number(values.y || 0),
        type: Number(values.pt || 0)
      });
    }
    relations.maps.set(mapId, mapEntry);
  }
  state.worldRelations = relations;
  return relations;
}

function mapLinks(ids = []) {
  return [...new Set(ids.map(Number).filter(Number.isInteger))].map(id => enrich("maps", id));
}

async function detail(type, id) {
  ensureCatalog();
  if (!TYPE_META[type]) return null;
  const base = getBase(type, id);
  if (!base) return null;
  const result = { ...base, sections: {}, source: "EverLeaf live server data" };

  if (type === "items") {
    const node = itemDataNode(id);
    const info = directImgdir(node, "info") || node;
    result.sections.stats = scalarFields(info);
    result.sections.sources = await itemSources(id);
  } else if (type === "monsters") {
    const node = mobDataNode(id);
    result.sections.stats = scalarFields(directImgdir(node, "info") || node);
    result.sections.drops = await monsterDrops(id);
    const relations = buildWorldRelations();
    result.sections.maps = mapLinks(relations.mobMaps.get(Number(id)) || []);
  } else if (type === "maps") {
    const node = mapDataNode(id);
    result.sections.raw = scalarFields(directImgdir(node, "info") || node);
    const relations = buildWorldRelations();
    const map = relations.maps.get(Number(id)) || { mobs: [], npcs: [], portals: [] };
    result.sections.mobs = map.mobs;
    result.sections.npcs = map.npcs;
    result.sections.portals = map.portals;
  } else if (type === "npcs") {
    const node = npcDataNode(id);
    result.sections.raw = scalarFields(directImgdir(node, "info") || node);
    result.sections.shop = await npcShop(id);
    const relations = buildWorldRelations();
    result.sections.maps = mapLinks(relations.npcMaps.get(Number(id)) || []);
  } else if (type === "skills") {
    const node = skillDataNode(id);
    result.sections.raw = scalarFields(node);
    const common = directImgdir(node, "common");
    result.sections.common = scalarFields(common);
    const levels = directImgdir(node, "level");
    result.sections.levels = (levels?.children || []).filter(child => child.tag === "imgdir").map(child => ({ level: Number(child.name), values: scalarFields(child) })).filter(row => Number.isInteger(row.level));
  } else if (type === "quests") {
    const nodes = questDataNodes(id);
    result.sections.info = nodeSummary(nodes.info, 2);
    result.sections.check = nodeSummary(nodes.check, 3);
    result.sections.act = nodeSummary(nodes.act, 3);
  }
  return result;
}

function typeMeta(type) {
  return TYPE_META[type] || null;
}

function allTypeMeta() {
  return TYPE_META;
}

module.exports = {
  TYPE_META,
  allTypeMeta,
  typeMeta,
  ensureCatalog,
  buildCatalog,
  snapshot,
  search,
  list,
  getBase,
  detail,
  parseWzXmlText,
  scalarFields,
  nodeSummary,
  _test: { decodeXml, parseAttributes, findNodeByNumericName, scoreEntity, directValue, directText }
};
