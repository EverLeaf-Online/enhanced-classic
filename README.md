# Everleaf

**Classic roots. New growth.**

Everleaf is an Enhanced Classic v83 server project built on Cosmic, focused on preserving the recognizable classic MapleStory experience while modernizing progression, balance, quality-of-life, and long-term endgame play.

## Development direction

- Level cap: **250**
- EXP: **5x**
- Meso: **3x**
- Drop: **2x**
- Boss drop: **2x**
- Quest multiplier: **1x**, with direct quest balancing planned
- No mandatory HP washing
- No pay-to-win donation rewards
- Expanded 200–250 endgame progression

## Post-200 progression

Everleaf begins its extended endgame at level 200:

- **200–209 — Rooted**
- **210–224 — Awakened**
- **225–239 — Ascendant**
- **240–249 — Ancient**
- **250 — Evergreen**

The endgame is divided into boss, weekly, quest, party, collection, and guild reward lanes so one activity does not become the only meaningful progression route.

### Hybrid weeklies

Weekly objectives are character-scoped, while valuable weekly rewards and catch-up allowance are capped at the account level. This lets players enjoy alts without multiplying high-value weekly rewards across every character.

Persistent weekly state is stored in:

- `everleaf_weekly_account_state`
- `everleaf_weekly_character_objective`

Apply `database/sql/migration/everleaf_weekly_progression.sql` before enabling persistent weeklies on a database.

### Verdant Marks

Verdant Marks are Everleaf's account-bound gameplay-earned post-200 currency. A successful weekly claim updates the weekly account budget, credits the account's Verdant Marks balance, writes the immutable currency ledger entry, and consumes the character objective claim in the same database transaction.

The initial reward architecture permits progression materials, catch-up rewards, cosmetics, utility/QoL rewards, and gear-upgrade components. Finished direct best-in-slot equipment and pay-to-win reward definitions are rejected by policy code. Donation currency does not convert into Verdant Marks.

Persistent Verdant Marks state is stored in:

- `everleaf_verdant_mark_balance`
- `everleaf_verdant_mark_ledger`

Apply `database/sql/migration/everleaf_verdant_marks.sql` after the weekly progression migration. Current catalog prices and limits are development tuning values; concrete item/script fulfillment remains intentionally separate from the currency accounting layer.

Player commands:

- `@progress` — current 200–250 tier and next milestone
- `@weekly` / `@weeklies` — current UTC week, character objective progress, and account reward budget
- `@marks` / `@verdant` — account Verdant Marks balance and eligible reward preview
- `@marks history` — recent Verdant Marks ledger activity

## Development workflow

`master` is the protected stable branch. Feature development happens on dedicated branches and enters `master` through pull requests after the Java 21/Maven build passes.

The CI pipeline applies the Everleaf configuration/source transforms, compiles, runs tests, packages the server, generates a build manifest, and uploads the resulting artifact.

## Building

Requirements:

- Java 21
- Maven wrapper included in the repository

On Linux/macOS:

```bash
chmod +x mvnw
python3 tools/apply_everleaf_config.py
python3 tools/apply_level_cap_250.py
./mvnw -B package
```

The GitHub Actions workflow performs these steps automatically for active Everleaf development branches and pull requests.

## Security and deployment

Production database credentials and host configuration should be supplied outside the repository through Everleaf environment overrides. Do not expose MySQL publicly, do not run the game server as the MySQL root user, and do not enable public automatic registration without an intentional account-security design.

See `docs/DEPLOYMENT_CHECKLIST.md` before any public deployment.

## Donations

Everleaf's donation policy is no-P2W. Donations may support cosmetics, visual effects, chairs, cosmetic presets, supporter badges/titles without combat stats, and carefully reviewed noncompetitive conveniences. Donations must not purchase best-in-slot equipment, stats, damage, survivability, better drop odds, or ranking advantages.

## Upstream

Everleaf is built from the Cosmic v83 server emulator and retains the upstream project's AGPL-3.0 licensing requirements and historical attribution. See the repository license and source history for details.