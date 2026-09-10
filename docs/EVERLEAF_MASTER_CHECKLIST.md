# EverLeaf Master Development Checklist

Repository-backed working checklist for the current EverLeaf release line.

Last synchronized: **2026-09-10** after master consolidation, workflow-definition cleanup, native Discord Rich Presence extraction/validation, live client publication, website Git migration, final branch cleanup, the final guarded production rebuild/restart, documentation audit/consolidation, and completion of the maintained player/staff documentation baseline.

## Current production baseline

- Primary repository: `EverLeaf-Online/enhanced-classic`
- Canonical branch: `master`
- Repository branch state: **`master` is the sole canonical line; temporary documentation refs may remain but contain no unique work**
- Open pull requests: **none**
- Current running game release source SHA: `92a646d6c42a4f5e100f8a0b2ccc6f1bfcabd45a`
- Current running game release: `/opt/everleaf/releases/92a646d6c42a4f5e100f8a0b2ccc6f1bfcabd45a-34484572759-2`
- Production source checkout: `/opt/everleaf/server`
- Active release symlink: `/opt/everleaf/current`
- Game service: `everleaf.service`
- Website checkout: `/opt/everleaf/web-repo`
- Website runtime symlink: `/opt/everleaf/web -> /opt/everleaf/web-repo/web`
- Website mutable state: `/opt/everleaf/web-state`
- Website service: `everleaf-web.service`
- Oracle origin / deployment host: `132.145.141.79`
- Player-facing game relay: `129.159.114.146`
- Public site: `https://everleafms.online`
- Login port: `8484`
- Channels: `7575-7594` (20 channels)
- Canonical production v95 XML baseline: **44,237 XML files** verified during final deployment.
- Final deployment rebuilt the server JAR, staged the canonical v95 WZ tree, backed up production, switched `/opt/everleaf/current`, restarted `everleaf.service`, verified login + all 20 local channels, verified all relay ports, and recorded the deployed release.
- Live managed client was rebuilt, validated, published, and includes the current native Discord Rich Presence integration.

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
- ✅ `master` is the sole canonical production/development line.
- ✅ Historical `release-dev` retired.
- ✅ Obsolete stacked development branches retired.
- ✅ Useful branch-only audit/tooling work preserved before cleanup.
- ✅ PR #366 closed as superseded after its unique Discord work was extracted onto current master.
- ✅ Old native-client donor branch removed.
- ✅ Temporary maintenance/finalization branches removed.
- ✅ Documentation consolidation PR #385 merged; temporary documentation refs contain no unique work and are housekeeping-only.
- ✅ No open PRs remain after cleanup.
- ✅ Direct Codex Connector writes to protected `master` are now available through the configured ruleset bypass.
- ✅ Production deploy workflow exists and is guarded.
- ✅ Automatic rollback path exists if new production health validation fails.
- ✅ Full Maven compile/test/package gating exists.
- ✅ Build manifest generation exists.
- ✅ Repository secret/artifact ignore hardening is present.
- ✅ Production WZ staging hardlink failure has a safe copy/reflink fallback.
- 🟢 Final guarded production deployment succeeded from `92a646d6c42a4f5e100f8a0b2ccc6f1bfcabd45a`.

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
- ✅ Production source checkout synchronizes to canonical `master`.
- 🟢 Final release passed production restart/runtime validation.
- 🟢 Login server is healthy on `8484`.
- 🟢 All 20 channel listeners are healthy on `7575-7594`.
- 🟢 All player-facing relay ports were externally verified after final restart.
- 🟡 Verify reconnect behavior under transient DB/network failures.
- 🟡 Run long-duration soak testing for memory leaks, deadlocks, scheduler drift, thread growth, sockets, file descriptors, and GC behavior.
- 🟡 Perform another deliberate full VM reboot/DR exercise later.

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
- ✅ Final September 10 deployment backup stage completed successfully before release switch.
- ✅ Disk cleanup completed during DR setup and restored substantial free space.
- ✅ Backup/DR setup is complete.
- ✅ Command-level recovery/rollback/restore rehearsal runbook documented in `docs/staff/RECOVERY_AND_RESTORE.md`.
- 🟡 Periodically perform an isolated full restore rehearsal.
- 🟡 Optional future upgrade: multi-region replication if regional disaster tolerance is desired.

# 4. Login / Accounts / Authentication

