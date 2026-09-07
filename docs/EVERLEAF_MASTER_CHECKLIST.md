# EverLeaf Master Development Checklist

Repository-backed working checklist for the current EverLeaf release line.

Last synchronized: **2026-09-07** after production deployment run #58, gameplay hardening through PR #373, production WZ staging fix PR #375, OCI backup/DR completion, v95/Future Henesys/Stronghold/Fallen Cygnus completion, and the latest client/runtime audit.

## Current production baseline

- Active server release branch: `release-dev`
- Current production/release-dev SHA: `ec8733f36bbe2b0f9a33ea71484e302bfedcf71e`
- Production deployment: **Deploy EverLeaf Game Production #58 — SUCCESS**
- Production deployment validates build, backup, release switch, server restart, channel runtime, canonical v95 WZ, public ports, and rollback on failure.
- `master` is still behind the active production release line and should not be treated as the canonical gameplay/server state until release consolidation is performed.
- Maintained client work remains on the dedicated client line/branches; do not blindly merge historical stacked client PRs.

## Status legend

- ✅ **Complete** — implemented and sufficiently evidenced.
- 🟢 **Live** — deployed and verified on production.
- 🟡 **Needs runtime verification** — implementation/static integrity exists but full gameplay/live validation remains.
- 🔧 **Needs work** — incomplete, partially implemented, or still requires hardening/integration.
- 🔴 **Not done** — significant work remains.
- ⏸ **Paused/deferred** — intentionally postponed.

---

# 1. Repository / Release Management

- ✅ Primary repository: `EverLeaf-Online/enhanced-classic`.
- ✅ `release-dev` is the active server release line.
- ✅ Production deploy workflow exists and is guarded.
- ✅ Automatic rollback path exists if new production health validation fails.
- ✅ Full Maven compile/test/package gating exists.
- ✅ Build manifest generation exists.
- ✅ Repository secret/artifact ignore hardening is present.
- ✅ Production WZ staging hardlink failure from deploy #57 was corrected in PR #375.
- 🟢 Production deploy #58 succeeded at `ec8733f36bbe2b0f9a33ea71484e302bfedcf71e`.
- 🟡 Reconcile historical useful branches only when still intentionally unconsumed.
- 🟡 Final `release-dev` → `master` consolidation after runtime validation.
- 🟡 Reconcile/close superseded historical client and website PRs instead of mass-merging them.

# 2. Core Server / Infrastructure

- ✅ Core server build/runtime baseline exists.
- ✅ MySQL persistence baseline exists.
- ✅ Oracle production deployment tooling exists.
- ✅ systemd-managed EverLeaf server runtime exists.
- ✅ Production release switching via `/opt/everleaf/current` exists.
- ✅ Rollback to prior release exists.
- ✅ Log rotation exists.
- ✅ Disk monitoring exists.
- ✅ Production-readiness auditing exists.
- 🟢 Latest release passed production restart/runtime validation.
- 🟡 Verify reconnect behavior under transient DB/network failures.
- 🟡 Run long-duration soak testing for memory leaks, deadlocks, scheduler drift, thread growth, sockets, file descriptors, and GC behavior.

# 3. Backup / Disaster Recovery

- ✅ OCI Object Storage bucket `everleaf-backups` configured.
- ✅ VM instance-principal authentication works.
- ✅ VM upload/read access works without VM-side object delete authority.
- ✅ Daily systemd backup timer enabled.
- ✅ MySQL all-database dump included.
- ✅ Critical server/web/nginx/systemd/config files included.
- ✅ Weekly broader archive includes production client/WZ recovery data.
- ✅ Backup uploads to OCI validated.
- ✅ Download-back verification completed.
- ✅ SHA256 verification passed.
- ✅ zstd archive verification passed.
- ✅ SQL contents verified, including `cosmic` database.
- ✅ Daily lifecycle retention: 45 days.
- ✅ Weekly lifecycle retention: 90 days.
- ✅ Previous object versions lifecycle retention: 14 days.
- ✅ Production deploy invokes backup before switching releases.
- ✅ Disk cleanup completed during DR setup and restored substantial free space.
- ✅ Backup/DR setup is **complete**.
- 🟡 Optional future upgrade: multi-region replication if regional disaster tolerance is desired.

# 4. Login / Accounts / Authentication

- ✅ Account/database framework exists.
- ✅ Launcher login integration framework exists.
- ✅ Login screen works in the accepted client flow.
- ✅ World selection works.
- ✅ Character selection works.
- ✅ Character selection → game entry works.
- 🟡 Verify registration end-to-end against production policy.
- 🟡 Verify password hashing and legacy-account compatibility.
- 🟡 Verify bans, temporary bans, IP/MAC restrictions, and duplicate-login/session protection.
- 🟡 Verify PIC/PIN behavior if enabled.
- 🟡 Verify account persistence across restart/reconnect conditions.
- 🟡 Continue mitigation/documentation for users launching the raw EXE instead of the EverLeaf Launcher.

# 5. Character Creation / Persistence

