# EverLeaf Content and Runtime Validation

This document summarizes the maintained content baseline and separates **implemented/static evidence** from **runtime gameplay validation**. Exact status is authoritative in [`../EVERLEAF_MASTER_CHECKLIST.md`](../EVERLEAF_MASTER_CHECKLIST.md).

## Canonical content baseline

Production stages a validated full-v95 XML baseline rather than depending on the smaller repository WZ tree alone. The September 10, 2026 synchronized baseline contains 44,237 XML files.

The broad world audit has already covered thousands of non-Empress maps and validates map references, portals, return/forced-return behavior, NPC/mob/reactor references, quest structure, and major script/link integrity. Static completeness is not the same as a successful real-client playthrough.

## Future Henesys / Stronghold / Fallen Cygnus

The earlier "candidate" and "do not activate" Empress planning documents are historical. Current state:

- Future Henesys content is implemented.
- The 42-map `271000xxx` content range has been validated.
- Future Henesys real-client map loading has been verified.
- Stronghold content/data and its monster ranges are present.
- Required NPCs, scripts, portals, map names, minimaps, and related data are implemented.
- Fallen Cygnus encounter support is implemented.
- Normal knights: `8850000–8850004`.
- Elite variants: `8850005–8850009`.
- Shinsoo: `8850010`.
- Fallen Cygnus: `8850011`.
- Encounter lifecycle, reward, and weekly-ownership logic exists.
- Representative Future Henesys/Fallen Cygnus production invariants are validated against the canonical v95 WZ tree.

The remaining gap is **multiplayer runtime/balance verification**, not base content import.

## World runtime validation still matters

Even after structural audits pass, real-client validation should cover:

- major travel and Hidden Street chains;
- important NPC visual/semantic placement;
- advancement, storage, shop, quest, event, and boss-access NPCs;
- portal transition behavior;
- reactor animations and state transitions;
- instance cleanup after clear, timeout, disconnect, and re-entry;
- monster respawn timing/density and boss triggers;
- drop ownership, pet loot, expiry, and race conditions.

## Boss runtime matrix

High-priority live regressions remain:

- Zakum
- Horntail
- Papulatus
- Pink Bean
- Fallen Cygnus/Empress
- retained secondary bosses such as Pianus/Balrog where applicable

Each run should cover prerequisites, signup/leadership, entry, phase transitions, death, revive, disconnect/rejoin, timeout, return maps, lockouts/cooldowns, cleanup, and reward delivery/replay resistance.

## Party Quest runtime matrix

The maintained server has PQ framework/reward protections, but complete multi-client runs remain important for HPQ, KPQ, LPQ, Ludi Maze, Ellin, OPQ, Pirate, Romeo & Juliet/Magatia, APQ, CWKPQ, GPQ, and any other retained production PQ.

Validate leader loss, reconnect, timeout, party-size changes, failure exits, stage transitions, cleanup, full-inventory reward handling, duplicate clear attempts, and reward/economy balance.

## Quest runtime boundary

Static quest audits already cover owner/prerequisite references, item/mob/map requirements, actions/rewards, quantities, intervals, and scripted handlers. Runtime testing should focus on:

- advancement chains;
- boss prerequisite chains;
- abandon/restart reward abuse;
- repeatable/daily/weekly cooldowns;
- disconnect/relog reward replay;
- transfer restrictions on quest items.

Historical WZ/community/Empress audit reports are retained under `../archive/` for provenance, but must not be used as the current content status document.
