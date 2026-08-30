const fs = require("fs");
const path = require("path");
const Database = require("better-sqlite3");
const env = require("../config/env");

fs.mkdirSync(path.dirname(env.cmsDbPath), { recursive: true });
const db = new Database(env.cmsDbPath);
db.pragma("journal_mode = WAL");

function initCms() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS admins (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT NOT NULL UNIQUE,
      password_hash TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS posts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      slug TEXT NOT NULL UNIQUE,
      title TEXT NOT NULL,
      excerpt TEXT NOT NULL DEFAULT '',
      body TEXT NOT NULL DEFAULT '',
      type TEXT NOT NULL DEFAULT 'news',
      published INTEGER NOT NULL DEFAULT 1,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS downloads (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      description TEXT NOT NULL DEFAULT '',
      url TEXT NOT NULL,
      kind TEXT NOT NULL DEFAULT 'client',
      version TEXT NOT NULL DEFAULT '',
      published INTEGER NOT NULL DEFAULT 1,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS settings (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS donations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      donor_name TEXT NOT NULL DEFAULT '',
      amount_cents INTEGER NOT NULL DEFAULT 0,
      provider TEXT NOT NULL DEFAULT '',
      reference TEXT NOT NULL DEFAULT '',
      status TEXT NOT NULL DEFAULT 'completed',
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS announcements (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      body TEXT NOT NULL DEFAULT '',
      active INTEGER NOT NULL DEFAULT 1,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS pages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      slug TEXT NOT NULL UNIQUE,
      title TEXT NOT NULL,
      body TEXT NOT NULL DEFAULT '',
      published INTEGER NOT NULL DEFAULT 1,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS audit_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      admin_id INTEGER,
      action TEXT NOT NULL,
      details TEXT NOT NULL DEFAULT '',
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
  `);

  const defaults = {
    hero_title: "Welcome to EverLeaf",
    hero_subtitle: "A refined v83 MapleStory experience built around progression, community, and classic gameplay.",
    announcement: "EverLeaf is currently in development.",
    maintenance_message: "",
    footer_note: "EverLeaf is a fan-made private server and is not affiliated with Nexon."
  };

  const stmt = db.prepare("INSERT OR IGNORE INTO settings (key,value) VALUES (?,?)");
  Object.entries(defaults).forEach(([k,v]) => stmt.run(k,v));
}

function settings() {
  return Object.fromEntries(
    db.prepare("SELECT key,value FROM settings").all().map(r => [r.key, r.value])
  );
}

module.exports = { db, initCms, settings };