- ✅ Character persistence framework exists.
- ✅ Character-persistence diagnostics exist.
- ✅ Beginner creation works.
- ✅ Beginner → NPC → Evan conversion works.
- ⏸ Direct modern class-card/direct Evan creation remains intentionally paused.
- 🟡 Verify name validation/reserved names/duplicates.
- 🟡 Verify character deletion/restoration policy and remaining edge cases.
- 🟡 Verify inventories, mesos, skills, quests, keybinds, buddy/guild state, pets, mounts, storage, and cooldowns survive relog/restart.
- 🟡 Verify persistence under production-like DB latency/failure.

# 6. Classes / Jobs / Skills / Advancement

- ✅ Broad class/skill integrity auditing exists.
- ✅ Explorer family supported.
- ✅ Playable Cygnus Knights supported.
- ✅ Aran supported.
- ✅ Evan supported.
- ✅ Evan ten-stage job chain structurally audited.
- ✅ Evan Dragon Fury hardening.
- ✅ Evan Magic Resistance hardening.
- ✅ Evan Slow fallthrough fix.
- ✅ Evan Phantom Imprint fallthrough fix.
- ✅ Evan Soul Stone one-time revive behavior.
- ✅ Evan Killer Wings target lock handling.
- ✅ Evan Critical Magic validation.
- ✅ Evan Blessing/Soul Stone classification fixes.
- ✅ Aran High Defense fixed in PR #371.
- 🟢 Aran High Defense fix is included in current production.
- 🟡 Verify all intended advancement quests/NPC chains live.
- 🟡 Verify full skill/passive/buff/summon/transform/charge/stance/dispel/seal interactions live.
- 🟡 Verify full projectile/melee/magic/summon formula parity.

# 7. AP / SP Reset / Mastery Books

- ✅ AP Reset validates target before source mutation.
- ✅ AP Reset rollback helper exists.
- ✅ Failed AP Reset does not consume item.
- ✅ Same-stat AP Reset rejected.
- ✅ Projected HP/MP cap enforced.
- ✅ HP Reset cannot cross below EverLeaf survivability floor.
- ✅ SP Reset validates source and target skills.
- ✅ Null/invalid/empty source skill rejected.
- ✅ Same-skill SP Reset rejected.
- ✅ 4th-job target mastery cap enforced.
- ✅ Failed SP Reset does not consume item.
- ✅ Mastery books validate real skill/mastery values.
- ✅ Mastery book result packets use real skill/mastery identifiers.
- ✅ Invalid paths restore client actions.
- ✅ Regression coverage includes Explorer/Evan/Beginner/level-250 cases.
- 🟢 PR #369 hardening is live.

# 8. Progression / Level Cap / EXP

- ✅ Central level cap = 250.
- ✅ Level-up path enforces cap.
- ✅ Post-200 progression framework exists.
- ✅ 201–249 EXP curve implemented.
- ✅ Monotonic post-200 EXP tests exist.
- ✅ Level 250 terminal behavior exists.
- ✅ Weekly progression service exists.
- ✅ Account-level weekly budgets exist.
- ✅ Transactional row locking exists for claims.
- ✅ Verdant Marks ledger uses unique account/reason protection.
- ✅ Verdant Marks are account-bound DB currency, not transferable inventory.
- 🟡 Balance 201–249 pacing from real gameplay telemetry.
- 🟡 Verify post-200 milestone pacing and reward balance live.

# 9. HP Washing Replacement / Survivability

- ✅ `SurvivabilityPolicy` exists.
- ✅ `SurvivabilityService` exists.
- ✅ Applied on level-up and load/login.
- ✅ Explorer/Cygnus/Aran/Evan coverage exists.
- ✅ Idempotent and never reduces legitimate existing MaxHP.
- ✅ Legacy washed HP above the floor is grandfathered.
- ✅ AP Reset cannot bypass the minimum HP floor.
- 🟡 Tune final HP curves against real boss damage/balance.
- 🟡 Synchronize survivability documentation with the current implementation.

# 10. Combat / Damage / Status Effects

- ✅ Core combat framework exists.
- ✅ Passive damage-reduction helper exists.
- ✅ Aran High Defense now applies WZ thousandths correctly.
- ✅ Achilles uses the same safe reduction path.
- ✅ Core mob status support includes seal, darkness, weakness, stun, curse, poison, slow, dispel, seduce, banish, reverse/confuse, undead, immunities, reflects, accuracy/avoid/speed effects, summon effects, and related status mechanics.
- ✅ Holy Shield status interaction support exists.
- 🟡 Verify physical weapon damage parity.
- 🟡 Verify magic damage parity.
- 🟡 Verify critical, defense, accuracy, avoid, elemental, and level-penalty formulas.
- 🟡 Verify Power Guard/Magic Guard/Meso Guard edge cases.
- 🟡 Verify weapon/magic cancel, reflect, boss immunities, knockback, invulnerability, and phase transitions.
- 🟡 Verify summons/projectiles under runtime conditions.