- ✅ Account/database framework exists.
- ✅ Launcher login integration framework exists.
- ✅ Login screen works in the accepted client flow.
- ✅ World selection works.
- ✅ Character selection works.
- ✅ Character selection → game entry works.
- ✅ Production web secrets are externalized.
- ✅ Production password mode uses bcrypt.
- ✅ Launcher-ticket enforcement is part of the current bootstrap contract.
- ✅ Current staff-reviewed account recovery flow is documented for players/support.
- 🟡 Verify registration end-to-end against production policy.
- 🟡 Verify password hashing and legacy-account compatibility across older accounts.
- 🟡 Verify bans, temporary bans, IP/MAC restrictions, and duplicate-login/session protection.
- 🟡 Verify PIC/PIN behavior if enabled.
- 🟡 Verify account persistence across restart/reconnect conditions.
- 🟡 Continue mitigation for users launching the raw EXE instead of the EverLeaf Launcher; supported launcher-first behavior is now documented.
- 🟡 Complete source-first authentication/security review with targeted runtime confirmation.

# 5. Character Creation / Persistence

- ✅ Character persistence framework exists.
- ✅ Character-persistence diagnostics exist.
- ✅ Beginner creation works.
- ✅ Beginner → NPC → Evan conversion works.
- ✅ Controlled graceful shutdown preserved character persistence during production testing.
- ⏸ Direct modern class-card/direct Evan creation remains intentionally paused.
- 🟡 Verify name validation/reserved names/duplicates.
- 🟡 Verify character deletion/restoration policy and remaining edge cases.
- 🟡 Resolve account deletion semantics where character rows can remain after an account is intentionally purged.
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
- ✅ Aran High Defense fixed and runtime-tested.
- ✅ Achilles damage-reduction behavior runtime-tested.
- 🟡 Run a systematic runtime matrix across Explorer, Cygnus, Aran, and Evan skills instead of ad-hoc spot tests.
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
- 🟢 AP/SP/mastery hardening is included in current production.

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
- ✅ Maintained player-facing progression/Verdant/PQ Points documentation exists.
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
- ✅ Survivability/no-HP-washing documentation is synchronized into maintained gameplay and player guides.
- 🟡 Tune final HP curves against real boss damage/balance.

# 10. Combat / Damage / Status Effects

- ✅ Core combat framework exists.
- ✅ Passive damage-reduction helper exists.
- ✅ Aran High Defense applies WZ thousandths correctly.
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
- ✅ Duplicate Family Reputation party-kill award fixed.
- 🟢 Duplicate family-reputation fix is live.
- 🟡 Validate intended EXP/leech balance with multi-client runtime tests.
- 🟡 Validate multi-party boss scenarios and unusual membership transitions.

# 12. Death / Revive / Charms

- ✅ Normal return-map death path exists.
- ✅ Event revive hook exists.
- ✅ Duplicate event unregister callback replay fixed.
- ✅ `playerUnregistered` no longer repeats for null/non-member/repeated unregister calls.
- ✅ Wheel of Fortune can no longer bypass event/PQ/boss revive semantics.
- ✅ Event revive hook is consulted before same-map Wheel revival.
- ✅ Wheel is not consumed if event callback ejects/unregisters the player.
- ✅ Normal non-event Wheel behavior preserved.
- ✅ Regression coverage exists for permissive, unregistering, script-handled, missing-item, and no-Wheel cases.
- 🟢 Death/event lifecycle fixes are live.
- 🟡 Verify EXP-loss/charm interactions.
- 🟡 Verify Resurrection-class skill interactions.
- 🟡 Perform full boss/PQ death/re-entry live matrix.

# 13. Maps / Portals / Reactors

- ✅ 5,238 non-Empress maps structurally audited in the broad world pass.
- ✅ Global map-reference audit completed.
- ✅ Broken/missing portal destinations audited.
- ✅ Named exits/script map references audited.
- ✅ Portal script filename case audited.
- ✅ `Depart_topFloor.js` filename/case cleanup is preserved.
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
- ✅ Map names/minimap/content data implemented.
- ✅ Fallen Cygnus encounter chain implemented.
- ✅ Five normal knights `8850000–8850004`.
- ✅ Five elite knights `8850005–8850009`.
- ✅ Shinsoo `8850010`.
- ✅ Fallen Cygnus `8850011`.
- ✅ Encounter lifecycle/reward/weekly ownership logic exists.
- ✅ Final production deployment validates representative Future Henesys/Fallen Cygnus map/mob/NPC/quest invariants against the canonical v95 WZ tree.
- 🟡 Full multiplayer live encounter/balance testing remains.

> The old checklist treated Empress/Stronghold as deferred. That status is obsolete. Current content is implemented; only runtime/balance validation remains.

