import crypto from "node:crypto";
import { spawnSync } from "node:child_process";

const baseUrl = "https://everleafms.online";
const username = `e2e${Date.now().toString(36)}`.slice(0, 13);
const email = `${username}@example.invalid`;
const originalPassword = crypto.randomBytes(9).toString("base64url");
const replacementPassword = crypto.randomBytes(9).toString("base64url");

async function post(path, fields, cookie) {
  const response = await fetch(`${baseUrl}${path}`, {
    method: "POST",
    redirect: "manual",
    headers: {
      "content-type": "application/x-www-form-urlencoded",
      ...(cookie ? {cookie} : {})
    },
    body: new URLSearchParams(fields)
  });
  return response;
}

function expectRedirect(response, location) {
  if (response.status !== 302 || response.headers.get("location") !== location) {
    throw new Error(`Expected redirect to ${location}; received HTTP ${response.status}.`);
  }
}

const registration = await post("/register", {
  username, email, password: originalPassword,
  confirmPassword: originalPassword, agree: "yes"
});
expectRedirect(registration, "/login");
console.log(`ACCOUNT_CREATED=${username}`);

const initialLogin = await post("/login", {username, password: originalPassword});
expectRedirect(initialLogin, "/account");
const cookie = initialLogin.headers.get("set-cookie")?.split(";", 1)[0];
if (!cookie) throw new Error("Website login did not establish a session.");
console.log("WEBSITE_INITIAL_LOGIN=true");

const change = await post("/account/password", {
  currentPassword: originalPassword,
  newPassword: replacementPassword,
  confirmPassword: replacementPassword
}, cookie);
expectRedirect(change, "/account?updated=1");
console.log("WEBSITE_PASSWORD_CHANGE=true");

const obsoleteLogin = await post("/login", {username, password: originalPassword});
if (obsoleteLogin.status !== 401) throw new Error("Old password remained valid after the change.");
console.log("WEBSITE_OLD_PASSWORD_REJECTED=true");

const replacementLogin = await post("/login", {username, password: replacementPassword});
expectRedirect(replacementLogin, "/account");
console.log("WEBSITE_REPLACEMENT_LOGIN=true");

const gameProbe = spawnSync("java", [
  "-cp", "/opt/everleaf/current/target/everleaf-server-1.0-SNAPSHOT.jar:/tmp",
  "EverLeafGameLoginProbe", "127.0.0.1", "8484", username
], {
  encoding: "utf8",
  env: {...process.env, EVERLEAF_TEST_PASSWORD: replacementPassword}
});
process.stdout.write(gameProbe.stdout);
if (gameProbe.status !== 0) {
  throw new Error(`Game login probe failed: ${gameProbe.stderr.trim()}`);
}
