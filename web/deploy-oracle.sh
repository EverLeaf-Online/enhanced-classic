#!/usr/bin/env bash
set -euo pipefail

APP_SRC="${1:-$(pwd)}"
APP_DIR="/opt/everleaf/web"
PUBLIC_HOST="everleafms.online"

echo "=== EverLeaf web deployment ==="

echo "This helper never derives database credentials from the game-server config."
echo "Provision $APP_DIR/.env separately with the least-privileged everleaf_web account before first use."

sudo apt-get update -y
sudo apt-get install -y curl ca-certificates gnupg unzip build-essential python3 make g++ rsync openssl

need_node=1
if command -v node >/dev/null 2>&1; then
  major="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)"
  if [ "${major:-0}" -ge 20 ]; then need_node=0; fi
fi

if [ "$need_node" -eq 1 ]; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

echo "Node: $(node -v)"
echo "npm:  $(npm -v)"

if [ -f "$APP_SRC/package.json" ]; then
  SRC="$APP_SRC"
elif [ -f "$APP_SRC/EverLeaf-Web-CMS/package.json" ]; then
  SRC="$APP_SRC/EverLeaf-Web-CMS"
else
  echo "Could not find EverLeaf Web CMS package.json under: $APP_SRC"
  exit 1
fi

sudo mkdir -p "$APP_DIR"
if [ -f "$APP_DIR/.env" ]; then sudo cp "$APP_DIR/.env" /tmp/everleaf-web.env.keep; fi
if [ -d "$APP_DIR/data" ]; then sudo cp -a "$APP_DIR/data" /tmp/everleaf-web-data.keep; fi

sudo rsync -a --delete \
  --exclude '.env' \
  --exclude 'data/' \
  --exclude 'node_modules/' \
  "$SRC/" "$APP_DIR/"

if [ -f /tmp/everleaf-web.env.keep ]; then sudo mv /tmp/everleaf-web.env.keep "$APP_DIR/.env"; fi
if [ -d /tmp/everleaf-web-data.keep ]; then sudo rm -rf "$APP_DIR/data"; sudo mv /tmp/everleaf-web-data.keep "$APP_DIR/data"; fi

if [ ! -f "$APP_DIR/.env" ]; then
  echo "ERROR: $APP_DIR/.env is not provisioned." >&2
  echo "Copy web/.env.example to that protected location and set SESSION_SECRET plus a dedicated GAME_DB_USER/GAME_DB_PASSWORD before deploying." >&2
  exit 2
fi

# Refuse known unsafe production values instead of silently bootstrapping them.
if grep -Eq '^GAME_DB_USER=(root|)$' "$APP_DIR/.env"; then
  echo "ERROR: GAME_DB_USER must be a dedicated least-privilege web account, not root." >&2
  exit 3
fi
if grep -Eq '^GAME_DB_PASSWORD=(|replace-me)$' "$APP_DIR/.env"; then
  echo "ERROR: GAME_DB_PASSWORD is not configured." >&2
  exit 4
fi
if grep -Eq '^SESSION_SECRET=(dev-only-change-me|replace-with-a-long-random-secret|)$' "$APP_DIR/.env"; then
  echo "ERROR: SESSION_SECRET is not production-safe." >&2
  exit 5
fi
if ! grep -q '^GTOP100_PINGBACK_KEY=' "$APP_DIR/.env" || grep -Eq '^GTOP100_PINGBACK_KEY=(|replace-with-the-key-from-gtop100)$' "$APP_DIR/.env"; then
  echo "ERROR: GTOP100_PINGBACK_KEY must be provisioned before enabling the EverLeaf Vote Point flow." >&2
  exit 6
fi
if ! grep -Eq '^GTOP100_VOTE_URL=https://(www\.)?gtop100\.com/' "$APP_DIR/.env"; then
  echo "ERROR: GTOP100_VOTE_URL must be an HTTPS gtop100.com URL." >&2
  exit 7
fi

set_env_var() {
  local key="$1"
  local value="$2"
  if grep -q "^${key}=" "$APP_DIR/.env"; then
    sudo sed -i "s|^${key}=.*|${key}=${value}|" "$APP_DIR/.env"
  else
    printf '%s=%s\n' "$key" "$value" | sudo tee -a "$APP_DIR/.env" >/dev/null
  fi
}

set_env_var NODE_ENV production
set_env_var BASE_URL "https://${PUBLIC_HOST}"
set_env_var TRUST_PROXY 1
set_env_var COOKIE_SECURE true
set_env_var GAME_HOST 127.0.0.1
set_env_var LOGIN_PORT 8484
set_env_var CHANNEL_PORTS 7575,7576,7577,7578,7579,7580,7581,7582
set_env_var GAME_ACCOUNT_VOTE_POINTS_COLUMN votepoints
set_env_var VOTE_POINTS_REWARD 1

sudo chown -R ubuntu:ubuntu "$APP_DIR"
sudo chmod 600 "$APP_DIR/.env"
sudo -u ubuntu mkdir -p "$APP_DIR/data"

cd "$APP_DIR"
if [ -f package-lock.json ]; then sudo -u ubuntu npm ci --omit=dev; else sudo -u ubuntu npm install --omit=dev; fi
sudo -u ubuntu npm run init-db

ADMIN_OUTPUT="$(sudo -u ubuntu node <<'NODE'
const bcrypt=require("bcryptjs");
const crypto=require("crypto");
const {db,initCms}=require("./src/db/cms");
initCms();
const n=db.prepare("SELECT COUNT(*) n FROM admins").get().n;
if(n===0){
  const username="everleafadmin";
  const password=crypto.randomBytes(18).toString("base64url");
  const hash=bcrypt.hashSync(password,12);
  db.prepare("INSERT INTO admins(username,password_hash) VALUES(?,?)").run(username,hash);
  console.log(`CREATED_ADMIN=${username}`);
  console.log(`CREATED_PASSWORD=${password}`);
}else console.log("ADMIN_ALREADY_EXISTS=1");
NODE
)"

sudo install -m 644 "$APP_DIR/ops/everleaf-web.service" /etc/systemd/system/everleaf-web.service
sudo mkdir -p /etc/nginx/conf.d
sudo install -m 644 "$APP_DIR/ops/nginx-everleaf.conf" /etc/nginx/conf.d/everleaf.conf
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl daemon-reload
sudo systemctl enable --now everleaf-web
sudo systemctl restart everleaf-web nginx
sleep 3

echo
echo "=== SERVICE ==="
sudo systemctl is-active everleaf-web
echo "=== NODE TEST ==="
curl -fsS -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:3000/
echo "=== VOTE PINGBACK STATUS ==="
curl -fsS http://127.0.0.1:3000/api/vote/pingback
echo
echo "=== NGINX TEST ==="
curl -fsS -H "Host: ${PUBLIC_HOST}" -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1/
echo "=== PUBLIC URL ==="
echo "https://${PUBLIC_HOST}"
echo
echo "$ADMIN_OUTPUT"