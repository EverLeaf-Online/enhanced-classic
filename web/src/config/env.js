const path = require("path");
require("dotenv").config();

const bool = (v, fallback=false) =>
  v == null ? fallback : ["1","true","yes","on"].includes(String(v).toLowerCase());

const patchRoot = path.resolve(process.env.LAUNCHER_PATCH_ROOT || "/opt/everleaf/patches");

module.exports = {
  nodeEnv: process.env.NODE_ENV || "development",
  port: Number(process.env.PORT || 3000),
  sessionSecret: process.env.SESSION_SECRET || "dev-only-change-me",
  trustProxy: Number(process.env.TRUST_PROXY || 0),
  cookieSecure: bool(process.env.COOKIE_SECURE, process.env.NODE_ENV === "production"),

  brand: {
    name: process.env.SERVER_NAME || "EverLeaf",
    tagline: process.env.SERVER_TAGLINE || "Enhanced Classic MapleStory",
    version: process.env.SERVER_VERSION || "v83",
    discordUrl: process.env.DISCORD_URL || "",
    donationUrl: process.env.DONATION_URL || "",
    launcherUrl: process.env.LAUNCHER_DOWNLOAD_URL || "/launcher/download",
    clientUrl: process.env.FULL_CLIENT_DOWNLOAD_URL || ""
  },

  game: {
    host: process.env.GAME_HOST || "127.0.0.1",
    loginPort: Number(process.env.LOGIN_PORT || 8484),
    channelPorts: String(process.env.CHANNEL_PORTS || "7575")
      .split(",").map(x => Number(x.trim())).filter(Number.isFinite)
  },

  gameDb: {
    host: process.env.GAME_DB_HOST || "127.0.0.1",
    port: Number(process.env.GAME_DB_PORT || 3306),
    user: process.env.GAME_DB_USER || "",
    password: process.env.GAME_DB_PASSWORD || "",
    database: process.env.GAME_DB_NAME || "cosmic",
    accountsTable: process.env.GAME_ACCOUNTS_TABLE || "accounts",
    charactersTable: process.env.GAME_CHARACTERS_TABLE || "characters",
    accountId: process.env.GAME_ACCOUNT_ID_COLUMN || "id",
    accountName: process.env.GAME_ACCOUNT_NAME_COLUMN || "name",
    accountPassword: process.env.GAME_ACCOUNT_PASSWORD_COLUMN || "password",
    accountEmail: process.env.GAME_ACCOUNT_EMAIL_COLUMN || "email",
    accountBanned: process.env.GAME_ACCOUNT_BANNED_COLUMN || "banned",
    accountLoggedIn: process.env.GAME_ACCOUNT_LOGGEDIN_COLUMN || "loggedin",
    characterAccountId: process.env.GAME_CHARACTER_ACCOUNT_ID_COLUMN || "accountid",
    characterName: process.env.GAME_CHARACTER_NAME_COLUMN || "name",
    characterLevel: process.env.GAME_CHARACTER_LEVEL_COLUMN || "level",
    characterJob: process.env.GAME_CHARACTER_JOB_COLUMN || "job",
    characterFame: process.env.GAME_CHARACTER_FAME_COLUMN || "fame",
    characterGm: process.env.GAME_CHARACTER_GM_COLUMN || "gm",
    characterExp: process.env.GAME_CHARACTER_EXP_COLUMN || "exp"
  },

  registration: {
    enabled: bool(process.env.GAME_REGISTRATION_ENABLED, false),
    mode: String(process.env.GAME_PASSWORD_MODE || "bcrypt").toLowerCase()
  },

  launcher: {
    patchRoot,
    filesRoot: path.join(patchRoot, "files"),
    manifestPath: path.resolve(process.env.LAUNCHER_MANIFEST_PATH || path.join(patchRoot, "manifest.json")),
    signingKeyPath: path.resolve(process.env.LAUNCHER_SIGNING_KEY_PATH || "/etc/everleaf/launcher-manifest-private.pem"),
    installerPath: path.resolve(process.env.LAUNCHER_INSTALLER_PATH || path.join(patchRoot, "downloads", "EverLeafLauncherSetup.exe")),
    announcement: process.env.LAUNCHER_ANNOUNCEMENT || "Welcome to EverLeaf. Your launcher will keep the client synchronized automatically."
  },

  cmsDbPath: path.resolve(process.env.CMS_DB_PATH || "./data/everleaf-cms.sqlite")
};
