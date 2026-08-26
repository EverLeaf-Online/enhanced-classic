# Everleaf

**Everleaf** is an Enhanced Classic MapleStory v83 server project built on top of Cosmic/HeavenMS, focused on preserving the classic feel while modernizing progression, balance, quality-of-life, and endgame.

> **Status:** Active development. Not ready for public launch.

## Vision

Everleaf is designed around a simple idea: keep what made classic MapleStory memorable, then improve the systems that aged poorly.

Core goals:

- Classic v83 identity and social gameplay
- Level cap increased to **250**
- No mandatory HP washing
- Rebalanced progression and class pain points
- Improved quests and Party Quest relevance
- Structured boss and gear progression
- Account-wide achievements and collections
- Guild progression and long-term social goals
- Expanded 200–250 endgame
- Modern testing, CI, and deployment practices
- **No pay-to-win**

## No-P2W policy

Everleaf is intended to be community-supported without selling gameplay power.

Donation/supporter rewards may include:

- Cosmetics
- Chairs and visual effects
- Cosmetic presets
- Supporter badges or titles without combat stats
- Noncompetitive quality-of-life features that do not create meaningful power advantages

Everleaf will not sell:

- Best-in-slot equipment
- Purchased combat stats
- Paid boss damage or survivability
- Better paid RNG/drop rates
- Exclusive progression power
- Ranking advantages

## Development rates

Current development targets are intentionally conservative and subject to playtesting:

- EXP: **5x**
- Meso: **3x**
- Drop: **2x**
- Boss drop: **2x**
- Quest rewards: balanced independently

These are development values, not permanent launch promises.

## Enhanced Classic progression

Everleaf treats level 200 as the beginning of extended endgame rather than the final stopping point.

Current endgame milestones:

| Tier | Level | Direction |
| --- | ---: | --- |
| Tier 1 | 200 | Entry endgame |
| Tier 2 | 210 | Advanced progression |
| Tier 3 | 225 | High-end progression |
| Tier 4 | 240 | Late endgame |
| Tier 5 | 250 | Capstone progression |

Boss access, high-level quests, equipment progression, achievements, and future weekly systems are intended to reference these shared tiers.

## Survivability / HP washing

Everleaf is being designed so players do not need to plan months of INT washing or MP washing just to participate in intended endgame content.

The server uses progression-based permanent MaxHP floors that preserve class durability differences while ensuring intended boss content remains realistically accessible.

The system is designed to be idempotent: characters only receive the missing amount needed to reach their current progression floor.

## Current development roadmap

### M0 — Baseline
- Reproducible Java 21/Maven build
- CI validation
- Configuration cleanup
- Security and database audit

### M1 — Enhanced Core
- Level 250 cap
- Post-200 EXP curve
- No-wash survivability system
- Progression framework
- Initial rate cleanup

### M2 — Classic Content Pass
- Quest improvements
- Party Quest overhaul
- Drop and economy review
- Travel/onboarding improvements
- Class pain-point fixes

### M3 — Account Systems
- Achievements
- Collections
- Monster/boss journal
- Account progression

### M4 — Boss & Endgame
- Boss progression tiers
- Gear progression
- 200–250 content
- Weekly objectives

### M5 — Social & Live Systems
- Guild progression
- Guild missions
- Events
- Rankings

### M6 — Public Infrastructure
- Website
- Account management
- Launcher/updater strategy
- Administration tools
- Monitoring and backups

### M7 — Closed Alpha
- Automated tests
- Invited playtesting
- Economy/progression telemetry
- Exploit review
- Balance iteration

## Development

### Requirements

- Java 21
- Git
- MySQL 8+
- Maven is provided through the Maven Wrapper

### Build

On Linux/macOS:

```bash
chmod +x mvnw
./mvnw clean package
```

On Windows:

```powershell
.\mvnw.cmd clean package
```

The GitHub Actions workflow builds and tests the `enhanced-dev` branch and pull requests before changes are merged into the protected `master` branch.

## Branch strategy

- `master` — protected stable branch
- `enhanced-dev` — active integration/development branch
- feature branches — used as the project grows

Changes to `master` must go through a pull request and pass the required build check.

## Project documentation

Additional design and audit documents are available in [`docs/`](docs/), including:

- Enhanced Classic project principles
- Baseline audit
- HP-washing replacement design
- Progression and endgame planning

## Upstream and license

Everleaf is a fork of **Cosmic**, which is based on a long line of MapleStory server emulators including HeavenMS and OdinMS.

The server emulator source remains subject to the upstream project's **GNU Affero General Public License v3 (AGPL-3.0)** and applicable notices. See [`LICENSE`](LICENSE) and source-file headers for details.

MapleStory, its client, artwork, music, characters, maps, and other game assets are property of their respective rights holders. This repository does not grant rights to proprietary game assets.

## Safety note

Do not blindly disable antivirus or security protections for third-party modified executables. Treat unofficial clients and binaries as untrusted unless you have independently verified their provenance and behavior.

---

**Everleaf — Classic roots. New growth.**
