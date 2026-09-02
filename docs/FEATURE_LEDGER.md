# EverLeaf verified feature ledger

This ledger records **implemented non-Empress behavior that must survive branch consolidation**. It is not a wishlist. Proposed features remain in `EVERLEAF_QOL_BACKLOG.md` until implemented and validated.

The automated subset is enforced by `tools/audit_consolidated_features.py` and `.github/workflows/audit-consolidated-features.yml`.

## Core server / progression

- [x] Level cap/progression supports level 250.
- [x] Website-only account-registration policy is retained in the release configuration.
- [x] Production configuration transforms and normal server release build remain active.
- [x] Free Market shortcut guards prevent unsafe transitions while trading, in player shops, hired merchants and restricted activity states.
- [x] NPC-shop sessions enforce current shop/session state, proximity and client locking.
- [x] Storage sessions are bound to the NPC/map that opened them and reject stale/forged use.
- [x] Inventory movement rejects invalid inventory tabs/quantities and uses client locking.
- [x] Equipment job requirements are enforced server-side rather than trusting the client.

## Classes

- [x] Adventurer class families retained.
- [x] Cygnus class families retained.
- [x] Aran retained.
- [x] Evan retained for the current supported scope.
- [x] Evan 43/43 server skill data/readiness gate retained.
- [x] Evan Dragon Fury and Magic Resistance release audits retained.
- [x] Evan automatic mastery/job advancement retained.
- [x] Maple Admin Evan creation route retained without replacing Heena's original quest behavior.
- [x] Native Evan selector and original Evan tutorial maps remain deferred rather than release blockers.

## Quests / world

- [x] Heena's original Maple Island tutorial behavior restored.
- [x] Quest 1031 / Heena and Sera protected by Maple Island quest audit.
- [x] Maple Island beginner quest integrity gate.
- [x] Global quest owner/prerequisite integrity gate.
- [x] Active quest item/mob/map reference gate.
- [x] Victoria Island regional quest gate.
- [x] Scripted quest-handler gate, including medal fallback semantics and expired-event classification.
- [x] Quest action/reward gate.
- [x] World map/NPC/portal/event-manager integrity gates.
- [x] Empress content excluded from active release gates.
- [x] Ola Ola randomized correct-portal flow restored during branch consolidation.

## Economy / rewards

- [x] Separate normal and boss drop-rate policy.
- [x] Ordinary global Chaos Scroll and White Scroll monster faucets removed.
- [x] Gachapon reward/source audit retained.
- [x] Vote Point exchange retained.
- [x] Verified vote reward audit retained.
- [x] PQ Point system and duplicate-clear protection retained.
- [x] Maple Leaf exchange retained.
- [x] Pet Vac timed-entitlement safety policy retained.
- [x] Rooted encounter/reward/forge content retained on the current release line.

## Transactions / abuse resistance

- [x] Hired Merchant concurrency protection retained.
- [x] Hired Merchant persistence, seller-credit, quantity and snapshot integrity audits retained.
- [x] PlayerShop transaction and snapshot integrity audits retained.
- [x] Duey ownership and settlement integrity audits retained.
- [x] Item stack/transfer restrictions retained.
- [x] Storage session authorization retained.
- [x] Trade/FM state guards represented in the current release behavior.

## Launcher / client distribution

- [x] EverLeaf launcher retained.
- [x] Signed/managed client update flow retained.
- [x] Bounded download copies exactly the manifest-signed byte count and rejects extra data.
- [x] One-time `.everleaf-launch` ticket retained with stale-ticket cleanup.
- [x] Launcher fail-closed behavior retained.
- [x] Evan XML donor builder retained on `client-dev` with WZ round-trip verification.
- [x] Managed WZ publication/client distribution infrastructure retained.

## Website / CMS / account

- [x] Public website/CMS retained on `master`.
- [x] Account dashboard retained.
- [x] Character roster/job presentation retained.
- [x] Rankings retained.
- [x] Download/help/community surfaces retained.
- [x] Password-change/account-security surface retained.
- [x] Discord account-linking surface retained.
- [x] GTop100 Vote for NX action retained.
- [x] Pending Vote NX / NX Credit account ledger retained.
- [x] GTop100 URL validation, constant-time pingback-secret validation and provider-success checking retained.
- [x] Verified NX queueing retained.
- [x] Wiki routes/catalog retained.
- [x] Wiki article source/verification/provenance presentation retained.
- [x] CMS/admin surface retained.

## Infrastructure / persistence

- [x] Full-game MySQL backup path retained.
- [x] `--single-transaction` dump retained.
- [x] Local privileged backup uses MySQL root/socket authentication rather than expanding website DB privileges.
- [x] Dumps remain schema-neutral so restore verification can target a temporary database safely.
- [x] Release build continues to compile, test and package with Java 21/Maven.

## Consolidation invariants

- [x] `master`, `release-dev`, and `client-dev` are canonical maintained lines for their respective surfaces.
- [x] `content-dev` is reconciliation-only and must not be wholesale-merged over newer policy.
- [x] `empress-dev` is excluded from the current release.
- [x] `Community-files` is excluded.
- [x] Active `wz/*` work is protected from branch cleanup until consumed.
- [x] Canonical feature audit currently passes 23/23 automated behavior checks.

## Proposed QoL that is **not** implied by this ledger

Items such as attack-while-moving, universal Flash Jump, infinite throwing stars, Sell All, Buyback, Boss Codex, overlay widgets and similar ideas remain proposals unless separately implemented and validated. Their presence in `EVERLEAF_QOL_BACKLOG.md` must never be interpreted as already shipped behavior.