# 15. NPCs / Spawn Placement

- ✅ Global NPC presence/asset audit completed.
- ✅ NPC spawn coordinates/footholds audited.
- ✅ NPC roam ranges audited.
- ✅ Duplicate NPCs structurally classified.
- ✅ Active NPC script coverage audited.
- ✅ Quest-owner NPC references audited.
- ✅ Release-facing NPC integrity gate exists.
- 🟡 Visually verify important NPC placement in packaged client.
- 🟡 Live-test travel, advancement, storage, shop, quest, event, boss-access, and custom EverLeaf NPC interactions.

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
- ✅ Quest gameplay-completeness audit tooling exists.
- 🟡 Live-test advancement quest chains.
- 🟡 Live-test boss prerequisite chains.
- 🟡 Live-test abandon/restart exploit paths.
- 🟡 Live-test repeatable/daily/weekly cooldown behavior.
- 🟡 Test reward disconnect/relog replay behavior.
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
- 🟡 Deliberately test drop/pickup race conditions.
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
- 🟡 Pianus/Balrog and other retained boss lifecycle checks.
- 🟡 Expedition signup/leader transfer/disconnect/rejoin cleanup.
- 🟡 Entry/lockout/cooldown policy validation.
- 🟡 Boss prerequisite quest validation.
- 🟡 Boss death/respawn/return-map/re-entry validation.
- 🟡 Boss drop/reward balance.

# 19. Party Quests

- ✅ PQ Points persistence/service exists.
- ✅ Account/reason uniqueness protection exists.
- ✅ Event clear is idempotent.
- ✅ Duplicate legacy Quest Point payout protection exists.
- ✅ Legacy event reward claims are protected per character/reward level/event instance.
- ✅ Inventory-full reward failure remains retryable.
- ✅ Already-paid reward retry completes without minting a second reward.
- ✅ PQ/event reward hardening is live.
- ✅ PQ Point values currently assigned for Henesys, Kerning, Ludibrium, Ludi Maze, Ellin, Orbis, Pirate, Magatia, Amoria, and CWKPQ.
- 🟡 Full live runs: HPQ, KPQ, LPQ, Ludi Maze, Ellin, OPQ, Pirate, Romeo/Juliet/Magatia, APQ, CWKPQ, GPQ.
- 🟡 Verify leader loss, reconnect, timeout, party-size, failure exit, and cleanup behavior.
- 🟡 Verify reward NPC/exchange economy balance.
- 🟡 Perform multi-client PQ regression after basic party/buddy/guild/trade validation is clean.

# 20. Events / Minigames

- ✅ Event script inventory/classification audit implemented.
- ✅ Missing `init()` detection.
- ✅ Event-manager case collision/missing manager checks.
- ✅ Seasonal scheduling safety checks.
- ✅ Dormant/legacy scripts remain report-only rather than silently enabled.
- ✅ RPS implementation/handler/opcode/NPC/WZ dependency audit exists.
- ✅ Event/minigame audit tooling exists.
- ✅ Staff event-operation/abort/cleanup procedure documented.
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
- ✅ Timed stacks merge only with compatible expiration semantics.
- ✅ Invalid/zero/negative slot-max paths fail closed.
- ✅ Direct-trade untradeable flag enforcement exists.
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
- 🟢 Storage settlement hardening is live.
- 🟢 Storage fee behavior has been runtime-verified.
- 🟡 Storage + disconnect race test.
- 🟡 Concurrent account-storage test.
- 🟡 Restricted/custom item bypass test.
- 🟡 Storage meso edge cases.

# 23. Trade / Free Market / Merchants / PlayerShop / Duey

- ✅ Direct Trade has lock/confirmation/replay protections.
- ✅ Symmetric partner validation exists.
- ✅ Trade cancel restores items/mesos.
- ✅ Meso-cap/space checks exist.
- ✅ Normal direct trade has been runtime-tested.
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
- ✅ Duey is disabled in production (`USE_DUEY: false`).
- ✅ Trade button → Free Market routing exists with safety restrictions.
- ✅ Free Market Cash Shop field-limit correction is live with the matching client WZ patch.
- ✅ Regular Store Permit behavior is corrected (`USE_ERASE_PERMIT_ON_OPENSHOP: false`).
- 🟡 Cancel/disconnect/channel-change races.
- 🟡 Simultaneous merchant/PlayerShop purchase races.
- 🟡 Merchant restart/recovery live test.
- 🟡 Fredrick recovery live test.
- 🟡 Restricted/custom currency transfer fuzzing.

