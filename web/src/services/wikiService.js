const { db } = require("../db/cms");
const { categories } = require("./wikiCatalog");

const categoryKeys = new Set(categories.map(category => category.key));

function parseJson(value, fallback=[]) {
  try {
    const parsed = JSON.parse(String(value || ""));
    return Array.isArray(parsed) ? parsed : fallback;
  } catch {
    return fallback;
  }
}

function sectionId(title, index) {
  const base = String(title || "section")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || `section-${index + 1}`;
  return `${base}-${index + 1}`;
}

function parseBody(body="") {
  const text = String(body || "").replace(/\r\n/g, "\n").trim();
  if (!text) return [];
  const sections = [];
  let title = "Overview";
  let lines = [];
  const flush = () => {
    const content = lines.join("\n").trim();
    if (content) sections.push({ title, body: content });
    lines = [];
  };
  for (const line of text.split("\n")) {
    const match = line.match(/^##\s+(.+)$/);
    if (match) {
      flush();
      title = match[1].trim() || "Overview";
    } else {
      lines.push(line);
    }
  }
  flush();
  return sections.map((section,index)=>({ ...section, id: sectionId(section.title,index) }));
}

function normalize(row) {
  if (!row) return null;
  return {
    id: Number(row.id),
    slug: row.slug,
    category: row.category,
    title: row.title,
    eyebrow: row.eyebrow,
    summary: row.summary,
    body: row.body,
    status: row.status,
    verification: row.verification,
    source: row.source,
    sourceDoc: row.source_doc,
    tags: parseJson(row.tags_json),
    facts: parseJson(row.facts_json),
    sections: parseBody(row.body),
    published: Boolean(row.published),
    createdAt: row.created_at,
    updatedAt: row.updated_at
  };
}

function listPublished() {
  return db.prepare("SELECT * FROM wiki_articles WHERE published=1 ORDER BY title COLLATE NOCASE").all().map(normalize);
}

function listAll() {
  return db.prepare("SELECT * FROM wiki_articles ORDER BY updated_at DESC,title COLLATE NOCASE").all().map(normalize);
}

function getBySlug(slug, includeUnpublished=false) {
  const sql = includeUnpublished
    ? "SELECT * FROM wiki_articles WHERE slug=? LIMIT 1"
    : "SELECT * FROM wiki_articles WHERE slug=? AND published=1 LIMIT 1";
  return normalize(db.prepare(sql).get(String(slug || "")));
}

function getById(id) {
  return normalize(db.prepare("SELECT * FROM wiki_articles WHERE id=? LIMIT 1").get(Number(id)));
}

function searchEntries(query="", category="all", { includeUnpublished=false }={}) {
  const q = String(query || "").trim().slice(0,120);
  const cat = categoryKeys.has(String(category || "")) ? String(category) : "all";
  const where = [];
  const params = [];
  if (!includeUnpublished) where.push("published=1");
  if (cat !== "all") {
    where.push("category=?");
    params.push(cat);
  }
  if (q) {
    where.push("(title LIKE ? ESCAPE '\\' OR summary LIKE ? ESCAPE '\\' OR body LIKE ? ESCAPE '\\' OR tags_json LIKE ? ESCAPE '\\' OR source LIKE ? ESCAPE '\\')");
    const escaped = q.replace(/[\\%_]/g, char => `\\${char}`);
    const needle = `%${escaped}%`;
    params.push(needle, needle, needle, needle, needle);
  }
  const clause = where.length ? `WHERE ${where.join(" AND ")}` : "";
  return db.prepare(`SELECT * FROM wiki_articles ${clause} ORDER BY published DESC,title COLLATE NOCASE`).all(...params).map(normalize);
}

function relatedEntries(entry, limit=4) {
  if (!entry) return [];
  return db.prepare(`
    SELECT * FROM wiki_articles
    WHERE published=1 AND category=? AND id<>?
    ORDER BY updated_at DESC,title COLLATE NOCASE
    LIMIT ?
  `).all(entry.category, entry.id, Number(limit)).map(normalize);
}

function sourceCoverage(entries=listAll()) {
  const counts = new Map();
  for (const entry of entries) {
    const doc = entry.sourceDoc || entry.source || "Unspecified";
    counts.set(doc, (counts.get(doc) || 0) + 1);
  }
  return [...counts.entries()]
    .map(([doc,count])=>({doc,count}))
    .sort((a,b)=>b.count-a.count || a.doc.localeCompare(b.doc));
}

function stats() {
  const row = db.prepare(`
    SELECT
      COUNT(*) total,
      SUM(CASE WHEN published=1 THEN 1 ELSE 0 END) published,
      SUM(CASE WHEN published=0 THEN 1 ELSE 0 END) drafts,
      MAX(updated_at) last_updated
    FROM wiki_articles
  `).get();
  return {
    total: Number(row?.total || 0),
    published: Number(row?.published || 0),
    drafts: Number(row?.drafts || 0),
    lastUpdated: row?.last_updated || null
  };
}

function parseTags(value) {
  return [...new Set(String(value || "")
    .split(",")
    .map(tag=>tag.trim())
    .filter(Boolean)
    .slice(0,20))];
}

function parseFacts(value) {
  return String(value || "")
    .split(/\r?\n/)
    .map(line=>line.trim())
    .filter(Boolean)
    .slice(0,30)
    .map(line=>{
      const split = line.indexOf(":");
      return split === -1
        ? [line, ""]
        : [line.slice(0,split).trim(), line.slice(split+1).trim()];
    })
    .filter(([label])=>label);
}

function saveArticle(input) {
  const article = {
    id: input.id ? Number(input.id) : null,
    slug: String(input.slug || "").trim().toLowerCase(),
    category: categoryKeys.has(String(input.category || "")) ? String(input.category) : "systems",
    title: String(input.title || "").trim(),
    eyebrow: String(input.eyebrow || "EVERLEAF WIKI").trim(),
    summary: String(input.summary || "").trim(),
    body: String(input.body || "").replace(/\r\n/g, "\n").trim(),
    status: String(input.status || "EverLeaf Guide").trim(),
    verification: String(input.verification || "").trim(),
    source: String(input.source || "EverLeaf").trim(),
    sourceDoc: String(input.sourceDoc || "EverLeaf").trim(),
    tagsJson: JSON.stringify(parseTags(input.tags)),
    factsJson: JSON.stringify(parseFacts(input.facts)),
    published: input.published ? 1 : 0
  };
  if (article.id) {
    db.prepare(`
      UPDATE wiki_articles SET
        slug=@slug, category=@category, title=@title, eyebrow=@eyebrow,
        summary=@summary, body=@body, status=@status, verification=@verification,
        source=@source, source_doc=@sourceDoc, tags_json=@tagsJson,
        facts_json=@factsJson, published=@published, updated_at=CURRENT_TIMESTAMP
      WHERE id=@id
    `).run(article);
    return getById(article.id);
  }
  const info = db.prepare(`
    INSERT INTO wiki_articles
      (slug,category,title,eyebrow,summary,body,status,verification,source,source_doc,tags_json,facts_json,published)
    VALUES
      (@slug,@category,@title,@eyebrow,@summary,@body,@status,@verification,@source,@sourceDoc,@tagsJson,@factsJson,@published)
  `).run(article);
  return getById(info.lastInsertRowid);
}

function editorFields(entry=null) {
  return {
    id: entry?.id || "",
    slug: entry?.slug || "",
    category: entry?.category || "systems",
    title: entry?.title || "",
    eyebrow: entry?.eyebrow || "EVERLEAF WIKI",
    summary: entry?.summary || "",
    body: entry?.body || "## Overview\n",
    status: entry?.status || "EverLeaf Guide",
    verification: entry?.verification || "Verified by EverLeaf staff",
    source: entry?.source || "EverLeaf",
    sourceDoc: entry?.sourceDoc || "EverLeaf CMS",
    tags: (entry?.tags || []).join(", "),
    facts: (entry?.facts || []).map(([label,value])=>`${label}: ${value}`).join("\n"),
    published: entry ? entry.published : true
  };
}

module.exports = {
  categories,
  categoryKeys,
  listPublished,
  listAll,
  getBySlug,
  getById,
  searchEntries,
  relatedEntries,
  sourceCoverage,
  stats,
  saveArticle,
  editorFields,
  parseBody,
  parseTags,
  parseFacts
};