# 11. Party EXP / Leech / Family Reputation

- ✅ Party EXP split framework exists.
- ✅ Leech interval/level-range logic exists.
- ✅ Party bonus EXP logic exists.
- ✅ Holy Symbol handling exists.
- ✅ Family Reputation award path exists.
- ✅ Duplicate Family Reputation party-kill award fixed in PR #372.
- 🟢 Duplicate family-reputation fix is live.
- 🟡 Validate intended EXP/leech balance with multi-client runtime tests.
- 🟡 Validate multi-party boss scenarios and unusual membership transitions.

# 12. Death / Revive / Charms

- ✅ Normal return-map death path exists.
- ✅ Event revive hook exists.
- ✅ Duplicate event unregister callback replay fixed in PR #372.
- ✅ `playerUnregistered` no longer repeats for null/non-member/repeated unregister calls.
- ✅ Wheel of Fortune can no longer bypass event/PQ/boss revive semantics.
- ✅ Event revive hook is consulted before same-map Wheel revival.
- ✅ Wheel is not consumed if event callback ejects/unregisters the player.
- ✅ Normal non-event Wheel behavior preserved.
- ✅ Regression coverage exists for permissive, unregistering, script-handled, missing-item, and no-Wheel cases.
- 🟢 PR #372/#373 death lifecycle fixes are live.
- 🟡 Verify EXP-loss/charm interactions.
- 🟡 Verify Resurrection-class skill interactions.
- 🟡 Perform full boss/PQ death/re-entry live matrix.

# 13. Maps / Portals / Reactors

- ✅ 5,238 non-Empress maps structurally audited in the broad world pass.
- ✅ Global map-reference audit completed.
- ✅ Broken/missing portal destinations audited.
- ✅ Named exits/script map references audited.
- ✅ Portal script filename case audited.
- ✅ Return/death-map and forced-return validation completed.
- ✅ Hidden Street references checked.
- ✅ NPC/mob/reactor asset references audited.
- ✅ Important missing reactor handlers restored, including Zakum prequest, Horntail maze, Romeo/Juliet, Pink Bean transition, GPQ/Sharenian, and Hidden Street/drop reactors.
- ✅ Event/map manager disposal framework exists.
- 🟡 Traverse major travel/Hidden Street chains in packaged client.
- 🟡 Verify reactor animation/state transitions live.
- 🟡 Verify cleanup after clear, timeout, disconnect, and re-entry.

# 14. Future Henesys / Stronghold / Fallen Cygnus / Empress

- ✅ Future Henesys content implemented.
- ✅ 42 maps under the `271000xxx` content range validated.
- ✅ Future Henesys real-client map load verified.
- ✅ Stronghold content/data implemented.
- ✅ Future Henesys/Stronghold mob ranges present.
- ✅ NPCs/scripts/portals implemented.
- ✅ map names/minimap/content data implemented.
- ✅ Fallen Cygnus encounter chain implemented.
- ✅ Five normal knights `8850000–8850004`.
- ✅ Five elite knights `8850005–8850009`.
- ✅ Shinsoo `8850010`.
- ✅ Fallen Cygnus `8850011`.
- ✅ Encounter lifecycle/reward/weekly ownership logic exists.
- 🟡 Full multiplayer live encounter/balance testing remains.

> The old checklist treated Empress/Stronghold as deferred. That status is obsolete. Current content is implemented; only runtime/balance validation remains.

# 15. NPCs / Spawn Placement

- ✅ Global NPC presence/asset audit completed.
- ✅ NPC spawn coordinates/footholds audited.
- ✅ NPC roam ranges audited.
- ✅ Duplicate NPCs structurally classified.
- ✅ Active NPC script coverage audited.
- ✅ Quest-owner NPC references audited.
- ✅ Release-facing NPC integrity gate exists in CI.
- 🟡 Visually verify important NPC placement in packaged client.
- 🟡 Live-test travel, advancement, storage, shop, quest, and event NPC interactions.

# 16. Quests

- ✅ Global quest structural integrity audit completed.
- ✅ Maple Island beginner quest audit completed.
- ✅ Victoria Island quest audit completed.
- ✅ Classic mainland quest audit completed.
- ✅ Active quest content-reference audit completed.
- ✅ Scripted quest-handler audit completed.
- ✅ Quest NPC/prerequisite references audited.
- ✅ Item collection and kill-counter structure audited.
- ✅ EXP/item/meso/fame/skill reward/action structure audited.
- ✅ Reward quantity/overflow safety audited.
- ✅ Repeatable interval validity audited.
- ✅ Quest gameplay-completeness audit is in release CI.
- 🟡 Live-test advancement quest chains.
- 🟡 Live-test boss prerequisite chains.
- 🟡 Live-test abandon/restart exploit paths.
- 🟡 Live-test repeatable/daily/weekly cooldown behavior.
- 🟡 Verify scripted quest items cannot bypass transfer restrictions.

# 17. Monsters / Spawns / Drops

