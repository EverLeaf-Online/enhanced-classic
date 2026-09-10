# EverLeaf Player Progression and Content Guide

This is the maintained player-facing overview of EverLeaf's progression, rates, reward currencies, survivability policy, and major custom/endgame content. Exact implementation/readiness status remains tracked in the master development checklist; this guide explains the intended player experience without exposing staff-only or exploit-sensitive details.

## Server rates and level cap

Current EverLeaf baseline:

- **Level cap:** 250
- **EXP:** 5x
- **Mesos:** 3x
- **Normal drop:** 2x
- **Boss drop:** 2x
- **Quest multiplier:** 1x, with quests balanced directly where needed

Use `@rates` / `@showrates` in game to view the active rate information exposed by the server.

EverLeaf does not use paid rate coupons or paid progression power as part of its no-P2W policy.

## Classic progression first

EverLeaf is built around the recognizable MapleStory v83 progression structure, with modernized balance, QoL, security, and an extended endgame rather than replacing the early/midgame with an unrelated leveling system.

Playable class families include:

- Explorers
- Cygnus Knights
- Aran
- Evan

The accepted Evan creation path currently starts as a Beginner and uses the in-game NPC conversion/progression path. Direct modern class-card Evan creation is intentionally paused while the broader character-selection redesign is deferred.

## Level 200–250 endgame

EverLeaf extends meaningful progression beyond the classic level-200 ceiling.

- **200–209 — Rooted**
- **210–224 — Awakened**
- **225–239 — Ascendant**
- **240–249 — Ancient**
- **250 — Evergreen**

Level 250 is the terminal character level. Evergreen progression is intended to continue through mastery, collection, weekly, boss, party, utility, cosmetic, and prestige goals rather than raising the level cap indefinitely.

Use:

```text
@progress
```

to view your current post-200 tier and next milestone where supported by the live release.

## Weekly progression

EverLeaf uses a hybrid weekly model:

- objective progress can be character-specific;
- high-value weekly reward allowance is capped at the account level;
- playing alts is allowed without multiplying valuable weekly rewards indefinitely;
- claims are persisted so disconnect/retry behavior does not intentionally create duplicate payouts.

Use:

```text
@weekly
@weeklies
```

to view the current weekly state exposed by the server.

## Verdant Marks

**Verdant Marks** are EverLeaf's account-bound post-200 progression currency.

They are:

- earned through approved gameplay progression;
- stored at the account level;
- not a normal inventory item;
- not tradeable between players;
- not purchasable by converting donation/premium currency;
- intended for controlled progression materials, catch-up rewards, cosmetics, utility/QoL rewards, and upgrade components rather than direct finished best-in-slot gear.

Commands:

```text
@marks
@verdant
@marks history
```

The history view exposes recent account ledger activity where supported.

## Party Quest Points

**PQ Points** provide a persistent reward layer for supported Party Quests so group content can remain relevant without making every PQ directly drop the same high-value item.

Supported PQs may award different point values based on difficulty/time. Exchange pricing and reward selection are balance parameters and can change as alpha/beta testing gives better completion-time and economy data.

The current server has PQ Point values for major retained content including Henesys, Kerning, Ludibrium, Ludi Maze, Ellin, Orbis, Pirate, Magatia/Romeo & Juliet, Amoria, and CWKPQ paths. Full multi-client regression/balance testing is still part of release hardening.

## NX / Cash Shop rewards

EverLeaf supports gameplay/vote-related account-level NX Credit reward infrastructure while keeping donation rewards separate from gameplay power.

The no-P2W boundary means donations must not buy:

- damage/stats;
- survivability advantages;
- best-in-slot equipment;
- better drop/RNG odds;
- Verdant Marks or equivalent progression currency;
- ranking advantages;
- bypasses around intended boss/PQ progression.

Cosmetics and carefully reviewed noncompetitive convenience are acceptable donation/supporter directions.

## No mandatory HP washing

EverLeaf does **not** require legacy HP/MP washing knowledge as an endgame prerequisite.

The server applies a class/progression-aware minimum survivability floor that:

- preserves different class HP identities;
- guarantees a minimum rather than forcing every class to the same HP;
- does not reduce legitimate HP above the floor;
- preserves legacy washed HP above the minimum;
- prevents AP Reset behavior from crossing below the EverLeaf survivability floor.

This system is still subject to boss-damage and balance tuning, but the design goal is clear: players should be able to build a legitimate character without hidden washing requirements.

## Future Henesys / Stronghold / Fallen Cygnus

EverLeaf includes the backported v95-era Future Henesys / Henesys Ruins and Stronghold content baseline plus Fallen Cygnus/Empress encounter support.

The base content import, maps/data/NPCs/scripts/portals, and encounter implementation are present. Ongoing alpha work is focused more on multiplayer encounter balance, prerequisites, transitions, cleanup, and reward validation than on importing the area itself.

## Bosses

Major retained/implemented boss content includes paths such as:

- Zakum
- Horntail
- Papulatus
- Pink Bean
- Fallen Cygnus / Empress
- additional retained bosses such as Pianus/Balrog where enabled

Boss prerequisites, death/re-entry, disconnect behavior, phase cleanup, lockouts, and reward balance continue to receive runtime regression testing during alpha/beta hardening.

## Party Quests

EverLeaf retains a broad classic PQ direction, including major content such as:

- Henesys PQ
- Kerning PQ
- Ludibrium PQ
- Ludi Maze
- Ellin PQ
- Orbis PQ
- Pirate PQ
- Romeo & Juliet / Magatia PQ
- Amoria PQ
- CWKPQ
- Guild PQ where retained/enabled

Not every retained script should be interpreted as fully public-ready merely because it exists in the repository. The project is still completing multi-client lifecycle/reward testing before public beta.

## Rare scrolls and economy

Ordinary global monster-drop faucets for **Chaos Scroll** and **White Scroll** have been removed from the current policy. High-value scroll supply is intended to come from controlled sources such as selected bosses, PQ rewards/exchanges, and rare Gachapon pools. White Scroll supply should remain tighter than Chaos Scroll supply.

Rates and high-value reward sources may be tuned as live economy data becomes available.

## Useful player commands

Common progression/support commands include:

```text
@help / @commands
@rates / @showrates
@progress
@weekly / @weeklies
@marks / @verdant
@marks history
@points
@vote
@whodrops
@whatdropsfrom
@bosshp
@mobhp
@reportbug
@gm
```

Use `@help`/`@commands` for the current in-game registration rather than an old web/forum command list.

## Reporting progression/content problems

When reporting a quest, boss, PQ, drop, progression, or reward issue, include:

- character job and approximate level;
- map/NPC/boss/PQ involved;
- exact step/action;
- expected vs actual result;
- whether relog/channel change reproduced it;
- timestamp/time zone;
- screenshot/video/log when relevant.

For suspected duplication or an exploitable reward/security bug, do **not** publish detailed reproduction steps publicly. Report it through staff/support so it can be contained and fixed without encouraging abuse.

See [`../KNOWN_ISSUES.md`](../KNOWN_ISSUES.md) for current known limitations and validation risks.