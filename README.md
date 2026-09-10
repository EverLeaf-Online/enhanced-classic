# EverLeaf

**Classic roots. New growth.**

EverLeaf is an Enhanced Classic MapleStory v83 server project built on Cosmic, focused on preserving the recognizable classic experience while modernizing progression, balance, quality-of-life, client stability, security, and long-term endgame play.

## Current project state

EverLeaf is an actively maintained production server with the game server, native Windows client work, launcher/patcher, website/CMS, deployment tooling, audits, and operational workflows maintained in this repository.

- Canonical branch: **`master`**
- Public site: **https://everleafms.online**
- Player-facing game relay: **`129.159.114.146`**
- Production deployment origin: Oracle Cloud
- Runtime: Java 21 / Maven
- Client: MapleStory v83 Win32 with EverLeaf-native runtime extensions
- Channels: **20**
- Login port: **8484**
- Game channel ports: **7575–7594**
- Canonical v95 production XML baseline: **44,237 files**
- Latest full production rebuild/restart completed successfully on **2026-09-10** from `92a646d6c42a4f5e100f8a0b2ccc6f1bfcabd45a`.

The canonical working roadmap and detailed implementation status live in [`docs/EVERLEAF_MASTER_CHECKLIST.md`](docs/EVERLEAF_MASTER_CHECKLIST.md). That file should be treated as the authoritative development checklist rather than old PR descriptions, retired branches, or historical workflow runs.

## Development direction

- Level cap: **250**
- EXP: **5x**
- Meso: **3x**
- Drop: **2x**
- Boss drop: **2x**
- Quest multiplier: **1x**, with direct quest balancing
- No mandatory HP washing
- No pay-to-win donation rewards
- Expanded 200–250 endgame progression
- EverLeaf-specific survivability progression
- Future Henesys / Stronghold / Fallen Cygnus content
- Continued exploit, transaction, quest, boss, and multiplayer hardening

## Native client and launcher

EverLeaf maintains its own v83 Windows client integration rather than treating the client as an unmodified external binary.

Current client work includes:

- EverLeaf network/bootstrap configuration
- Launcher-managed client updates
- Win32 startup/bootstrap hardening
- Windowed, borderless, and Alt+Enter support
- Widescreen/runtime corrections
- Presentation-only frame limiting without changing Maple game-logic timing
- Crash/freeze diagnostics without automatic telemetry upload
- WASD input support
- Native Discord Rich Presence through local Discord IPC
- Managed WZ/client overlays distributed through the patch system

The broader login/world/character-selection visual overhaul is intentionally deferred until the Kaentake client review is complete. Native Discord Rich Presence was separated from that visual scope and shipped independently.

## Post-200 progression

EverLeaf begins its extended endgame at level 200:

- **200–209 — Rooted**
- **210–224 — Awakened**
- **225–239 — Ascendant**
- **240–249 — Ancient**
- **250 — Evergreen**

The endgame is divided across boss, weekly, quest, party, collection, and guild reward lanes so one activity does not become the only meaningful progression route.

### Hybrid weeklies

Weekly objectives are character-scoped, while valuable weekly rewards and catch-up allowance are capped at the account level. This allows alt play without multiplying high-value weekly rewards across every character.

Persistent weekly state is stored in:

- `everleaf_weekly_account_state`
- `everleaf_weekly_character_objective`

Apply `database/sql/migration/everleaf_weekly_progression.sql` before enabling persistent weeklies on a new database.

### Verdant Marks

Verdant Marks are EverLeaf's account-bound, gameplay-earned post-200 currency. A successful weekly claim updates the weekly account budget, credits the account balance, records the immutable ledger entry, and consumes the character objective claim in the same database transaction.

The reward architecture permits progression materials, catch-up rewards, cosmetics, utility/QoL rewards, and gear-upgrade components. Finished direct best-in-slot equipment and pay-to-win reward definitions are rejected by policy code. Donation currency does not convert into Verdant Marks.

Persistent Verdant Marks state is stored in:

