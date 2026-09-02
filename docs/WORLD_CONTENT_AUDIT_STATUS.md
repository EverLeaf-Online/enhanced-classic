# EverLeaf World / NPC / Quest / Monster Audit Status

Verified against the non-Empress `release-dev` content line on 2026-09-02.

This document records repository/static completion evidence separately from live-client gameplay verification. It intentionally does not modify or consume the protected updated-WZ/v95 modernization work.

## Maps / portals / reactors

### Repository/static coverage complete

- ✅ Global map structural scan across 5,238 in-scope maps.
- ✅ Spawned NPC, mob, and reactor IDs validated against matching data definitions.
- ✅ Static portal target-map validation.
- ✅ Named destination-portal validation with runtime portal-0 fallback awareness.
- ✅ Scripted portal filename/case/reference validation.
- ✅ `returnMap` and `forcedReturn` destination validation.
- ✅ Hidden/dormant portal findings separated from hard release failures.
- ✅ Exact duplicate spawn/link review.
- ✅ Reactor script coverage is now machine-classified instead of treating every scriptless reactor as broken.
- ✅ Proven missing handlers restored for baby-bird/Hidden Street drops, Zakum prequest boxes, Horntail maze drops, Romeo/Juliet PQ, Pink Bean transition, and Sharenian GPQ reward reactors.
- ✅ Event/map manager disposal infrastructure exists for instance cleanup.

### Still requires live gameplay verification

- 🟡 Walk/warp through important travel and Hidden Street chains in the packaged client.
- 🟡 Verify boss/PQ instance teardown after clear, timeout, disconnect, and re-entry.
- 🟡 Review remaining action-bearing scriptless reactors before enabling their legacy/seasonal content; do not create guessed stubs.

## NPCs

### Repository/static coverage complete

- ✅ Full spawned-NPC asset integrity audit.
- ✅ Spawn coordinate, foothold, roam-range, and exact-duplicate checks.
- ✅ Active NPC script coverage review.
- ✅ Quest owner NPC references cross-checked against active world spawns.
- ✅ Existing verified NPC spawn correction tooling retained.

### Still requires live gameplay verification

- 🟡 Visual/semantic placement of travel, advancement, shop/storage, and quest NPCs in the packaged client.
- 🟡 Confirm intentionally duplicated NPCs behave correctly when interacted with.

## Quests

### Repository/static coverage complete

- ✅ Global `Check` / `Act` / `Say` / `QuestInfo` structural integrity audit.
- ✅ Active quest owner NPC validation.
- ✅ Prerequisite quest validation.
- ✅ Item, mob/kill, and map requirement references.
- ✅ Quest action/reward validation for EXP, mesos, fame, items, pets, skills, quest-state transitions, scripts, and next-quest targets.
- ✅ Counter quantity/overflow checks.
- ✅ Repeat interval validity checks.
- ✅ Start-phase reward surfaces are explicitly reported for abandon/restart exploit review.
- ✅ Maple Island, Victoria Island, and classic mainland release audits are wired into the required build.

### Still requires live gameplay verification

- 🟡 Complete representative advancement/boss-prerequisite chains in-client.
- 🟡 Exercise repeatable cooldowns at runtime.
- 🟡 Abandon/restart quests that grant start items/rewards and confirm intended anti-duplication behavior.

## Monsters / spawns / drops

### Repository/static coverage complete

- ✅ Spawned mob IDs validated against Mob data.
- ✅ Spawn coordinates, footholds, roam ranges, and respawn timer shape reviewed.
- ✅ High-density maps surfaced for manual balance review rather than silently accepted.
- ✅ Boss/PQ event-manager linkage audit is part of the required build.
- ✅ Economy/NX/global-drop audits are part of the required build.

### Still requires live gameplay/balance verification

- 🟡 Confirm real respawn pacing and density on representative training maps.
- 🟡 Verify boss trigger behavior in live encounters.
- 🟡 Continue full drop-table balance/parity review as economy/content is tuned.

## CI gate

The required build now runs the world, NPC/portal, script-map-reference, regional quest, global quest, quest content/action/gameplay, economy/drop, and boss/PQ linkage audits before Maven compile/test/package. The 2026-09-02 hardening batches passed these gates before merging to `release-dev`.

## Scope boundary

- 🚫 Empress/Cygnus content remains excluded.
- 🚫 Updated-WZ/v95 modernization branches and artifacts remain protected and are not changed by this audit work.