# 24. Shops / Exchanges / Crafting / Rooted Forge

- ✅ Rooted Forge framework exists.
- 🟡 Audit standard shop inventory mappings.
- 🟡 Verify buy/sell quantity, meso, inventory-space checks, and rollback live.
- 🟡 Verify extreme quantity and meso-cap handling in NPC shops.
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
- ✅ Normal Cash Shop entry/use behavior has been runtime-tested.
- ✅ FM-specific Cash Shop field limit is corrected in server + client WZ.
- 🟡 Verify Cash Shop entry/exit and character state across disconnect/re-entry.
- 🟡 Verify NX balances/scopes.
- 🟡 Verify purchase history/gifting/wishlist/storage if retained.
- 🟡 Verify retry/replay behavior and transfer-state races.
- 🟡 Verify paid rate coupons stay disabled as intended.
- 🟡 Verify cosmetic transfer policy.
- 🟡 Final no-P2W review.

# 28. Party / Guild / Alliance / Buddy / Fame

- ✅ Party framework exists.
- ✅ Guild framework exists.
- ✅ Alliance/buddy/fame frameworks exist.
- 🟡 Perform two-client party lifecycle/leader migration regression.
- 🟡 Verify party HP/status/map updates across channels.
- 🟡 Verify guild create/emblem/ranks/invite/kick/leave/contribution/disband.
- 🟡 Verify alliances if enabled.
- 🟡 Verify buddy lifecycle/capacity/offline state.
- 🟡 Verify fame limits/anti-abuse.
- 🟡 Verify cross-channel social updates.
- 🟡 Perform two-client direct-trade transition/disconnect regression as part of this matrix.

# 29. Channels / World Capacity

- ✅ Production target/configuration is 20 channels (CH1–CH20).
- ✅ Production deployment validates local channel runtime.
- ✅ Production deployment validates player-facing relay ports.
- 🟢 Final production release passed runtime/public-port validation for all 20 channels.
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
- ✅ Race-safe dinput8 proxy/bootstrap behavior exists.
- ✅ Crash/freeze diagnostics exist without automatic telemetry upload.
- ✅ Presentation-only frame limiter preserves game-logic timing.
- ✅ Windowed/borderless/Alt+Enter support is separated from game logic.
- ✅ Client v2 integration guard passed during September 10 finalization.
- ✅ WASD guard passed during September 10 finalization; WASD remains optional/opt-in rather than release-critical.
- ✅ Frame-limiter guard passed during September 10 finalization.
- ✅ Diagnostics guard passed during September 10 finalization.
- ✅ Source-built Win32 client compiled successfully on the GitHub-hosted Windows runner.
- ✅ Live managed `dinput8.dll` overlay rebuilt, packaged, published, and endpoint-verified.
- 🟡 Borderless/fullscreen runtime sweep.
- 🟡 Alt+Enter runtime testing across clean installs.
- 🟡 Multi-monitor/minimize/restore/alt-tab testing.
- 🟡 Clean disconnect/crash behavior.
- 🟡 Clean-machine source-built client test.
- ⏸ Broader login/world/character-select visual overhaul remains deferred until Kaentake review.

# 31. Discord Rich Presence

- ✅ EverLeaf-native Rich Presence implementation extracted from old PR #366 onto current canonical `master`.
- ✅ Old PR #366 closed as superseded; stale donor branch removed.
- ✅ No bot token/OAuth secret embedded.
- ✅ No Discord Game SDK DLL dependency required.
- ✅ No Yuna runtime dependency required.
- ✅ Uses local Discord named-pipe IPC.
- ✅ Reconnect behavior handles Discord not running at client startup.
- ✅ `DiscordRichPresence=false` disables the feature.
- ✅ Default activity contains EverLeaf website and Discord buttons.
- ✅ IPC framing/escaping/acknowledgement tests passed on Windows runner.
- ✅ Win32 client compiled with `DiscordPresence.cpp` wired through the current `dllmain.cpp`.
- 🟢 Rich Presence code is included in the published managed client overlay.
- 🟡 Character/map/job activity hooks still require verified v83 memory contracts before enabling.
- 🟡 Final visual presence-card check on a clean player machine remains useful.

# 32. Launcher / Patcher / Auto-Updater

