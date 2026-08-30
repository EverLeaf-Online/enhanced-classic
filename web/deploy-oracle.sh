#!/usr/bin/env bash
set -euo pipefail

APP_SRC="${1:-$(pwd)}"
APP_DIR="/opt/everleaf/web"
SERVER_DIR="/opt/everleaf/server"
PUBLIC_IP="132.145.141.79"

echo "=== EverLeaf web deployment ==="

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
  echo "Could not find EverLeaf-Web-CMS/package.json under: $APP_SRC"
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

DB_HOST="127.0.0.1"
DB_USER="root"
DB_PASS=""
DB_NAME="cosmic"

if [ -f "$SERVER_DIR/config.yaml" ]; then
  val="$(sed -n 's/^[[:space:]]*DB_HOST:[[:space:]]*"\([^"]*\)".*/\1/p' "$SERVER_DIR/config.yaml" | head -1 || true)"; [ -n "$val" ] && DB_HOST="$val"
  val="$(sed -n 's/^[[:space:]]*DB_USER:[[:space:]]*"\([^"]*\)".*/\1/p' "$SERVER_DIR/config.yaml" | head -1 || true)"; [ -n "$val" ] && DB_USER="$val"
  val="$(sed -n 's/^[[:space:]]*DB_PASS:[[:space:]]*"\([^"]*\)".*/\1/p' "$SERVER_DIR/config.yaml" | head -1 || true)"; DB_PASS="${val:-$DB_PASS}"
  val="$(sed -n 's#^[[:space:]]*DB_URL_FORMAT:[[:space:]]*"jdbc:mysql://[^/]*/\([^"?]*\).*#\1#p' "$SERVER_DIR/config.yaml" | head -1 || true)"; [ -n "$val" ] && DB_NAME="$val"
fi

if [ ! -f "$APP_DIR/.env" ]; then
  SECRET="$(openssl rand -hex 48)"
  sudo tee "$APP_DIR/.env" >/dev/null <<EOF
NODE_ENV=production
PORT=3000
BASE_URL=http://${PUBLIC_IP}
SESSION_SECRET=${SECRET}
TRUST_PROXY=1
COOKIE_SECURE=false

SERVER_NAME=EverLeaf
SERVER_TAGLINE=Enhanced Classic MapleStory
SERVER_VERSION=v83
DISCORD_URL=
DONATION_URL=
LAUNCHER_DOWNLOAD_URL=
FULL_CLIENT_DOWNLOAD_URL=

GAME_HOST=127.0.0.1
LOGIN_PORT=8484
CHANNEL_PORTS=7575,7576,7577

GAME_DB_HOST=${DB_HOST}
GAME_DB_PORT=3306
GAME_DB_USER=${DB_USER}
GAME_DB_PASSWORD=${DB_PASS}
GAME_DB_NAME=${DB_NAME}

GAME_ACCOUNTS_TABLE=accounts
GAME_CHARACTERS_TABLE=characters
GAME_ACCOUNT_ID_COLUMN=id
GAME_ACCOUNT_NAME_COLUMN=name
GAME_ACCOUNT_PASSWORD_COLUMN=password
GAME_ACCOUNT_EMAIL_COLUMN=email
GAME_ACCOUNT_BANNED_COLUMN=banned
GAME_ACCOUNT_LOGGEDIN_COLUMN=loggedin
GAME_CHARACTER_ACCOUNT_ID_COLUMN=accountid
GAME_CHARACTER_NAME_COLUMN=name
GAME_CHARACTER_LEVEL_COLUMN=level
GAME_CHARACTER_JOB_COLUMN=job
GAME_CHARACTER_FAME_COLUMN=fame
GAME_CHARACTER_GM_COLUMN=gm
GAME_CHARACTER_EXP_COLUMN=exp

GAME_REGISTRATION_ENABLED=true
GAME_PASSWORD_MODE=bcrypt
CMS_DB_PATH=./data/everleaf-cms.sqlite
EOF
fi

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
  const password=crypto.randomBytes(12).toString("base64url");
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
echo "=== NGINX TEST ==="
curl -fsS -H "Host: ${PUBLIC_IP}" -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1/
echo "=== PUBLIC URL ==="
echo "http://${PUBLIC_IP}"
echo
echo "$ADMIN_OUTPUT"