- ✅ Spawn monster IDs audited against available monster data.
- ✅ Spawn coordinates/footholds audited.
- ✅ Roam ranges audited.
- ✅ Density review surfaced by world audit.
- ✅ Economy/global-drop audits exist.
- ✅ Ordinary global Chaos Scroll and White Scroll drops removed.
- 🟡 Verify actual respawn timing/density in live gameplay.
- 🟡 Verify elite/boss trigger behavior live.
- 🟡 Verify meso drop ranges/global rules.
- 🟡 Verify quest-item drop conditions.
- 🟡 Verify party ownership, pickup rights, pet loot, and expiry.
- 🟡 Verify drop-rate modifiers stack safely.
- 🟡 Complete final economy-facing drop/boss reward balance pass.

# 18. Bosses / Expeditions

- ✅ Dedicated boss/event framework exists.
- ✅ Zakum implementation exists.
- ✅ Horntail implementation exists.
- ✅ Papulatus implementation exists.
- ✅ Pink Bean implementation exists.
- ✅ Fallen Cygnus/Empress encounter exists.
- ✅ Rooted Zakum exists.
- ✅ Boss/PQ event-manager linkage audit exists.
- ✅ Reward replay protections improved.
- ✅ Event unregister replay protection added.
- ✅ Death/Wheel event bypass fixed.
- 🟡 Full Zakum live party lifecycle.
- 🟡 Full Horntail live run.
- 🟡 Full Papulatus live run.
- 🟡 Full Pink Bean live run.
- 🟡 Full Cygnus live run.
- 🟡 Expedition signup/leader transfer/disconnect/rejoin cleanup.
- 🟡 Entry/lockout/cooldown policy validation.
- 🟡 Boss drop/reward balance.

# 19. Party Quests

- ✅ PQ Points persistence/service exists.
- ✅ Account/reason uniqueness protection exists.
- ✅ Event clear is idempotent.
- ✅ Duplicate legacy Quest Point payout protection exists.
- ✅ Legacy event reward claims are protected per character/reward level/event instance.
- ✅ Inventory-full reward failure remains retryable.
- ✅ Already-paid reward retry completes without minting a second reward.
- 🟢 PR #370 PQ/event reward hardening is live.
- ✅ PQ Point values currently assigned for Henesys, Kerning, Ludibrium, Ludi Maze, Ellin, Orbis, Pirate, Magatia, Amoria, and CWKPQ.
- 🟡 Full live runs: HPQ, KPQ, LPQ, Ludi Maze, Ellin, OPQ, Pirate, Romeo/Juliet/Magatia, APQ, CWKPQ, GPQ.
- 🟡 Verify leader loss, reconnect, timeout, party-size, failure exit, and cleanup behavior.
- 🟡 Verify reward NPC/exchange economy balance.

# 20. Events / Minigames

- ✅ Event script inventory/classification audit implemented in PR #368.
- ✅ Missing `init()` detection.
- ✅ Event-manager case collision/missing manager checks.
- ✅ Seasonal scheduling safety checks.
- ✅ Dormant/legacy scripts remain report-only rather than silently enabled.
- ✅ RPS implementation/handler/opcode/NPC/WZ dependency audit exists.
- ✅ Event/minigame audit is part of release CI.
- 🟡 Runtime-test enabled events/minigames.
- 🟡 Verify event map reset behavior.
- 🟡 Verify reward replay/disconnect behavior.
- 🔧 Define future seasonal event support policy.

# 21. Items / Equipment / Scrolls

- ✅ Item/equipment integrity audit exists.
- ✅ Item transfer/stack integrity audit exists.
- ✅ Equipment requirement fixes exist.
- ✅ White Scroll behavior audited and structurally correct.
- ✅ Ordinary scroll is consumed normally.
- ✅ Selected White Scroll is consumed and protects only the upgrade slot on scroll failure.
- ✅ Curse/destruction behavior remains possible.
- ✅ Ordinary global White Scroll and Chaos Scroll drops removed.
- 🟡 Verify throwing star/bullet consumption and projectile edge cases.
- 🟡 Verify expiration.
- 🟡 Verify untradeable/account-bound/quest flags across all transfer systems.
- 🟡 Verify unique/equip restrictions.
- 🟡 Verify cloning/serialization cannot create malformed equips.
- 🟡 Define/finalize explicit rare-scroll acquisition sources and balance.

# 22. Inventory / Storage

- ✅ Inventory/stack transfer integrity framework exists.
- ✅ Storage withdrawal preflights inventory space before fee.
- ✅ Storage takeout failure rolls item back.
- ✅ Inventory insertion failure restores original item to storage.
- ✅ Fees are applied only after successful settlement.
- ✅ Storage deposit checks the locked `storage.store(item)` result.
- ✅ Failed store restores original-form item to inventory.
- ✅ Critical rollback failure logging exists.
- 🟢 PR #370 storage settlement hardening is live.
- 🟡 Storage + disconnect race test.
- 🟡 Concurrent account-storage test.
- 🟡 Restricted/custom item bypass test.
- 🟡 Storage meso edge cases.