- ✅ EverLeaf launcher project exists.
- ✅ Patch service exists.
- ✅ Patch manifest tooling exists.
- ✅ Production patch hosting exists.
- ✅ Managed-client baseline exists.
- ✅ Launcher/update infrastructure exists.
- ✅ September 10 live client publication generated the managed overlay, updated the patch manifest, published to Oracle patch storage, and verified public patch endpoints.
- ✅ Player-facing bootstrap/default game IP uses relay `129.159.114.146`.
- ✅ Player-facing launcher-first/raw-EXE guidance is documented.
- 🟡 Verify launcher self-update.
- 🟡 Verify damaged-file repair/hash validation.
- 🟡 Verify interrupted update atomicity/rollback/retry.
- 🟡 Verify Play launches the correct executable/config.
- 🟡 Add technical enforcement/handling for raw EXE launches if desired beyond documentation.
- 🟡 Verify signing/provenance strategy.
- 🟡 Clean-machine install/update/repair test.

# 33. Website / CMS

- ✅ Production website/CMS exists.
- ✅ Website is Git-backed from `/opt/everleaf/web-repo`.
- ✅ Runtime points through `/opt/everleaf/web -> /opt/everleaf/web-repo/web`.
- ✅ Mutable `.env` and data are externalized under `/opt/everleaf/web-state`.
- ✅ `everleaf-web.service` is active.
- ✅ Home, downloads, news, account, rankings, Wiki, help/support, auth routes exist.
- ✅ Major public UI/UX redesign exists.
- ✅ Rankings redesign exists.
- ✅ Wiki redesign exists.
- ✅ Dark public theme restoration merged.
- ✅ Production web readiness hardening exists.
- ✅ Local v83 WZ avatar renderer exists and rankings use it.
- ✅ Staff-reviewed account-recovery request queue and player documentation exist.
- 🟡 Final page-by-page visual polish, especially rankings, Wiki, and login presentation.
- 🟡 Verify registration/login against production game DB.
- 🟡 Verify rankings stale/deleted/renamed character behavior.
- 🟡 Verify live server/channel status integration.
- 🟡 Verify production download/launcher manifest links.
- 🟡 Verify admin auth/session/CSRF/rate-limit/security controls.
- 🟡 Continue responsive/mobile polish.

# 34. Database / Migrations / Admin

- ✅ Base DB/drop/shop/admin SQL exists.
- ✅ Migration framework exists.
- ✅ Weekly progression migration exists.
- ✅ Verdant Marks migration exists.
- ✅ PQ Points migration exists.
- ✅ Rooted migration work exists.
- ✅ Production database backups are automated and verified.
- ✅ DBeaver remote administration path is configured.
- ✅ Class changes can be applied without server restart.
- 🟡 Test migrations from clean baseline.
- 🟡 Test sequential upgrade from current production schema.
- 🟡 Verify migration idempotency/safe-failure behavior.
- 🟡 Verify constraints/indexes/uniqueness for reward/currency systems.
- 🟡 Verify least privilege and no public MySQL exposure.
- 🟡 Define orphaned/deleted-account character cleanup policy.
- 🟡 Review relationship integrity for inventory/equipment/quest/social rows belonging to deleted accounts/characters.
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
- ✅ Normal storage/direct-trade/merchant/Cash-Shop paths have targeted runtime evidence.
- 🔧 **Fix `mobskill` command permission registration:** it is currently registered at rank 0 despite GM2 placement; review `gachalist`/`loot` rank intent in the same block and add regression coverage.
- 🔧 Complete broad packet-validation audit.
- 🔧 Malformed packet fuzzing.
- 🔧 Broad dupe/race-condition matrix.
- 🟡 Trade transition/disconnect race cases.
- 🟡 Cash Shop disconnect transfer/re-entry.
- 🟡 Quest reward replay after disconnect/relog.
- 🟡 NPC shop extreme quantity and meso-cap paths.
- 🟡 Drop/pickup races and cross-system persistence races.
- 🟡 Verify quantities server-side across item/meso/NX/custom currencies.
- 🟡 Verify NPC/quest/shop/map proximity/state validation where required.
- 🟡 Verify unauthorized GM/admin command rejection after command-rank defect is corrected.
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
- 🟡 Cross-system persistence races involving more than one subsystem.

# 37. SoloMapling / Automated Gameplay Agents

- ✅ SoloMapling donor baseline integrated/pinned.
- ✅ Headless/real server-side bot-client foundation exists.
- ✅ QA bot provisioning normalized to controlled single-bot creation.
- ✅ Synthetic bot persistence disabled.
- ✅ Empty-map travel routing implemented.
- ✅ GCTravel/GCMove graph integration exists.
- ✅ Potion restock exists.
- ✅ Combat reachability improvements exist.
- ✅ Distant-target handling exists.
- ✅ Projectile supplies exist.
- ✅ Loadout reapply exists.
- ✅ Untargetable-map rerouting exists.
- ✅ Basic hunt/death/fleet/soak/class behavior was live-tested.
- ⏸ Further pathfinding/terrain/long-soak/autonomous progression work is intentionally parked unless the project returns to it.
- 🔴 Fully unattended live-client login→progression E2E remains a major future gap if we decide to pursue it.

