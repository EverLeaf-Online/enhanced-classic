# EverLeaf original-site Maple remaster — release checklist

This document covers the source-only redesign of the existing Oracle-hosted Express/EJS site at `everleafms.online`.

## Scope locked for this release

- Shared public navigation, announcements, mobile menu, footer, and EverLeaf remaster branding.
- Maple/v83-inspired homepage with existing local world art, live server status, launcher entry points, class showcase, news, and rankings.
- Adventurer class emblems plus Cygnus Knights, Aran, and Evan identity surfaces.
- News/post, downloads, rankings, help, support, CMS-managed pages, account, login/register/recovery, and 404/500 presentation.
- Player portal character roster and reward/community/security surfaces.
- Staff CMS overview and shared manager styling.
- Local UI assets for launcher, patching, tools, rankings, journal, community, account, and recovery.
- Local asset import workflow for later approved v83 exports.

## Explicitly out of scope

- Game-server code or process changes.
- Game database schema or data changes.
- DNS or TLS changes.
- Oracle host migration or reconfiguration.
- Launcher/client binary changes.
- Replacing working backend routes, form actions, authentication, server-status providers, or CMS data bindings.

## Automated gates

Before merge, both should pass on the final PR head:

1. `Web Maple Overhaul CI`
   - Node web tests.
   - All remaster CSS layers present.
   - Local class and UI asset set present.
   - Homepage, Help, Downloads, Rankings, and Account remaster markers present.
2. Repository `Run build`
   - Website/CMS tests.
   - Existing economy/reward/world audits.
   - Maven compile/test/package and build manifest.

## Production behavior

`master` pushes touching `web/**` trigger `.github/workflows/deploy-web.yml` and deploy to the Oracle-hosted production website. Therefore the PR must remain unmerged until production deployment is explicitly approved.

The deployment workflow performs a production backup before synchronizing the web app and restarting/verifying the website service. No manual Oracle commands should be needed for this visual release.

## Post-deploy smoke test

Check these routes immediately after deployment:

- `/`
- `/news`
- `/downloads`
- `/rankings`
- `/help`
- `/login`
- `/register`
- `/recover`
- `/account` with a test account
- `/admin` with authorized staff access
- `/404-test` or another nonexistent route

Verify:

- Header/footer/mobile navigation render correctly.
- All local `/assets/jobs/*` and `/assets/ui/*` images return successfully.
- Server status/player/channel values still populate.
- News and rankings still read existing data.
- Launcher/download URLs are unchanged and usable.
- Login, register, recovery, password change, logout, Discord link, vote links, and CMS forms retain their existing behavior.
- No third-party image hotlinks are required for core UI.

## Rollback

If production smoke testing finds a blocking presentation or runtime regression:

1. Use the production backup created by the existing deployment workflow or redeploy the previous known-good `master` web revision.
2. Verify `https://everleafms.online` and `/api/status` after rollback.
3. Keep the remaster branch/PR intact for correction; do not modify game data to address a web presentation regression.

## Asset policy

External MapleStory resources are research/reference or asset-export inputs. Production templates should use locally stored, versioned files. The importer at `web/scripts/import-maple-assets.js` is the supported path for approved/exported sprites and icons so the website does not depend on hotlinks.
