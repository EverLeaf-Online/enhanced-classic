const crypto = require("crypto");
const env = require("../config/env");
const supporter = require("./supporterService");

function oauthReady() {
  return env.discord.enabled && !!env.discord.clientId && !!env.discord.clientSecret && !!env.discord.redirectUri;
}

function roleSyncReady() {
  return oauthReady() && !!env.discord.botToken && !!env.discord.guildId && !!env.discord.supporterRoleId;
}

function authorizationUrl(state) {
  if (!oauthReady()) throw new Error("Discord account linking is not available yet.");
  const query = new URLSearchParams({
    client_id: env.discord.clientId,
    response_type: "code",
    redirect_uri: env.discord.redirectUri,
    scope: "identify",
    state,
  });
  return `https://discord.com/oauth2/authorize?${query}`;
}

function newState() {
  return crypto.randomBytes(32).toString("base64url");
}

async function discordRequest(path, options = {}) {
  const response = await fetch(`https://discord.com/api/v10${path}`, options);
  if (!response.ok) {
    const error = new Error(`Discord API request failed with status ${response.status}.`);
    error.status = response.status;
    throw error;
  }
  return response.status === 204 ? null : response.json();
}

async function exchangeCode(code) {
  if (!oauthReady()) throw new Error("Discord account linking is not available yet.");
  const body = new URLSearchParams({
    client_id: env.discord.clientId,
    client_secret: env.discord.clientSecret,
    grant_type: "authorization_code",
    code,
    redirect_uri: env.discord.redirectUri,
  });
  const token = await discordRequest("/oauth2/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  try {
    return await discordRequest("/users/@me", {
      headers: { Authorization: `Bearer ${token.access_token}` },
    });
  } finally {
    token.access_token = "";
    token.refresh_token = "";
  }
}

async function syncAccount(accountId) {
  const summary = supporter.accountSummary(accountId);
  const profile = summary.profile;
  if (!profile || !profile.discord_user_id) return false;
  if (!roleSyncReady()) {
    supporter.setDiscordRoleStatus(accountId, "pending");
    return false;
  }
  if (profile.lifetime_cents <= 0) {
    supporter.setDiscordRoleStatus(accountId, "linked");
    return false;
  }
  try {
    await discordRequest(`/guilds/${env.discord.guildId}/members/${profile.discord_user_id}/roles/${env.discord.supporterRoleId}`, {
      method: "PUT",
      headers: { Authorization: `Bot ${env.discord.botToken}` },
    });
    supporter.setDiscordRoleStatus(accountId, "assigned");
    return true;
  } catch (error) {
    supporter.setDiscordRoleStatus(accountId, error.status === 404 ? "not_member" : error.status === 403 ? "permission_error" : "failed");
    return false;
  }
}

module.exports = { oauthReady, roleSyncReady, authorizationUrl, newState, exchangeCode, syncAccount };