# 38. Automated QA

- ✅ QA agent infrastructure exists.
- ✅ Static/deep QA tooling exists.
- ✅ Runtime QA tooling exists.
- ✅ Game-agent tooling exists.
- ✅ Maven build/test/package tooling exists.
- ✅ World/NPC/portal/reactor/quest audits exist.
- ✅ Economy/item/merchant audits exist.
- ✅ Full Maven test suite passed after final branch-only preservation before workflow-only cleanup.
- ✅ Native Discord Windows validation passed.
- ✅ Client v2 integration/WASD/frame-limiter/diagnostics guards passed during finalization.
- ✅ Heavy QA/build workflows were converted to manual-only where continuous execution was generating unnecessary runner usage.
- ✅ Maintained human-readable `docs/KNOWN_ISSUES.md` and machine-readable `docs/known-issues.json` registers exist.
- 🟡 Run automated gameplay QA against the actual packaged client/release when valuable.
- 🟡 Add regression tests for every fixed exploit/critical bug.

# 39. Performance / Stability / Soak

- 🔴 Realistic concurrent player load test.
- 🔴 Multi-hour/day soak test.
- 🔴 Concurrent boss/PQ instance load.
- 🔴 Simultaneous login/channel-change test.
- 🔴 Database hotspot profiling.
- 🔴 Map/mob scheduler profiling.
- 🔴 GC/heap/thread/socket/file-descriptor telemetry under load.
- 🔴 Reconnect/network-failure simulation.
- 🟡 Leave load/concurrency stress testing until gameplay, transaction, and multi-client correctness passes are substantially complete.
- 🟡 Measure before changing JVM/runtime tuning.

# 40. Logging / Monitoring / Operations

- ✅ Log rotation exists.
- ✅ Disk monitoring exists.
- ✅ Character-persistence diagnostics exist.
- ✅ Production-readiness audit exists.
- ✅ Production health/runtime validation exists.
- ✅ Public game-port validation exists.
- ✅ Production rollback exists.
- ✅ Production pre-deploy backup exists.
- ✅ `everleaf-healthcheck.timer` and `everleaf-disk-monitor.timer` provide normal server-side scheduled health coverage.
- ✅ GitHub production monitoring workflow is manual-only to avoid redundant hosted-runner usage.
- ✅ Discord status-monitor deployment workflow is explicit/manual.
- ✅ Formal restart/recovery/rollback/restore operations runbook exists.
- ✅ Emergency stop/containment/reopen runbook exists.
- 🟡 Add/verify proactive production alerts where server-side timers/bot do not already cover them.
- 🟡 Structured gameplay/reward/trade/storage anomaly logging.
- 🟡 Client crash/diagnostic collection strategy.

# 41. Incident / Security Investigation

- ✅ Relevant nginx evidence preserved for the active account/incident investigation.
- ✅ `trustProxy` production configuration identified.
- 🟡 Complete correlated timeline across Oracle/server, Git/GitHub, ChatGPT/Codex/Work, and personal-PC evidence where relevant.
- 🟡 Produce final incident conclusion/remediation report.
- 🟡 Keep incident investigation separate from ordinary gameplay development.

# 42. Player Documentation

- ✅ Definitive installation/launcher guide: `docs/player/INSTALLATION_AND_SUPPORT.md`.
- ✅ Clear launcher-first/raw-EXE guidance.
- ✅ Account creation/recovery/support documentation, including the current staff-reviewed recovery queue.
- ✅ Rates/level-250/post-200 progression documentation.
- ✅ Verdant Marks documentation.
- ✅ PQ Points documentation.
- ✅ No-HP-washing progression explanation.
- ✅ Boss/PQ/custom-content documentation.
- ✅ Known-issues/reporting documentation in `docs/KNOWN_ISSUES.md`.
- ✅ Antivirus false-positive guidance without recommending global antivirus disablement.

# 43. Staff / GM Documentation