# 23. Trade / Free Market / Merchants / PlayerShop / Duey

- ✅ Direct Trade has lock/confirmation/replay protections.
- ✅ Symmetric partner validation exists.
- ✅ Trade cancel restores items/mesos.
- ✅ Meso-cap/space checks exist.
- ✅ Hired Merchant buy-slot guard exists.
- ✅ Overflow-safe merchant quantity/price handling exists.
- ✅ Merchant seller-credit concurrency hardening exists.
- ✅ Merchant persistence transaction hardening exists.
- ✅ Merchant snapshot consistency exists.
- ✅ Fredrick recovery hardening exists.
- ✅ PlayerShop transaction integrity exists.
- ✅ PlayerShop snapshot consistency exists.
- ✅ Duey package ownership hardening exists.
- ✅ Duey settlement hardening exists.
- ✅ Trade button → Free Market routing exists with safety restrictions.
- 🟡 Direct trade live E2E.
- 🟡 Cancel/disconnect/channel-change races.
- 🟡 Simultaneous merchant/PlayerShop purchase races.
- 🟡 Merchant restart/recovery live test.
- 🟡 Fredrick recovery live test.
- 🟡 Restricted/custom currency transfer fuzzing.

# 24. Shops / Exchanges / Crafting / Rooted Forge

- ✅ Rooted Forge framework exists.
- 🟡 Audit standard shop inventory mappings.
- 🟡 Verify buy/sell quantity, meso, inventory-space checks, and rollback live.
- 🟡 Verify exchange/token shops.
- 🟡 Audit Maker/crafting if retained.
- 🟡 Verify Rooted Forge fulfillment, persistence, stat application, retry/failure, and exploit resistance live.
- 🟡 Verify custom-material acquisition/consumption.

# 25. Economy / Mesos / Custom Currencies / Random Rewards

- ✅ Verdant Marks framework exists.
- ✅ PQ Points framework exists.
- ✅ NX reward framework exists.
- ✅ Reward-source/economy audits exist.
- ✅ Maple Leaf exchange audit exists.
- ✅ Gachapon/reward-source audit exists.
- ✅ Vote Point audit exists.
- ✅ Ordinary global Chaos/White drops removed.
- 🟡 Complete final economy source/sink model.
- 🟡 Verify meso cap/overflow.
- 🟡 Verify high-level hourly meso generation.
- 🟡 Balance boss reward/high-value item generation.
- 🟡 Balance Gachapon pools.
- 🟡 Finalize rare-scroll sources.
- 🟡 Inflation/load simulation.
- 🟡 Define anti-RMT monitoring/policies.
- 🔧 Decide whether fishing remains supported, reworked, or disabled.

# 26. Pets / Mounts

- ✅ Pet Vac safety audit exists.
- 🟡 Verify pet summon/equip/hunger/closeness/commands/expiry/revive.
- 🟡 Verify pet item/meso pickup rules and ownership restrictions.
- 🟡 Verify multi-pet if enabled.
- 🟡 Verify mounts, saddles, fatigue, skills, and unlock quests.
- 🟡 Verify mount/pet state across channel change/relog.
- 🔧 Define final universal/earnable Pet Vac design and balance.

# 27. Cash Shop / NX

- ✅ Cash Shop framework exists.
- ✅ NX reward framework exists.
- ✅ NX/global-drop/reward audits exist.
- 🟡 Verify Cash Shop entry/exit and character state.
- 🟡 Verify NX balances/scopes.
- 🟡 Verify purchase history/gifting/wishlist/storage if retained.
- 🟡 Verify retry/replay behavior.
- 🟡 Verify paid rate coupons stay disabled as intended.
- 🟡 Verify cosmetic transfer policy.
- 🟡 Final no-P2W review.

# 28. Party / Guild / Alliance / Buddy / Fame

- ✅ Party framework exists.
- ✅ Guild framework exists.
- ✅ Alliance/buddy/fame frameworks exist.
- 🟡 Verify party lifecycle/leader migration.
- 🟡 Verify party HP/status/map updates across channels.
- 🟡 Verify guild create/emblem/ranks/invite/kick/leave/contribution/disband.
- 🟡 Verify alliances if enabled.
- 🟡 Verify buddy lifecycle/capacity/offline state.
- 🟡 Verify fame limits/anti-abuse.
- 🟡 Verify cross-channel social updates.

# 29. Channels / World Capacity

- ✅ Production target/configuration is 20 channels (CH1–CH20).
- ✅ Production deployment validates public game ports.
- 🟢 Latest production release passed deployment runtime/public-port validation.
- 🟡 Manual player channel-change sweep CH1→CH20.
- 🟡 Verify capacity/failure messaging.
- 🟡 Load-test multi-channel concurrency.

# 30. Client / Client v2

