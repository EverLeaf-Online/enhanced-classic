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
    clientUrl: process.env.FULL_CLIENT_DOWNLOAD_URL || "https://drive.google.com/file/d/1TW-COG0-lfu998QjYvqvh6OemzZeSWXa/view?usp=sharing"
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

  discord: {
    enabled: bool(process.env.DISCORD_ENABLED, false),
    clientId: process.env.DISCORD_CLIENT_ID || "",
    clientSecret: process.env.DISCORD_CLIENT_SECRET || "",
    botToken: process.env.DISCORD_BOT_TOKEN || "",
    guildId: process.env.DISCORD_GUILD_ID || "",
    supporterRoleId: process.env.DISCORD_SUPPORTER_ROLE_ID || "",
    redirectUri: process.env.DISCORD_REDIRECT_URI || "https://everleafms.duckdns.org/account/discord/callback"
  },

  payments: {
    currency: String(process.env.PAYMENT_CURRENCY || "usd").toLowerCase(),
    publicBaseUrl: String(process.env.PUBLIC_BASE_URL || "https://everleafms.duckdns.org").replace(/\/$/, ""),
    stripe: {
      enabled: bool(process.env.STRIPE_ENABLED, false),
      environment: process.env.STRIPE_ENVIRONMENT === "live" ? "live" : "sandbox",
      sandbox: {
        secretKey: process.env.STRIPE_SANDBOX_SECRET_KEY || process.env.STRIPE_SECRET_KEY || "",
        publishableKey: process.env.STRIPE_SANDBOX_PUBLISHABLE_KEY || "",
        webhookSecret: process.env.STRIPE_SANDBOX_WEBHOOK_SECRET || process.env.STRIPE_WEBHOOK_SECRET || ""
      },
      live: {
        secretKey: process.env.STRIPE_LIVE_SECRET_KEY || "",
        publishableKey: process.env.STRIPE_LIVE_PUBLISHABLE_KEY || "",
        webhookSecret: process.env.STRIPE_LIVE_WEBHOOK_SECRET || ""
      }
    },
    paypal: {
      enabled: bool(process.env.PAYPAL_ENABLED, false),
      environment: process.env.PAYPAL_ENVIRONMENT === "live" ? "live" : "sandbox",
      sandbox: {
        clientId: process.env.PAYPAL_SANDBOX_CLIENT_ID || process.env.PAYPAL_CLIENT_ID || "",
        clientSecret: process.env.PAYPAL_SANDBOX_CLIENT_SECRET || process.env.PAYPAL_CLIENT_SECRET || "",
        webhookId: process.env.PAYPAL_SANDBOX_WEBHOOK_ID || process.env.PAYPAL_WEBHOOK_ID || ""
      },
      live: {
        clientId: process.env.PAYPAL_LIVE_CLIENT_ID || "",
        clientSecret: process.env.PAYPAL_LIVE_CLIENT_SECRET || "",
        webhookId: process.env.PAYPAL_LIVE_WEBHOOK_ID || ""
      }
    }
  },

  launcher: {
    patchRoot,
    filesRoot: path.join(patchRoot, "files"),
    manifestPath: path.resolve(process.env.LAUNCHER_MANIFEST_PATH || path.join(patchRoot, "manifest.json")),
    signingKeyPath: path.resolve(process.env.LAUNCHER_SIGNING_KEY_PATH || "/etc/everleaf/launcher-manifest-private.pem"),
    portablePath: path.resolve(process.env.LAUNCHER_PORTABLE_PATH || process.env.LAUNCHER_INSTALLER_PATH || path.join(patchRoot, "downloads", "EverLeafLauncher-portable.zip")),
    announcement: process.env.LAUNCHER_ANNOUNCEMENT || "Welcome to EverLeaf. Your launcher will keep the client synchronized automatically."
  },

  cmsDbPath: path.resolve(process.env.CMS_DB_PATH || "./data/everleaf-cms.sqlite")
};