- ✅ Source-verified GM command/permission reference: `docs/staff/GM_COMMANDS_AND_PERMISSIONS.md`.
- ✅ Player-support procedures and account-recovery handling: `docs/staff/OPERATIONS_AND_INCIDENTS.md` + `docs/staff/ACCOUNT_RECOVERY_PROCEDURE.md`.
- ✅ Rollback/economy incident procedures.
- ✅ Ban/appeal/evidence procedures: `docs/staff/MODERATION_AND_APPEALS.md`.
- ✅ Event-operation procedures: `docs/staff/EVENT_OPERATIONS.md`.
- ✅ Deploy/restart/backup/restore runbook: `docs/staff/RECOVERY_AND_RESTORE.md` plus production release guide.
- ✅ Exploit-response/emergency shutdown procedure: `docs/staff/OPERATIONS_AND_INCIDENTS.md` + `docs/staff/EMERGENCY_SHUTDOWN.md`.

# 44. Historical Git Work / Reconciliation

The prior stacked-branch cleanup is complete. Historical PRs remain available as Git history/reference, but they are not active development lines.

- ✅ PR #366 — native Discord Rich Presence — closed as superseded after unique implementation was extracted, validated, and shipped from current master.
- ✅ Old client donor branch removed.
- ✅ Old `release-dev` line removed.
- ✅ Obsolete stacked maintenance/development branches removed.
- ✅ `master` is the sole canonical active line; temporary documentation refs are identical to `master` and carry no unique work.
- ✅ No open PRs remain after the September 10 cleanup/documentation consolidation.
- ✅ Future work should normally land directly on `master` through the authorized Codex Connector bypass unless a real review/CI branch is deliberately useful.

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
- ✅ Strong server audit/test coverage.
- ✅ Substantial anti-dupe/reward/storage/merchant hardening.
- ✅ Native Discord Rich Presence integrated and published.
- ✅ One canonical branch line and clean repository structure.
- ✅ Maintained player/staff documentation baseline and known-issues register.

## Remaining closed-alpha validation

- 🟡 Clean-machine launcher/client install.
- 🟡 Multi-character persistence/restart test.
- 🟡 Advancement playthrough.
- 🟡 Major quest chains.
- 🟡 Boss/PQ real-client testing.
- 🟡 Direct trade/merchant/storage race testing.
- 🟡 Soak/load testing.
- 🔧 Correct the confirmed `mobskill` command-rank defect before broad external testing.

**Assessment:** EverLeaf is closed-alpha capable, but not yet public-beta hardened.

# 46. Public Beta Readiness

Main remaining blockers:

1. 🔧 Correct the confirmed `mobskill` rank-0 permission defect and re-audit command authorization.
2. 🔴 Automated live-client/E2E coverage if we choose to make that a beta gate.
3. 🔴 Soak/load/concurrency testing.
4. 🟡 Boss/PQ live regression matrix.
5. 🟡 Combat formula/runtime parity.
6. 🟡 Trade/storage/merchant/Cash-Shop race testing.
7. 🟡 Advancement/boss-prerequisite quest playthroughs.
8. 🟡 Clean-machine launcher install/update/repair.
9. 🟡 Website/account/rankings/channel integration verification.
10. 🟡 Packet/admin/web security pass.
11. 🟡 Economy/boss-drop/source-sink balance.

# 47. Public Launch Readiness

- 🟡 Critical/high-severity issues closed or consciously accepted.
- ✅ Game release line consolidated into canonical `master`.
- ✅ Current server release reproducible and deployed through the guarded workflow.
- ✅ Current managed client overlay reproducible/published through the maintained client workflow.
- 🟡 Client/server/launcher assets verified from clean install.
- 🟡 Live channel count/config verified with actual client channel switching across all channels.
- 🟡 Website/CMS/auth/rankings/status verified end-to-end.
- 🟡 Economy/security/performance/load validation complete.
- ✅ Backup/restore/rollback foundation validated.
- ✅ Player/staff documentation baseline published and indexed.
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

# Recently Closed Gameplay / Production / Repository Work

