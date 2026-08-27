const bcrypt = require("bcryptjs");
const crypto = require("crypto");

function digest(algo, password) {
  return crypto.createHash(algo).update(password, "utf8").digest("hex");
}

async function hashPassword(password, mode="bcrypt") {
  if (mode === "bcrypt") return bcrypt.hash(password, 12);
  if (mode === "sha1") return digest("sha1", password);
  if (mode === "sha512") return digest("sha512", password);
  if (mode === "plaintext") return password;
  throw new Error("Unsupported password mode.");
}

// Mirrors EverLeaf's Client.login behavior: BCrypt first, then legacy
// plaintext/SHA-1/SHA-512 so old accounts can still use the web portal.
async function verifyPassword(password, stored) {
  if (!stored) return false;
  const value = String(stored);
  if (/^\$2[aby]\$/.test(value)) {
    try { return await bcrypt.compare(password, value); } catch { return false; }
  }
  if (password === value) return true;
  const lower=value.toLowerCase();
  return digest("sha1", password).toLowerCase() === lower ||
         digest("sha512", password).toLowerCase() === lower;
}

module.exports = { hashPassword, verifyPassword };
