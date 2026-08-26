# Everleaf — Enhanced Classic v83

**Classic roots. New growth.**

Everleaf is an Enhanced Classic MapleStory v83 server project built on Cosmic. It keeps the recognizable classic-game foundation while extending progression, reducing obsolete pain points, and creating a longer endgame through level 250.

## Current direction

- Level cap: **250**
- Development rates: **5x EXP / 3x meso / 2x drop / 2x boss drop**
- No mandatory HP washing
- No pay-to-win donation progression
- Post-200 endgame milestones at **200 / 210 / 225 / 240 / 250**
- Named endgame phases: **Rooted / Awakened / Ascendant / Ancient / Evergreen**
- Multiple progression lanes instead of one mandatory activity
- Java 21 + Maven + GitHub Actions validation
- Packaged CI server artifacts with build metadata

## Post-200 progression

Everleaf treats level 200 as the beginning of extended endgame rather than the finish line. Progression is split across six lanes:

- Boss
- Weekly
- Quest
- Party
- Collection
- Guild

The initial weekly framework uses deterministic Monday 00:00 UTC reset windows, tier-based weekly budgets, bounded objective rewards, and a two-week catch-up bank model. Exact content rewards and balance values remain development targets until playtesting.

Player commands currently include:

- `@progress` — current level, Everleaf tier, next milestone, and weekly budget.
- `@weekly` / `@weeklies` — currently eligible weekly objective templates.

See `docs/PROGRESSION_200_250.md` for the design model.

## Core principles

1. **Classic identity first.** Preserve recognizable v83 jobs, maps, combat, social systems, party quests, and progression.
2. **No pay-to-win.** Donations may support the server, but gameplay power and competitive progression are earned in game.
3. **No mandatory HP washing.** Endgame survivability should not require legacy INT/MP washing plans.
4. **Useful content.** Quests, party play, bosses, exploration, collections, and guild activities should remain relevant.
5. **Long-term progression.** Reaching level 200 or 250 should not exhaust meaningful account goals.
6. **Test before tuning.** Rates, HP floors, weekly budgets, and endgame rewards are development values until validated through testing.

## Development workflow

`master` is the protected stable branch. Feature work is performed on development branches and merged through pull requests after CI succeeds.

The build pipeline applies Everleaf configuration/source transforms, compiles and tests with Java 21, packages the server, generates build metadata, and uploads the resulting server artifact.

## Deployment configuration

Production credentials and hosts should be supplied using the supported `EVERLEAF_*` environment overrides rather than committed directly to `config.yaml`. See `docs/DEPLOYMENT_CHECKLIST.md` for the current deployment checklist and safety rules.

## Upstream and licensing

Everleaf is derived from Cosmic and the broader OdinMS/HeavenMS ecosystem. Upstream copyright and AGPL licensing notices remain applicable. This project is not affiliated with or endorsed by Nexon.