- ✅ Current accepted flow reaches login/world/character/game.
- ✅ 1280×720 gameplay/client configuration restored.
- ✅ Broken coordinate-only login experiment disabled.
- ✅ `CWvsApp::Run` compatibility behavior restored.
- ✅ No Whack client combat fix.
- ✅ Attack-while-moving work exists.
- ✅ No Breath exists.
- ✅ Bootstrap/hook hardening foundation exists.
- 🟡 Borderless/fullscreen runtime sweep.
- 🟡 Alt+Enter runtime testing.
- 🟡 Multi-monitor/minimize/restore/alt-tab testing.
- 🟡 Clean disconnect/crash behavior.
- 🟡 Clean-machine source-built client test.
- 🟡 Optional WASD remains draft/opt-in, not current release-critical.
- 🔧 Reconcile stacked historical Client v2 PRs rather than merging them blindly.

# 31. Discord Rich Presence

- ✅ EverLeaf-native Rich Presence implementation exists on the dedicated client branch.
- ✅ No bot token/OAuth secret embedded.
- ✅ No Discord Game SDK DLL dependency required.
- 🟡 PR #366 remains draft/open.
- 🟡 Windows/runtime validation still required before merge/promotion.
- 🟡 Character/map/job activity hooks still require verified v83 memory contracts.
- 🟡 Final live Discord presence display validation pending.

# 32. Launcher / Patcher / Auto-Updater

- ✅ EverLeaf launcher project exists.
- ✅ Patch service exists.
- ✅ Patch manifest tooling exists.
- ✅ Production patch hosting exists.
- ✅ Managed-client baseline exists.
- ✅ Launcher/update infrastructure exists.
- 🟡 Verify launcher self-update.
- 🟡 Verify damaged-file repair/hash validation.
- 🟡 Verify interrupted update atomicity/rollback/retry.
- 🟡 Verify Play launches the correct executable/config.
- 🟡 Add clear handling for raw EXE launches.
- 🟡 Verify signing/provenance strategy.
- 🟡 Clean-machine install/update/repair test.

# 33. Website / CMS

- ✅ Production website/CMS exists.
- ✅ Home, downloads, news, account, rankings, Wiki, help/support, auth routes exist.
- ✅ Major public UI/UX redesign exists.
- ✅ Rankings redesign exists.
- ✅ Wiki redesign exists.
- ✅ Dark public theme restoration merged.
- ✅ Production web readiness hardening exists.
- 🟡 Final page-by-page visual polish.
- 🟡 Verify registration/login against production game DB.
- 🟡 Verify rankings stale/deleted/renamed character behavior.
- 🟡 Verify live server/channel status integration.
- 🟡 Verify production download/launcher manifest links.
- 🟡 Verify admin auth/session/CSRF/rate-limit/security controls.
- 🔧 Reconcile/close superseded historical website PRs.

# 34. Database / Migrations / Admin

- ✅ Base DB/drop/shop/admin SQL exists.
- ✅ Migration framework exists.
- ✅ Weekly progression migration exists.
- ✅ Verdant Marks migration exists.
- ✅ PQ Points migration exists.
- ✅ Rooted migration work exists.
- ✅ Production database backups are automated and verified.
- 🟡 Test migrations from clean baseline.
- 🟡 Test sequential upgrade from current production schema.
- 🟡 Verify migration idempotency/safe-failure behavior.
- 🟡 Verify constraints/indexes/uniqueness for reward/currency systems.
- 🟡 Verify least privilege and no public MySQL exposure.
- 🟡 Define orphaned/deleted-account character cleanup policy.
- 🟡 Document/administer safe DBeaver workflows.

# 35. Security / Exploit Resistance

- ✅ Repository secret/artifact hardening.
- ✅ Reward claim idempotency hardening.
- ✅ Event clear idempotency hardening.
- ✅ Event unregister replay protection.
- ✅ Wheel/event revive bypass fixed.
- ✅ Storage settlement rollback hardening.
- ✅ Item transfer/stack hardening.
- ✅ Duey hardening.
- ✅ Merchant hardening.
- ✅ PlayerShop hardening.
- ✅ Weekly/account-currency transactional protections.
- 🔧 Complete broad packet-validation audit.
- 🔧 Malformed packet fuzzing.
- 🔧 Broad dupe/race-condition matrix.
- 🟡 Verify quantities server-side across item/meso/NX/custom currencies.
- 🟡 Verify NPC/quest/shop/map proximity/state validation where required.
- 🟡 Verify unauthorized GM/admin command rejection.
- 🟡 Verify web rate limiting/session/cookie security.
- 🟡 Verify logs do not expose secrets/sensitive account data.

# 36. Concurrency / Transaction Safety

- ✅ Merchant persistence/seller-credit/purchase/snapshot audits exist.
- ✅ PlayerShop transaction/snapshot audits exist.
- ✅ Duey ownership/settlement audits exist.
- ✅ PQ/event reward idempotency exists.
- ✅ Weekly progression uses transactional claim protection.
- 🟡 Concurrent Verdant Marks earn/spend.
- 🟡 Concurrent PQ Points award/spend.
- 🟡 Trade + disconnect race.
- 🟡 Storage + disconnect race.
- 🟡 Merchant + restart/disconnect race.
- 🟡 Cash Shop retry/replay.
- 🟡 Boss reward retry/disconnect.
- 🟡 DB rollback tests for failed multi-step rewards.

