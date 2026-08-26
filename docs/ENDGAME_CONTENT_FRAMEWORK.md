# Everleaf Endgame Content Framework

This document defines the stable contracts used to attach concrete bosses, PQs, quests, forge recipes, collections, and guild objectives to the level 200–250 progression system.

## Milestone identities

- 200 — **Rooted**
- 210 — **Awakened**
- 225 — **Ascendant**
- 240 — **Ancient**
- 250 — **Evergreen**

Milestones accumulate access. Reaching a later tier never removes earlier content.

## Content gates

Concrete scripts should depend on named content gates rather than raw level checks. This gives us a single place to rebalance progression requirements later without editing every NPC, boss script, and PQ.

Initial gates:

- Rooted boss tier / Rooted forge
- Awakened boss tier / Awakened forge
- Ascendant hard-mode boss tier / Ascendant forge
- Ancient boss tier / Ancient forge
- Evergreen Mastery / Evergreen capstone quest

The gates are intentionally content-agnostic. Boss IDs, maps, item IDs, recipes, and quest IDs are bound through content adapters.

## Approved hybrid boss model

Everleaf uses recognizable v83 encounters as the initial endgame backbone while changing their server-side tuning and encounter rules. This minimizes early client/WZ dependencies while giving post-200 players genuinely different fights.

Initial ladder:

- **200 Rooted:** Rooted Zakum — introductory enhanced encounter; party pressure, add waves, and controlled burst windows.
- **210 Awakened:** Awakened Horntail — stronger coordination requirements, dispel pressure, phase escalation, and adds.
- **225 Ascendant:** Ascendant Pink Bean — first hard-tier encounter with statue sequencing, damage checks, adds, and hard enrage.
- **240 Ancient:** Ancient Pink Bean — accelerated/punishing remix that serves as the pre-cap mastery encounter.
- **250 Evergreen:** reserved for an Everleaf-original capstone encounter rather than another stat-inflated classic boss.

These definitions are policy contracts, not direct monster/map mutations. Concrete IDs and scripts stay behind adapters so encounter balance can evolve without contaminating progression policy.

## Encounter principles

- Enhanced bosses should not be simple HP multipliers.
- Mechanics must remain practical with the v83 client and server capabilities.
- Existing maps/assets are preferred for the first playable release.
- Party sizes target small coordinated groups rather than mandatory raid-scale populations.
- Earlier bosses remain relevant through identity-specific materials, weeklies, mastery, and collections.
- Failure states should be understandable: timers, enrages, phase rules, and recovery pressure rather than arbitrary one-shots.
- The level-250 capstone may introduce custom Everleaf assets only after the server-side endgame loop is proven.

## Reward philosophy

- Bosses have identity-specific drops and mastery goals.
- Verdant Marks provide a predictable horizontal progression lane, not a replacement for boss drops.
- Forge components can supplement progression but cannot directly purchase best-in-slot equipment.
- Major milestone unlocks remain level/progression based, never donation based.
- Cosmetic prestige becomes increasingly important at 240–250 so power creep does not become infinite.
- Donation rewards never grant encounter access, boss materials, forge power, or best-in-slot equipment.

## Next implementation pass

1. Bind enhanced encounter contracts to reusable server-side encounter adapters.
2. Add attempt/completion tracking and weekly boss reward eligibility.
3. Define boss-specific material contracts and forge dependencies.
4. Add GM/debug inspection hooks for encounter state.
5. Implement Rooted Zakum first as the reference encounter before cloning the architecture into higher tiers.