- `everleaf_verdant_mark_balance`
- `everleaf_verdant_mark_ledger`

Apply `database/sql/migration/everleaf_verdant_marks.sql` after the weekly progression migration.

Player commands include:

- `@progress` — current 200–250 tier and next milestone
- `@weekly` / `@weeklies` — current UTC week, character objective progress, and account reward budget
- `@marks` / `@verdant` — account Verdant Marks balance and eligible reward preview
- `@marks history` — recent Verdant Marks ledger activity

## Production content baseline

EverLeaf production uses a canonical full-v95 XML baseline during release staging rather than depending on the smaller repository WZ tree alone. The production deployment validates required maps, mobs, NPCs, quests, and content invariants before switching releases.

Implemented content includes Future Henesys/Henesys Ruins, Stronghold content, Fallen Cygnus/Empress data and encounter support, and the associated v95-backed content required by those systems. Remaining work is primarily live gameplay, balance, transition, prerequisite, and multiplayer regression rather than basic content import.

## Development workflow

`master` is the single canonical branch.

Routine repository maintenance, documentation updates, source edits, and workflow changes can be written directly to protected `master` through the authorized Codex connector bypass. Hosted runners are intentionally reserved for work that actually needs execution, such as:

- Java build/test validation when required
- Windows native-client compilation
- client/launcher/WZ artifact publication
- production deployment and restart
- production health verification
- explicit audit workflows

Heavy QA/build workflows are manual-only unless there is a deliberate reason to run them. This keeps GitHub Actions usage focused and avoids generating large numbers of redundant or skipped workflow runs.

## Building the game server

Requirements:

- Java 21
- Maven wrapper included in the repository
- Python 3 for EverLeaf source/config transforms

On Linux/macOS:

```bash
chmod +x mvnw
python3 tools/apply_everleaf_config.py
python3 tools/apply_level_cap_250.py
./mvnw -B package
```

Production deployment applies the complete maintained transform chain, stages the canonical production WZ baseline, builds the release on Oracle, verifies the JAR, takes a backup, atomically switches `/opt/everleaf/current`, restarts `everleaf.service`, validates login/channel health, verifies the public relay ports, and retains the previous release for rollback.

## Production layout

The current production layout is release-based:

- Source checkout: `/opt/everleaf/server`
- Active release symlink: `/opt/everleaf/current`
- Releases: `/opt/everleaf/releases/`
- Game service: `everleaf.service`
- Website checkout: `/opt/everleaf/web-repo`
- Website runtime symlink: `/opt/everleaf/web`
- Mutable website state: `/opt/everleaf/web-state`
- Website service: `everleaf-web.service`

Player traffic is advertised through the EverLeaf relay, while GitHub deployment and server administration continue to target the Oracle origin directly.

## Security and deployment

Production database credentials, SSH material, tokens, and mutable runtime secrets must remain outside source control. MySQL should not be exposed publicly, the game server should not run as the MySQL root user, and production registration/authentication policy should remain deliberate and auditable.

Deployment uses staged releases with backup, health validation, and automatic rollback behavior. See [`docs/DEPLOYMENT_CHECKLIST.md`](docs/DEPLOYMENT_CHECKLIST.md) and the master checklist before production changes.

## Backups and disaster recovery

EverLeaf has automated OCI Object Storage backups covering MySQL and critical production configuration/server/web data, plus broader periodic recovery material. Production deployment runs a backup stage before switching releases. Restore testing and full disaster-recovery rehearsals remain part of the operational roadmap.

## Donations

EverLeaf's donation policy is no-P2W. Donations may support cosmetics, visual effects, chairs, cosmetic presets, supporter badges/titles without combat stats, and carefully reviewed noncompetitive conveniences.

Donations must not purchase best-in-slot equipment, stats, damage, survivability, better drop odds, progression currency, or ranking advantages.

## Upstream and licensing

EverLeaf is built from the Cosmic v83 server emulator and retains the upstream project's AGPL-3.0 licensing requirements and historical attribution. See the repository license and source history for details.