- ✅ AP/SP resets and mastery books hardened.
- ✅ PQ clear idempotency, event reward idempotency, and storage settlement hardened.
- ✅ Aran High Defense damage reduction fixed.
- ✅ Duplicate party Family Reputation fixed.
- ✅ Event unregister replay fixed.
- ✅ Event death/Wheel revive bypass fixed.
- ✅ Production WZ staging hardlink fallback fixed.
- ✅ Production website migrated to Git-backed checkout with mutable state externalized.
- ✅ Origin/relay network roles normalized: Oracle origin for deployment, relay for player traffic.
- ✅ SoloMapling QA bot persistence, routing, restock, combat reachability, projectile supply, loadout, and untargetable-map behavior improved and live-tested; further work parked.
- ✅ Workflow-definition cleanup removed/disabled junk-trigger paths and moved heavyweight guards/audits to manual execution.
- ✅ PR #366 Discord implementation salvaged without merging its stale branch ancestry.
- ✅ Native Discord Rich Presence passed Windows validation and shipped in the managed client overlay.
- ✅ Old client/maintenance branches removed; repository returned to one canonical `master` line.
- ✅ Final production rebuild/restart deployed exact source SHA `92a646d6c42a4f5e100f8a0b2ccc6f1bfcabd45a`.
- ✅ Final production release validated 44,237 v95 XML files, login 8484, all 20 channels, and all player-facing relay ports.
- ✅ Documentation audit/consolidation completed and merged through PR #385.
- ✅ Maintained player installation/support, progression/content, and account-recovery guides completed.
- ✅ Maintained GM permissions, moderation/appeals, staff account-recovery, event operations, recovery/restore, and emergency-shutdown runbooks completed.
- ✅ Maintained human-readable and machine-readable known-issues registers created.

# Immediate Priority Queue

1. **Fix command authorization defect** — register `mobskill` at the intended staff rank, review `gachalist`/`loot` rank intent, and add player-rejection regression coverage.
2. **Boss runtime regression** — Zakum, Horntail, Papulatus, Pink Bean, Fallen Cygnus/Empress, plus prerequisite/entry/death/re-entry behavior.
3. **Systematic class/skill runtime matrix** — Explorer, Cygnus, Aran, Evan; attacks, buffs, passives, summons, movement, party effects, status interactions.
4. **Advancement + boss-prerequisite quests** — live progression, repeat/abuse/disconnect paths.
5. **NPC / portal / reactor runtime sweep** — focus on high-impact travel, advancement, boss, storage/shop/event/custom paths.
6. **Transaction/exploit edge cases** — trade transition, Cash Shop disconnect transfer/re-entry, quest reward replay, NPC-shop extremes, drop/pickup races, cross-system persistence races.
7. **Client runtime regression** — clean install, launcher repair/update, crash/disconnect, windowing, Alt+Enter, channel switching.
8. **Source-first authentication/security audit** — packet/state/admin/web review with targeted live confirmation only where static inspection cannot prove behavior.
9. **Two-client social/transaction matrix** — party, buddy, guild, trade, cross-channel updates.
10. **PQ multi-client regression** — after core two-client systems are clean.
11. **Website/account/rankings final verification and page-by-page polish**.
12. **Economy/balance pass** — post-200 pacing, boss rewards, rare scrolls, Verdant/PQ Points, meso generation/sinks, Gachapon.
13. **Performance/load/concurrency testing last** — only after gameplay and transaction correctness are substantially clean.
14. **Kaentake review → Phase 2 client decision** — connected login/world/character panorama, broader branding/UI redesign, direct Evan/future class cards remain deferred until that review.

# Current Completion Assessment

EverLeaf has moved beyond repository consolidation, broad static-content import, the first major transaction-hardening stage, and the documentation cleanup stage. Core v95 backport work, Future Henesys/Stronghold/Fallen Cygnus, backup/DR, level-250 progression, survivability replacement, AP/SP/mastery hardening, Aran High Defense, PQ/event reward idempotency, storage settlement, Family Reputation duplication, event unregister replay, Wheel/event death bypass, native Discord Rich Presence, client publication, Git-backed website deployment, workflow cleanup, branch consolidation, player/staff runbooks, and maintained known-issues documentation are implemented.

The exact final canonical server source SHA `92a646d6c42a4f5e100f8a0b2ccc6f1bfcabd45a` was rebuilt and deployed to production. The final release is healthy with the canonical 44,237-file v95 XML baseline, login server, all 20 channels, and player-facing relay ports verified. Documentation-only commits after that deployment do not change the currently running game release SHA.

The largest remaining uncertainty is now **runtime behavior under real multi-client gameplay and load**: boss/PQ lifecycle, full class/combat parity, advancement/prerequisite quest behavior, persistence/concurrency and anti-dupe race testing, clean-machine client/launcher behavior, final website/account integration, and performance/operations validation. A newly confirmed source-level `mobskill` command registration defect is now tracked explicitly and should be corrected before broad external testing.

## Operating rule

Treat this file as the canonical EverLeafMS roadmap/status document. Preserve its detailed section structure, update statuses when work materially changes state, and do not replace it with a condensed rewrite. Do not infer current production state from old PR bodies, stale branches, or historical workflow runs.