# 37. SoloMapling / Automated Gameplay Agents

- ✅ SoloMapling donor baseline integrated/pinned for current work.
- ✅ Headless/real server-side bot-client foundation exists.
- ✅ Training/QA bot work exists.
- ✅ Some party/PQ driver infrastructure exists.
- 🟡 Batch 4: death/recovery/autonomous cross-map travel.
- 🟡 Batch 5: party/trade/storage.
- 🟡 Batch 6: bosses/PQ/quests.
- 🟡 Batch 7: autonomous multi-bot soak/E2E.
- 🔴 Fully unattended live-client login→progression E2E remains a major gap.

# 38. Automated QA

- ✅ QA agent infrastructure exists.
- ✅ Static/deep QA tooling exists.
- ✅ Runtime QA tooling exists.
- ✅ Game-agent tooling exists.
- ✅ Maven build/test/package CI integrated.
- ✅ World/NPC/portal/reactor/quest audits integrated.
- ✅ Economy/item/merchant audits integrated.
- ✅ Recent gameplay PRs cleared CI before merge.
- 🟡 Run automated gameplay QA against the actual packaged client/release.
- 🟡 Add regression tests for every fixed exploit/critical bug.
- 🟡 Maintain machine-readable known-issues list.

# 39. Performance / Stability / Soak

- 🔴 Realistic concurrent player load test.
- 🔴 Multi-hour/day soak test.
- 🔴 Concurrent boss/PQ instance load.
- 🔴 Simultaneous login/channel-change test.
- 🔴 Database hotspot profiling.
- 🔴 Map/mob scheduler profiling.
- 🔴 GC/heap/thread/socket/file-descriptor telemetry under load.
- 🔴 Reconnect/network-failure simulation.

# 40. Logging / Monitoring / Operations

- ✅ Log rotation exists.
- ✅ Disk monitoring exists.
- ✅ Character-persistence diagnostics exist.
- ✅ Production-readiness audit exists.
- ✅ Production health/runtime validation exists.
- ✅ Public game-port validation exists.
- ✅ Production rollback exists.
- ✅ Production pre-deploy backup exists.
- 🟡 Add/verify proactive production alerts.
- 🟡 Structured gameplay/reward/trade/storage anomaly logging.
- 🟡 Client crash/diagnostic collection strategy.
- 🟡 Formal restart/recovery operations runbook.

# 41. Incident / Security Investigation

- ✅ Relevant nginx evidence preserved for the active account/incident investigation.
- ✅ `trustProxy` production configuration identified.
- 🟡 Complete correlated timeline across Oracle/server, Git/GitHub, ChatGPT/Codex/Work, and personal-PC evidence where relevant.
- 🟡 Produce final incident conclusion/remediation report.
- 🟡 Keep incident investigation separate from ordinary gameplay development.

# 42. Player Documentation

- 🔴 Definitive installation/launcher guide.
- 🔴 Clear launcher-only/raw-EXE guidance.
- 🟡 Account creation/recovery/support documentation.
- 🟡 Rates/level-250/post-200 progression documentation.
- 🟡 Verdant Marks documentation.
- 🟡 PQ Points documentation.
- 🟡 No-HP-washing progression explanation.
- 🟡 Boss/PQ/custom-content documentation.
- 🟡 Known-issues/reporting documentation.
- 🟡 Antivirus false-positive guidance without recommending global antivirus disablement.

# 43. Staff / GM Documentation

- 🔴 GM command/permission reference.
- 🔴 Player-support procedures.
- 🔴 Rollback/economy incident procedures.
- 🔴 Ban/appeal/evidence procedures.
- 🔴 Event-operation procedures.
- 🔴 Deploy/restart/backup/restore runbook.
- 🔴 Exploit-response/emergency shutdown procedure.

# 44. Open / Historical Git Work Requiring Reconciliation

Do not mass-merge these branches/PRs. Reconcile them individually against current production/client state.

- 🟡 PR #366 — EverLeaf native Discord Rich Presence — draft/open.
- 🟡 PR #361 — copycat WZ reference metadata — draft/open.
- 🟡 PR #360 — copycat client audit tooling — draft/open.
- 🟡 PR #359 — optional WASD Client v2 work — draft/open.
- 🟡 PR #358 — loader/import cleanup stack — draft/open.
- 🟡 Older stacked Client v2 display/input/bootstrap PRs may be superseded by later merged/live work.
- 🟡 Older website PRs may be superseded by current production styling.

# 45. Closed Alpha Readiness

## Ready / strong enough

- ✅ Reproducible production server deployment.
- ✅ Automatic rollback.
- ✅ Off-VM backup/DR.
- ✅ Restore verification.
- ✅ Login/world/character/game flow.
- ✅ v95 server/client content baseline.
- ✅ Future Henesys/Stronghold/Fallen Cygnus implementation.
- ✅ Broad world-content structural integrity.
- ✅ Core custom progression.
- ✅ Strong server CI/audit coverage.
- ✅ Substantial anti-dupe/reward/storage/merchant hardening.

