const session = require("express-session");
const Database = require("better-sqlite3");
const fs = require("node:fs");
const path = require("node:path");

class SqliteSessionStore extends session.Store {
  constructor(filename, {now = Date.now} = {}) {
    super();
    fs.mkdirSync(path.dirname(filename), {recursive:true, mode:0o700});
    this.now = now;
    this.db = new Database(filename);
    fs.chmodSync(filename, 0o600);
    this.db.pragma("journal_mode = WAL");
    this.db.pragma("busy_timeout = 3000");
    this.db.exec("CREATE TABLE IF NOT EXISTS sessions (sid TEXT PRIMARY KEY, data TEXT NOT NULL, expires INTEGER NOT NULL); CREATE INDEX IF NOT EXISTS sessions_expires ON sessions(expires)");
    this.cleanup = setInterval(() => {
      try { this.db.prepare("DELETE FROM sessions WHERE expires <= ?").run(this.now()); }
      catch(error) { console.error("Session cleanup failed:", error.message); }
    }, 15*60_000);
    this.cleanup.unref();
  }
  expiry(value) {
    return value.cookie?.expires ? new Date(value.cookie.expires).getTime() : this.now()+12*60*60_000;
  }
  get(sid, callback) {
    try {
      const row=this.db.prepare("SELECT data FROM sessions WHERE sid=? AND expires>?").get(sid,this.now());
      callback(null,row?JSON.parse(row.data):null);
    } catch(error) { callback(error); }
  }
  set(sid,value,callback=()=>{}) {
    try {
      this.db.prepare("INSERT INTO sessions(sid,data,expires) VALUES(?,?,?) ON CONFLICT(sid) DO UPDATE SET data=excluded.data,expires=excluded.expires")
        .run(sid,JSON.stringify(value),this.expiry(value));
      callback();
    } catch(error) { callback(error); }
  }
  touch(sid,value,callback=()=>{}) {
    try { this.db.prepare("UPDATE sessions SET expires=? WHERE sid=?").run(this.expiry(value),sid);callback(); }
    catch(error) { callback(error); }
  }
  destroy(sid,callback=()=>{}) {
    try { this.db.prepare("DELETE FROM sessions WHERE sid=?").run(sid);callback(); }
    catch(error) { callback(error); }
  }
  close() { clearInterval(this.cleanup);this.db.close(); }
}
module.exports = SqliteSessionStore;
