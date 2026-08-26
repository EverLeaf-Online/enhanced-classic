# Everleaf — Enhanced Classic v83

**Everleaf** is a custom gameplay fork of Cosmic targeting the feel of classic Global MapleStory v83 with modernized progression, balance, quality-of-life, and long-term endgame systems.

## Core principles

1. **No pay-to-win.** Gameplay power, competitive advantages, boss progression, and best-in-slot equipment are earned through gameplay.
2. **Classic identity first.** Preserve recognizable v83 combat, maps, jobs, social play, party quests, and progression while improving weak or obsolete systems.
3. **No mandatory HP washing.** Characters should be able to participate in intended endgame encounters without legacy HP-washing requirements.
4. **Useful content.** Quests, party quests, exploration, bosses, crafting, collections, and guild activities should remain worthwhile instead of becoming dead content.
5. **Long-term progression.** Reaching the level cap should not exhaust meaningful account goals.
6. **Transparent economy.** Avoid systems that create paid power or uncontrolled currency/item inflation.
7. **Test before tuning.** Rates and balance values are initial targets and will change based on simulations, automated tests, and playtesting.

## Initial development rates

These are development targets, not permanent launch promises.

- EXP: 5x
- Meso: 3x
- Drop: 2x
- Boss drop: 2x initially
- Quest rewards: to be rebalanced independently rather than relying solely on a global multiplier

## Planned systems

### Foundation
- Environment-safe configuration
- Development / testing / production profiles
- Automated build and regression testing
- Database migration discipline
- Logging and operational health checks

### Progression
- Revised leveling curve and training alternatives
- Level cap 250
- No mandatory HP washing
- Quest reward overhaul
- Party Quest reward and relevance overhaul
- Improved travel and early-game onboarding

### Classes
- Data-driven class balance targets
- Fix severely underperforming or dysfunctional skills first
- Preserve class identity rather than homogenizing jobs
- Separate PvE balance decisions from convenience changes

### Account progression
- Account-wide achievements
- Monster and boss collection/journal
- Exploration milestones
- Account progression rewards that avoid runaway stat inflation

### Endgame
- Shared progression tiers at 200 / 210 / 225 / 240 / 250
- Clear boss progression tiers
- Normal/Hard variants where appropriate
- Gear progression with multiple acquisition paths
- Weekly objectives and longer-term goals
- Additional endgame progression beyond simply reaching level cap

### Social
- Guild progression
- Guild missions
- Party-focused incentives
- Community events

## Donations

Donations support operation and development. Donation rewards must not determine competitive strength.

Allowed direction:
- Cosmetics
- Chairs and visual effects
- Cosmetic presets
- Supporter badges/titles without combat stats
- Noncompetitive quality-of-life where it does not create meaningful gameplay power

Disallowed direction:
- Exclusive best-in-slot equipment
- Purchased stats
- Paid boss damage or survivability
- Better paid RNG/drop odds
- Exclusive progression power
- Paid ranking advantages

## Milestones

### M0 — Baseline
Get the fork building and running reproducibly. Document database, server, and client assumptions.

### M1 — Enhanced Core
Establish configuration, rates, progression rules, HP-wash replacement strategy, telemetry, level-250 support, and balance framework.

### M2 — Classic Content Pass
Improve quests, Party Quests, drops, travel, early/mid-game progression, and class pain points.

### M3 — Account Systems
Achievements, collections, journal, account progression, and supporting UI/NPC interfaces.

### M4 — Boss & Endgame
Boss tiers, gear progression, weekly systems, endgame rewards, and expanded 200–250 progression.

### M5 — Social & Live Systems
Guild progression, events, seasons/rotations where appropriate, rankings, and community systems.

### M6 — Public Infrastructure
Website, account management, launcher/updater strategy, administration tools, backups, monitoring, and deployment hardening.

### M7 — Closed Alpha
Automated tests plus invited playtesting, economy simulation, progression telemetry, exploit review, and balance iteration.

## Current status

- Server name: **Everleaf**.
- Upstream foundation forked from Cosmic.
- `enhanced-dev` is the integration branch for Everleaf development.
- CI compiles, runs the regression suite, packages the server, and publishes successful build artifacts.
- Everleaf development configuration is applied deterministically in CI.
- Level cap 250 support and regression coverage are in place.
- The no-mandatory-HP-washing survivability policy and service are implemented with tests.
- Shared endgame tiers and level-based progression unlock policy are implemented with tests.
- M0 is substantially established; remaining foundation work includes operational health checks and database migration hardening.
- M1 is active; the next gameplay work is progression/rate telemetry and the first M2 quest/PQ/content passes.
