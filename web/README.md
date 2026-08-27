# EverLeaf Website + CMS

This is a deployable web portal built for the EverLeaf MapleStory v83 server.

## Included
- Home page
- Server status
- Online player count
- Rankings
- Player login
- Player registration
- Player account portal
- Downloads / launcher page
- News and patch notes
- Community and support pages
- Donation/support page
- Admin CMS
- Separate CMS database
- Server-side MySQL adapter for the game database
- Secure sessions, rate limiting and headers

## Security
The production `.env` stays on the server only. Runtime CMS data is also kept outside Git and backed up before deployment.

Players never receive database credentials, internal server config, admin credentials, Java server config, or secret keys.

## Installation
```bash
cp .env.example .env
npm install
npm run init-db
npm run create-admin
npm start
```

## Recommended layout
```text
/opt/everleaf/server   # enhanced-classic Java server
/opt/everleaf/web      # this project
/opt/everleaf/client   # launcher/client release files
```

## Registration
EverLeaf website registration uses BCrypt for all newly created accounts. The current `enhanced-classic` login server accepts BCrypt directly and also recognizes legacy plaintext, SHA-1, and SHA-512 passwords for older accounts. Website-created accounts explicitly set `tos=1`; all other required account fields use the defaults defined by the EverLeaf/Cosmic `accounts` table.

```env
GAME_REGISTRATION_ENABLED=true
GAME_PASSWORD_MODE=bcrypt
```

## Launcher API
`GET /api/launcher/manifest` returns the currently published launcher/client/patch downloads.

## Player account portal
Authenticated players can view all characters on their account and change the password used by both the website and EverLeaf game client. New passwords are stored as BCrypt.

The homepage refreshes server status, online players, and online channel counts every 30 seconds through `/api/status`.

## Oracle VM deployment
Run `deploy-oracle.sh` to install/update the site at `/opt/everleaf/web`, install the `everleaf-web` systemd service, configure Nginx, preserve the CMS database and `.env`, and auto-detect the live EverLeaf MySQL configuration from `/opt/everleaf/server/config.yaml`.

While the site is served over plain HTTP by public IP:

```env
COOKIE_SECURE=false
```

Change it to `true` after a domain and HTTPS certificate are configured.

## GitHub deployment
The repository-level workflow `.github/workflows/deploy-web.yml` deploys changes under `web/` after they are merged to `master`. Runtime `.env`, CMS SQLite data, and `node_modules` are preserved on the Oracle VM. Production state is backed up before each deployment.

Required repository secrets:
- `EVERLEAF_HOST`
- `EVERLEAF_SSH_USER`
- `EVERLEAF_SSH_PRIVATE_KEY`
- `EVERLEAF_SSH_KNOWN_HOSTS`