## Remaining closed-alpha validation

- 🟡 Clean-machine launcher/client install.
- 🟡 Multi-character persistence/restart test.
- 🟡 Advancement playthrough.
- 🟡 Major quest chains.
- 🟡 Boss/PQ real-client testing.
- 🟡 Direct trade/merchant/storage race testing.
- 🟡 Soak/load testing.
- 🟡 Known-issues list.

**Assessment:** EverLeaf is closed-alpha capable, but not yet public-beta hardened.

# 46. Public Beta Readiness

Main remaining blockers:

1. 🔴 Automated live-client/E2E coverage.
2. 🔴 Soak/load/concurrency testing.
3. 🟡 Boss/PQ live regression matrix.
4. 🟡 Combat formula/runtime parity.
5. 🟡 Trade/storage/merchant race testing.
6. 🟡 Advancement/boss-prerequisite quest playthroughs.
7. 🟡 Clean-machine launcher install/update/repair.
8. 🟡 Website/account/rankings/channel integration verification.
9. 🟡 Packet/admin/web security pass.
10. 🟡 Economy/boss-drop/source-sink balance.
11. 🟡 Rich Presence if required for beta.
12. 🟡 Player/staff documentation/support procedures.

# 47. Public Launch Readiness

- 🟡 Critical/high-severity issues closed or consciously accepted.
- 🟡 `release-dev` consolidated/promoted to `master` after runtime validation.
- 🟡 Server/client/launcher artifacts reproducible from source/workflows.
- 🟡 Client/server assets verified from clean install.
- 🟡 Live channel count/config verified with actual client channel switching.
- 🟡 Website/CMS/auth/rankings/status verified.
- 🟡 Economy/security/performance/load validation complete.
- ✅ Backup/restore/rollback foundation validated.
- 🟡 Player/staff documentation published.
- 🟡 Final launch approval after beta telemetry/balance/security review.

# 48. Post-Launch Operations

- 🔧 Define patch cadence/emergency hotfix process.
- 🔧 Define launcher manifest/version policy.
- 🔧 Define DB migration/release process.
- 🔧 Monitor inflation/high-value item generation.
- 🔧 Monitor crashes/disconnect/channel health.
- 🔧 Monitor suspicious trade/storage/merchant/reward behavior.
- 🔧 Maintain public changelog/known issues.
- 🔧 Schedule recurring restore verification/security/performance/content audits.

---

# Recently Closed Gameplay / Production Work

- ✅ PR #369 — AP/SP resets and mastery books hardened.
- ✅ PR #370 — PQ clear idempotency, event reward idempotency, storage settlement hardening.
- ✅ PR #371 — Aran High Defense damage reduction fixed.
- ✅ PR #372 — duplicate party Family Reputation fixed; event unregister replay fixed.
- ✅ PR #373 — event death/Wheel revive bypass fixed.
- ✅ PR #374 — production deployment trigger for latest gameplay hardening.
- ✅ PR #375 — production WZ staging hardlink fallback fix.
- 🟢 Production deployment #58 succeeded at `ec8733f36bbe2b0f9a33ea71484e302bfedcf71e`.

# Immediate Priority Queue

1. **Automated gameplay / SoloMapling E2E** — login, spawn, combat, death, party, storage, trade, PQ, boss, reconnect.
2. **Boss + PQ runtime verification** — structural work is strong; runtime evidence is now the gap.
3. **Combat parity** — finish damage/status/passive formula edge cases.
4. **Trade/storage/merchant concurrency** — deliberately race the now-hardened transaction paths.
5. **Progression/economy balance** — EXP 201–250, rare scrolls, boss drops, Verdant Marks, PQ Points, meso sources/sinks.
6. **Client/runtime cleanup** — Rich Presence, remaining Client v2 reconciliation, clean install, crash/windowing tests.
7. **Website/account/launcher integration validation**.
8. **Security packet/admin/web pass**.
9. **Performance/soak/load testing**.
10. **Release consolidation** — reconcile stale PRs and promote approved `release-dev` toward `master` only after runtime confidence is sufficient.

# Current Completion Assessment

EverLeaf has moved beyond the repository-consolidation and broad static-content stage. Core v95 backport work, Future Henesys/Stronghold/Fallen Cygnus, backup/DR, level 250 progression, survivability replacement, AP/SP/mastery hardening, Aran High Defense, PQ/event reward idempotency, storage settlement, Family Reputation duplication, event unregister replay, and Wheel/event death bypass are implemented. The current combined server state is deployed successfully to production.

The largest remaining uncertainty is now **runtime behavior under real multi-client gameplay and load**: boss/PQ lifecycle, combat parity, persistence/concurrency, anti-dupe race testing, clean-machine client/launcher behavior, and performance/operations validation.
