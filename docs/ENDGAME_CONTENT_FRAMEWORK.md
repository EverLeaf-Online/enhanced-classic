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

The gates are intentionally content-agnostic. Boss IDs, maps, item IDs, recipes, and quest IDs will be bound in later content adapters.

## Reward philosophy

- Bosses should have identity-specific drops and mastery goals.
- Verdant Marks provide a predictable horizontal progression lane, not a replacement for boss drops.
- Forge components can supplement progression but cannot directly purchase best-in-slot equipment.
- Major milestone unlocks remain level/progression based, never donation based.
- Cosmetic prestige becomes increasingly important at 240–250 so power creep does not become infinite.

## Next content pass

The next pass must select the actual boss ladder and decide whether Everleaf should primarily remix existing v83 bosses, create enhanced/hard variants of them, or add custom encounters. That choice affects client assets, scripts, balance workload, and launch timeline and should be approved before concrete encounter IDs and rewards are committed.
