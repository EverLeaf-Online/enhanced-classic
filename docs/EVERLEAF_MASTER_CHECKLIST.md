# EverLeaf Master Development Checklist

Canonical repository-backed working checklist for EverLeafMS.

Last synchronized: **2026-09-10** after repository consolidation, workflow-definition cleanup, native Discord Rich Presence extraction/validation, live client publication, website Git migration, final branch cleanup, and the final guarded production rebuild/restart.

This document preserves the detailed checklist we have been maintaining, but combines overlapping categories so the roadmap is easier to use without losing the underlying work items.

## Current production baseline

- Repository: `EverLeaf-Online/enhanced-classic`
- Canonical branch: `master`
- Running production release source SHA: `92a646d6c42a4f5e100f8a0b2ccc6f1bfcabd45a`
- Running production release: `/opt/everleaf/releases/92a646d6c42a4f5e100f8a0b2ccc6f1bfcabd45a-34484572759-2`
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
- Canonical full-v95 production XML baseline: **44,237 XML files**
- Final production build/restart/health/relay validation: **PASS**
- GitHub branch state after cleanup: **`master` only**

Repository-only documentation/workflow commits may move `master` beyond the running release SHA without changing Java/runtime behavior. A new production deploy is required only when runtime/server content must change.

## Status legend

- ✅ **Complete** — implemented and sufficiently evidenced.
- 🟢 **Live** — deployed and verified on production.
- 🟡 **Needs runtime verification** — implementation/static integrity exists but full gameplay/live validation remains.
- 🔧 **Needs work** — incomplete, partially implemented, or still requires hardening/integration.
- 🔴 **Not done** — significant work remains.
- ⏸ **Paused/deferred** — intentionally postponed.

---

# 1. Repository, Release Management, GitHub Actions, and Deployment

- ✅ Primary repository is `EverLeaf-Online/enhanced-classic`.
- ✅ `master` is the sole canonical production/development line.
- ✅ Historical `release-dev` and obsolete stacked development branches were retired.
- ✅ Useful branch-only audit/tooling work was preserved before cleanup.
- ✅ Stale native-client PR #366 was closed after its unique Discord work was extracted onto current `master`.
- ✅ Obsolete website/client historical work was reconciled instead of mass-merged.
- ✅ Production deployment workflow exists and is guarded.
- ✅ Automatic rollback path exists if production health validation fails.
- ✅ Release switching uses `/opt/everleaf/releases` and `/opt/everleaf/current`.
- ✅ Production source checkout is synchronized through the existing deployment/finalization tooling.
- ✅ Final production rebuild from `92a646d6c42a4f5e100f8a0b2ccc6f1bfcabd45a` succeeded.
- ✅ Final deploy backed up production, rebuilt the JAR, restarted `everleaf.service`, validated login/channel runtime, checked canonical v95 content, verified relay ports, and recorded the deployed release.
- ✅ Obsolete branch-consolidation/client-dev workflows were removed.
- ✅ `run-build.yml` is manual-only.
- ✅ `everleaf-qa.yml` is manual-only.
- ✅ Production-readiness audit is manual-only.
- ✅ Production monitoring workflow is manual-only; server-side systemd health timers remain the normal monitoring path.
- ✅ Version bumping is explicit/manual instead of creating skipped runs on every push.
- ✅ Discord status-monitor deployment is explicit/manual.
- ✅ Heavy client build/publish operations are explicit/narrowly triggered.
- ✅ Client v2 integration, diagnostics, frame-limiter, and WASD guards are retained as manual checks after final validation.
- ✅ Native Discord validation has a dedicated Windows workflow.
- ✅ Direct protected-`master` writes through the ChatGPT Codex Connector bypass are working, reducing unnecessary PR/check runner usage.
- ✅ Branch cleanup returned the repository to `master` only.
- 🟡 Historical Actions-run deletion is optional and remains GitHub API rate-limit sensitive.
- 🟡 Keep runner usage focused on real execution: builds/tests, Windows client validation, artifact publication, and production deployment.

# 2. Core Server, Infrastructure, Backup, Monitoring, and Disaster Recovery

- ✅ Core Java server build/runtime baseline exists.
- ✅ MySQL persistence baseline exists.
- ✅ Oracle production deployment tooling exists.
- ✅ systemd-managed game runtime exists.
- ✅ Log rotation exists.
- ✅ Disk monitoring exists.
- ✅ Production health/runtime validation exists.
- ✅ Public game-port validation exists.
- ✅ Graceful shutdown has been verified across all 20 channels.
- ✅ Character persistence was observed during controlled shutdown.
- 🟢 Final production release is live and healthy.
- ✅ OCI Object Storage bucket `everleaf-backups` configured.
- ✅ VM instance-principal authentication works.
- ✅ VM upload/read access works without VM-side object-delete authority.
- ✅ Daily systemd backup timer exists.
- ✅ MySQL all-database dump included.
- ✅ Critical game/web/nginx/systemd/config data included.
- ✅ Weekly broader archive includes client/WZ recovery data.
- ✅ Backup upload/download verification completed.
- ✅ SHA256 archive verification passed.
- ✅ zstd archive verification passed.
- ✅ SQL contents verified, including `cosmic` database.
- ✅ Daily retention: 45 days.
- ✅ Weekly retention: 90 days.
- ✅ Previous object-version retention: 14 days.
- ✅ Production deploy invokes backup before switching releases.
- ✅ Rollback to previous release exists.
- 🟡 Perform an intentional full VM reboot/recovery exercise later.
- 🟡 Perform a documented isolated restore rehearsal from backups.
- 🟡 Verify reconnect behavior during transient DB/network failures.
- 🟡 Add/verify proactive production alerts and anomaly reporting.
- 🟡 Formalize restart/recovery operations runbook.
- 🟡 Optional future upgrade: multi-region backup replication.

# 3. Network Topology and Production Configuration

- ✅ Oracle origin/deploy host remains `132.145.141.79`.
- ✅ Player-facing traffic uses relay `129.159.114.146`.
- ✅ `HOST: 129.159.114.146`.
- ✅ `LANHOST: 129.159.114.146`.
- ✅ `LOCALHOST: 127.0.0.1`.
- ✅ `SPAWN_BOTS_ON_STARTUP: false`.
- ✅ `USE_DUEY: false`.
- ✅ `USE_ERASE_PERMIT_ON_OPENSHOP: false`.
- ✅ Player/site domain is `everleafms.online`.
- ✅ Client bootstrap uses the relay address.
- ✅ Deployment SSH continues to target the Oracle origin rather than the relay.
- ✅ Obsolete active DuckDNS checks were removed from maintained deployment/workflow paths.
- 🟡 Historical migration docs may retain old hosts/IPs only when clearly labeled historical.

# 4. Accounts, Authentication, Character Creation, Persistence, Database, and Admin

- ✅ Account/database framework exists.
- ✅ Launcher login integration framework exists.
- ✅ Login screen works in the accepted client flow.
- ✅ World selection works.
- ✅ Character selection works.
- ✅ Character selection → gameplay works.
- ✅ Beginner creation works.
- ✅ Beginner → NPC → Evan conversion works.
- ⏸ Direct modern class-card/direct Evan creation remains intentionally paused.
- ✅ Character persistence framework and diagnostics exist.
- ✅ DBeaver remote administration path is configured.
- ✅ Class changes can be performed without a game-server restart.
- ✅ Base DB/drop/shop/admin SQL exists.
- ✅ Migration framework exists.
- ✅ Weekly progression, Verdant Marks, PQ Points, and Rooted migration work exists.
- ✅ Production database backups are automated and verified.
- 🟡 Verify registration end-to-end against production policy.
- 🟡 Verify password hashing and legacy-account compatibility.
- 🟡 Verify bans, temporary bans, IP/MAC restrictions, duplicate-login/session protection, and PIC/PIN behavior if enabled.
- 🟡 Verify account/session persistence across restart/reconnect conditions.
- 🟡 Verify name validation, reserved names, and duplicate-character handling.
- 🟡 Define/fix character deletion/restoration and intentional account-purge semantics; deleted accounts should not unexpectedly leave orphaned character data.
- 🟡 Verify inventories, mesos, skills, quests, keybinds, buddy/guild state, pets, mounts, storage, and cooldowns survive relog/restart.
- 🟡 Test migrations from a clean baseline and sequentially from current production schema.
- 🟡 Verify migration idempotency/safe failure and reward/currency constraints/indexes.
- 🟡 Verify least privilege and that MySQL is not publicly exposed.
- 🟡 Continue relationship-integrity checks for orphaned inventory/equipment/quest/social/account records.
- 🟡 Document safe DBeaver/admin workflows.
- 🟡 Continue mitigation/documentation for users launching the raw EXE instead of the EverLeaf Launcher.

# 5. Classes, Skills, Advancement, AP/SP, Progression, and Survivability

- ✅ Explorer family supported.
- ✅ Playable Cygnus Knights supported.
- ✅ Aran supported.
- ✅ Evan supported.
- ✅ Broad class/skill integrity auditing exists.
- ✅ Evan ten-stage job chain structurally audited.
- ✅ Evan Dragon Fury, Magic Resistance, Slow, Phantom Imprint, Soul Stone, Killer Wings, Critical Magic, Onyx Blessing/Soul Stone classification, and progression/SP behavior fixes exist.
- ✅ Aran High Defense is fixed and live.
- ✅ Achilles uses the same safe damage-reduction path.
- ✅ AP Reset validates target before source mutation and rolls back safely on failure.
- ✅ Same-stat AP Reset rejected.
- ✅ Projected HP/MP cap enforced.
- ✅ AP Reset cannot drop below the EverLeaf survivability floor.
- ✅ SP Reset validates source/target skills, rejects invalid/empty/same-skill cases, and does not consume on failure.
- ✅ 4th-job target mastery cap enforced.
- ✅ Mastery books validate real skill/mastery values and return correct identifiers.
- ✅ Regression coverage includes Explorer/Evan/Beginner/level-250 cases.
- ✅ Central level cap = 250.
- ✅ 201–249 EXP curve implemented with monotonic tests.
- ✅ Level-250 terminal behavior exists.
- ✅ Weekly progression service/account budgets/transactional claims exist.
- ✅ Verdant Marks ledger has unique account/reason protection and is account-bound DB currency.
- ✅ HP-washing replacement exists through `SurvivabilityPolicy` / `SurvivabilityService`.
- ✅ Survivability floor applies on level-up and load/login for Explorer/Cygnus/Aran/Evan.
- ✅ Legitimate/legacy HP above the floor is preserved.
- 🟡 Run a systematic runtime class/skill matrix across Beginner, all Explorer branches, Cygnus classes, Aran, and Evan.
- 🟡 Verify intended advancement quests/NPC chains live for Explorer/Cygnus/Aran/Evan.
- 🟡 Verify SP/level requirements and repeated/wrong-class advancement abuse cases.
- 🟡 Verify buffs, summons, passives, transforms, charges, stance, dispel, seal, movement skills, and party buffs—not only direct attacks.
- 🟡 Verify full projectile/melee/magic/summon formula parity.
- 🟡 Balance 201–249 pacing from real gameplay telemetry.
- 🟡 Verify post-200 milestone/reward pacing live.
- 🟡 Tune survivability curves against real boss damage and update player documentation.

# 6. Combat, Damage, Status Effects, Death, Revive, Party EXP, and Family Reputation

- ✅ Core combat framework exists.
- ✅ Passive damage-reduction helper exists.
- ✅ Core mob status support includes seal, darkness, weakness, stun, curse, poison, slow, dispel, seduce, banish, reverse/confuse, undead, immunities, reflects, accuracy/avoid/speed effects, summons, and related mechanics.
- ✅ Holy Shield status interaction support exists.
- ✅ Normal return-map death path exists.
- ✅ Event revive hook exists.
- ✅ Duplicate event unregister callback replay was fixed.
- ✅ Wheel of Fortune can no longer bypass event/PQ/boss revive semantics.
- ✅ Wheel is not consumed when event handling ejects/unregisters the player.
- ✅ Normal non-event Wheel behavior remains.
- ✅ Party EXP split, leech interval/level-range, party bonus EXP, and Holy Symbol logic exists.
- ✅ Duplicate Family Reputation party-kill award is fixed and live.
- 🟡 Verify physical weapon damage parity.
- 🟡 Verify magic damage parity.
- 🟡 Verify critical, defense, accuracy, avoid, elemental, and level-penalty formulas.
- 🟡 Verify Power Guard, Magic Guard, and Meso Guard edge cases.
- 🟡 Verify weapon/magic cancel, reflect, boss immunities, knockback, invulnerability, phase transitions, summons, and projectile behavior live.
- 🟡 Verify EXP-loss/charm and Resurrection-class interactions.
- 🟡 Perform full boss/PQ death/re-entry matrix.
- 🟡 Validate intended party EXP/leech balance with multiple clients.
- 🟡 Validate multi-party boss membership transitions.

# 7. World Content: Maps, Portals, Reactors, Future Henesys, Stronghold, NPCs, and Quests

- ✅ 5,238 non-Empress maps structurally audited in the broad world pass.
- ✅ Global map-reference, portal-destination, named-exit/script-map, return/death-map, Hidden Street, NPC/mob/reactor-asset audits completed.
- ✅ Portal script filename case audit completed; `Depart_topFloor.js` correction is preserved.
- ✅ Important missing reactor handlers restored, including Zakum prequest, Horntail maze, Romeo/Juliet, Pink Bean transition, GPQ/Sharenian, and Hidden Street/drop reactors.
- ✅ Event/map manager disposal framework exists.
- ✅ Canonical full-v95 baseline is on production and injected into releases.
- ✅ Final deployment verified **44,237 XML files**.
- ✅ Future Henesys implemented; 42 maps in the `271000xxx` range validated.
- ✅ Future Henesys real-client map load verified.
- ✅ Stronghold content/data implemented.
- ✅ Future Henesys/Stronghold mob ranges, NPCs, scripts, portals, names, minimaps, and content data implemented.
- ✅ Fallen Cygnus encounter chain implemented, including normal/elite knights, Shinsoo, and Cygnus `8850011`.
- ✅ Encounter lifecycle/reward/weekly ownership logic exists.
- ✅ Global NPC presence/asset/spawn-coordinate/foothold/roam/duplicate/script/quest-owner audits completed.
- ✅ Global quest structural integrity and Maple Island/Victoria/classic mainland/content/script/NPC/prerequisite/reward/repeatable audits completed.
- ✅ Quest reward quantity/overflow safety audited.
- 🟡 Traverse major travel/Hidden Street chains in packaged client.
- 🟡 Verify reactor animation/state transitions and cleanup after clear/timeout/disconnect/re-entry.
- 🟡 Visually verify important NPC placement.
- 🟡 Live-test travel, advancement, storage, shop, quest, event, and boss-access NPCs.
- 🟡 Live-test advancement and boss prerequisite quest chains.
- 🟡 Live-test abandon/restart, repeatable/daily/weekly cooldown, and reward replay paths.
- 🟡 Verify scripted quest items cannot bypass transfer restrictions.
- 🟡 Full multiplayer Future Henesys/Stronghold/Fallen Cygnus encounter and balance validation remains.

# 8. Monsters, Drops, Bosses, Expeditions, Party Quests, Events, and Minigames

- ✅ Monster IDs/spawn coordinates/footholds/roam ranges audited against available data.
- ✅ Spawn-density review exists.
- ✅ Economy/global-drop audits exist.
- ✅ Ordinary global Chaos Scroll and White Scroll drops removed.
- ✅ Dedicated boss/event framework exists.
- ✅ Zakum, Horntail, Papulatus, Pink Bean, Rooted Zakum, and Fallen Cygnus/Empress implementations exist.
- ✅ Boss/PQ event-manager linkage audit exists.
- ✅ Reward replay/event unregister/death-Wheel protections improved.
- ✅ PQ Points persistence/service exists with account/reason uniqueness protection.
- ✅ Event clear is idempotent.
- ✅ Duplicate legacy Quest Point payout protection exists.
- ✅ Legacy event reward claims are protected per character/reward level/event instance.
- ✅ Inventory-full reward failure remains retryable without duplicate minting.
- ✅ PQ Point values assigned for HPQ, KPQ, LPQ/Ludi Maze, Ellin, OPQ, Pirate, Magatia/Romeo-Juliet, APQ, and CWKPQ paths.
- ✅ Event/minigame inventory/classification, missing `init()`, manager case collision, seasonal scheduling, RPS handler/opcode/NPC/WZ audits exist.
- ✅ Dormant/legacy event scripts remain report-only rather than silently enabled.
- 🟡 Verify actual respawn timing/density, elite/boss triggers, meso ranges, quest-item conditions, ownership/pet-loot/expiry, and drop-rate modifier stacking.
- 🟡 Full live boss runs: Zakum, Horntail, Papulatus, Pink Bean, Cygnus.
- 🟡 Verify expedition signup, leader transfer, disconnect/rejoin cleanup, entry/lockout/cooldown policy, death/re-entry, and reward/drop balance.
- 🟡 Full live PQ runs: HPQ, KPQ, LPQ, Ludi Maze, Ellin, OPQ, Pirate, Romeo/Juliet/Magatia, APQ, CWKPQ, GPQ.
- 🟡 Verify PQ leader loss, reconnect, timeout, party size, failure exit, cleanup, and reward-economy balance.
- 🟡 Runtime-test enabled events/minigames, map reset, reward replay, and disconnect behavior.
- 🔧 Define future seasonal event support policy.

# 9. Items, Inventory, Storage, Trade, Merchants, Shops, Economy, and Cash Shop

- ✅ Item/equipment integrity and item transfer/stack integrity audits exist.
- ✅ Equipment requirement fixes exist.
- ✅ White Scroll behavior audited; failed scroll can preserve slot only when selected, curse/destruction remains possible, and ordinary scrolls consume normally.
- ✅ Expiration-compatible stacking and slot-max normalization/validation exist.
- ✅ Invalid/non-positive slotMax cases fail closed.
- ✅ Direct trade enforces UNTRADEABLE restrictions.
- ✅ Storage withdrawal preflights space before fee; failed insertion restores the item; fees apply after settlement.
- ✅ Storage deposit checks the locked store result and restores item on failure.
- ✅ Direct Trade lock/confirmation/replay protections and symmetric partner validation exist.
- ✅ Trade cancel restores items/mesos; meso-cap/space checks exist.
- ✅ Hired Merchant buy-slot, quantity/price overflow, seller-credit concurrency, persistence transaction, snapshot consistency, Fredrick recovery, listing compensation, and open-persistence protections exist.
- ✅ PlayerShop transaction, buy/take-back, overflow, rollback, and detached snapshot protections exist.
- ✅ Duey ownership/settlement hardening exists even though Duey is disabled in production.
- ✅ Trade button → Free Market routing exists with safety restrictions.
- ✅ Free Market Cash Shop field-limit fix is live with matching client WZ patch.
- ✅ Regular Store Permit behavior corrected.
- ✅ Rooted Forge framework exists.
- ✅ Verdant Marks, PQ Points, NX reward, Maple Leaf exchange, Gachapon/reward-source, and Vote Point audits/frameworks exist.
- 🟡 Throwing star/bullet consumption and projectile edge cases.
- 🟡 Item expiration and untradeable/account-bound/quest flags across every transfer system.
- 🟡 Unique/equip restrictions and malformed-equip serialization/cloning resistance.
- 🟡 Define/finalize rare-scroll acquisition sources and balance.
- 🟡 Storage disconnect/concurrent-account/restricted-item/meso edge cases.
- 🟡 Direct trade cancel/disconnect/channel-change race cases.
- 🟡 Simultaneous merchant/PlayerShop purchase races and merchant restart/Fredrick recovery live tests.
- 🟡 Restricted/custom-currency transfer fuzzing.
- 🟡 Audit standard shops and verify buy/sell quantity, meso, inventory-space, rollback, exchange/token shops, Maker/crafting if retained, and Rooted Forge fulfillment/retry/exploit resistance.
- 🟡 Complete economy source/sink model: meso cap, hourly generation, boss rewards, Gachapon, rare scrolls, inflation simulation, and anti-RMT monitoring/policies.
- 🟡 Cash Shop entry/exit, balances/scopes, gifting/wishlist/storage if retained, retry/replay, paid-coupon disablement, cosmetic transfer policy, and final no-P2W review.
- 🟡 Cash Shop disconnect transfer/re-entry duplication attempts.
- 🟡 NPC shop extreme quantity/meso-cap handling.
- 🟡 Quest reward disconnect/relog replay.
- 🟡 Drop/pickup and cross-system persistence races.
- 🔧 Decide whether fishing remains supported, reworked, or disabled.

# 10. Pets, Mounts, Party, Guild, Alliance, Buddy, Fame, and Channels

- ✅ Pet Vac safety audit exists.
- ✅ Party/guild/alliance/buddy/fame frameworks exist.
- ✅ Production target/configuration is 20 channels.
- ✅ Production deployment validates login and all 20 public channel ports.
- 🟡 Verify pet summon/equip/hunger/closeness/commands/expiry/revive and item/meso pickup ownership restrictions.
- 🟡 Verify multi-pet if enabled.
- 🟡 Verify mounts, saddles, fatigue, skills, unlock quests, and persistence across channel/relog.
- 🔧 Define final universal/earnable Pet Vac design and balance.
- 🟡 Two-client party lifecycle/leader migration/HP/status/map updates.
- 🟡 Guild create/emblem/rank/invite/kick/leave/contribution/disband behavior.
- 🟡 Alliance behavior if enabled.
- 🟡 Buddy capacity/offline-state lifecycle.
- 🟡 Fame limits/anti-abuse and cross-channel social updates.
- 🟡 Manual player channel-change sweep CH1→CH20 and capacity/failure messaging.
- 🟡 PQ multi-client validation after core social/two-client systems are clean.

# 11. Native Client / Client v2 Runtime

- ✅ Accepted flow reaches login/world/character/game.
- ✅ 1280×720 gameplay/client configuration restored.
- ✅ Broken coordinate-only login experiment disabled.
- ✅ `CWvsApp::Run` compatibility behavior restored.
- ✅ No Whack client combat fix exists.
- ✅ Attack-while-moving work exists.
- ✅ No Breath exists.
- ✅ Bootstrap/hook hardening foundation exists.
- ✅ Race-safe `dinput8` proxy/bootstrap logic exists.
- ✅ Crash/freeze diagnostics exist without automatic telemetry upload.
- ✅ Presentation-only frame limiter preserves Maple game-logic timing.
- ✅ Windowed/borderless/Alt+Enter behavior is separated from game logic.
- ✅ Current source-built Win32 client passed Windows build validation during September 10 finalization.
- ✅ Client v2 integration guard passed.
- ✅ WASD guard passed.
- ✅ Frame-limiter guard passed.
- ✅ Diagnostics guard passed.
- ✅ Live managed client overlay was rebuilt, verified, and published.
- 🟡 Borderless/fullscreen/Alt+Enter multi-monitor/minimize/restore/alt-tab runtime sweep.
- 🟡 Clean disconnect/crash behavior.
- 🟡 Clean-machine source-built client test.
- 🟡 Validate future Windows toolset changes against the x86 v83 client before adopting globally.
- ⏸ Broader login/world/character-select visual overhaul remains deferred until Kaentake review.
- ⏸ Connected panorama and direct Evan/future class-card redesign remain deferred with that Phase 2 work.

# 12. Discord Rich Presence

- ✅ EverLeaf-native local Discord IPC implementation is on canonical `master`.
- ✅ Uses the EverLeaf Discord application ID and local named-pipe IPC.
- ✅ No bot token or OAuth secret embedded.
- ✅ No Yuna runtime or `discord_game_sdk.dll` dependency.
- ✅ Handles Discord not running at Maple startup and reconnects later.
- ✅ Can be disabled with `DiscordRichPresence=false`.
- ✅ Default activity includes EverLeaf website and Discord buttons.
- ✅ IPC framing/escaping/acknowledgement tests passed on Windows runner.
- ✅ Win32 client compiled with `DiscordPresence.cpp` wired through current `dllmain.cpp`.
- ✅ PR #366 was superseded/closed after useful code was extracted.
- 🟡 Character/job/map-specific presence remains intentionally unhooked until v83 memory contracts are safely verified.
- 🟡 Final real-user visual validation of Discord display/buttons is still useful.

# 13. Launcher, Patcher, Managed Client, and Auto-Updater

- ✅ EverLeaf launcher project exists.
- ✅ Patch service and manifest tooling exist.
- ✅ Production patch hosting exists.
- ✅ Managed-client baseline exists.
- ✅ Launcher/update infrastructure remains authoritative for managed client files.
- ✅ September 10 client publication rebuilt/verified `dinput8.dll`, generated managed overlay, updated manifest, published to Oracle patch storage, and verified public endpoints.
- 🟡 Verify launcher self-update.
- 🟡 Verify damaged-file repair/hash validation.
- 🟡 Verify interrupted update atomicity/rollback/retry.
- 🟡 Verify Play launches correct executable/config.
- 🟡 Add clear handling for raw EXE launches.
- 🟡 Verify signing/provenance strategy.
- 🟡 Clean-machine install/update/repair test.
- 🟡 Formalize client rollback/version policy.

# 14. Website / CMS

- ✅ Production website/CMS exists and is Git-backed from `/opt/everleaf/web-repo`.
- ✅ Runtime points through `/opt/everleaf/web`.
- ✅ Mutable `.env` and data live outside Git in `/opt/everleaf/web-state`.
- ✅ `everleaf-web.service` is active.
- ✅ Home, downloads, news, account, rankings, Wiki, help/support, auth, rules, terms, and recovery routes exist.
- ✅ Major public UI/UX redesign exists.
- ✅ Rankings redesign exists.
- ✅ Wiki redesign exists.
- ✅ Dark public theme restoration merged.
- ✅ Production web readiness hardening exists.
- ✅ Local WZ character-avatar renderer exists and rankings use it.
- 🟡 Final page-by-page visual polish, especially rankings, Wiki, and login/auth pages.
- 🟡 Verify registration/login against production game DB.
- 🟡 Verify rankings behavior for stale/deleted/renamed characters.
- 🟡 Verify live server/channel-status integration.
- 🟡 Verify production download/launcher manifest links.
- 🟡 Verify admin auth/session/CSRF/rate-limit/security controls.
- 🟡 Continue responsive/mobile polish.

# 15. Security, Exploit Resistance, Concurrency, and Automated QA

- ✅ Repository secret/artifact hardening exists.
- ✅ Reward claim and event-clear idempotency protections exist.
- ✅ Event unregister replay protection exists.
- ✅ Wheel/event revive bypass fixed.
- ✅ Storage settlement rollback hardening exists.
- ✅ Item transfer/stack hardening exists.
- ✅ Duey, merchant, and PlayerShop hardening exists.
- ✅ Weekly/account-currency transactional protections exist.
- ✅ QA agent/static/deep/runtime/game-agent tooling exists.
- ✅ World/NPC/portal/reactor/quest/economy/item/merchant audits exist.
- ✅ SoloMapling integration guardrails exist.
- 🔧 Complete broad packet-validation audit.
- 🔧 Malformed packet fuzzing.
- 🔧 Broad dupe/race-condition matrix.
- 🟡 Verify server-side quantity validation across item/meso/NX/custom currencies.
- 🟡 Verify NPC/quest/shop/map proximity/state validation where required.
- 🟡 Verify unauthorized GM/admin command rejection.
- 🟡 Verify web rate limiting/session/cookie security and that logs avoid secrets/sensitive account data.
- 🟡 Concurrent Verdant Marks/PQ Points earn-spend.
- 🟡 Trade/storage/merchant/Cash Shop/boss-reward disconnect/retry/restart races.
- 🟡 DB rollback tests for failed multi-step rewards.
- 🟡 Add regression tests for every fixed exploit/critical bug.
- 🟡 Maintain a machine-readable known-issues list.
- 🟡 Source-first auth/security review should precede targeted live tests rather than relying on ad-hoc production poking.

# 16. SoloMapling / Automated Gameplay Agents

- ✅ SoloMapling donor baseline integrated/pinned.
- ✅ Headless real server-side bot-client foundation exists.
- ✅ QA bot provisioning normalized.
- ✅ Automatic bot population/persistence disabled.
- ✅ Empty-map travel routing implemented.
- ✅ GCMove/travel graph integration exists.
- ✅ Potion restock, combat reachability, distant-target handling, projectile supply, loadout reapply, and untargetable-map rerouting implemented.
- ✅ Basic live hunt/death/fleet/5-minute soak/class behavior was verified.
- ✅ Disposable runtime smoke is explicitly gated and QA constrained.
- ⏸ Further bot pathfinding/terrain/long-soak work is intentionally parked unless this stream is resumed.
- 🟡 Party/trade/storage automated-agent coverage remains incomplete.
- 🟡 Boss/PQ/quest automated-agent coverage remains incomplete.
- 🔴 Fully unattended real-client login→progression E2E remains a major gap.

# 17. Performance, Stability, Load, and Soak

- ✅ Current production runs 20 channels.
- ✅ Health tooling verifies channel/listener topology.
- 🔴 Realistic concurrent-player load test.
- 🔴 Multi-hour/day soak test.
- 🔴 Concurrent boss/PQ instance load.
- 🔴 Simultaneous login/channel-change test.
- 🔴 Database hotspot profiling.
- 🔴 Map/mob scheduler profiling.
- 🔴 GC/heap/thread/socket/file-descriptor telemetry under load.
- 🔴 Reconnect/network-failure simulation.
- 🟡 Do this after gameplay, transaction, and multi-client correctness work; measure before changing JVM/runtime tuning.

# 18. Incident / Security Investigation

- ✅ Relevant nginx evidence preserved for the active account/incident investigation.
- ✅ `trustProxy` production configuration identified.
- 🟡 Complete correlated timeline across Oracle/server, Git/GitHub, ChatGPT/Codex/Work, and personal-PC evidence where relevant.
- 🟡 Produce final incident conclusion/remediation report.
- 🟡 Keep incident-investigation evidence separate from ordinary gameplay development.

# 19. Player Documentation, Staff Documentation, and Operations Runbooks

- 🔴 Definitive installation/launcher guide.
- 🔴 Clear launcher-only/raw-EXE guidance.
- 🟡 Account creation/recovery/support documentation.
- 🟡 Rates/level-250/post-200 progression documentation.
- 🟡 Verdant Marks documentation.
- 🟡 PQ Points documentation.
- 🟡 No-HP-washing/survivability explanation.
- 🟡 Boss/PQ/custom-content documentation.
- 🟡 Known-issues/reporting documentation.
- 🟡 Antivirus false-positive guidance without recommending global AV disablement.
- 🔴 GM command/permission reference.
- 🔴 Player-support procedures.
- 🔴 Rollback/economy incident procedures.
- 🔴 Ban/appeal/evidence procedures.
- 🔴 Event-operation procedures.
- 🔴 Deploy/restart/backup/restore runbook.
- 🔴 Exploit-response/emergency-shutdown procedure.

# 20. Release Readiness

## Closed Alpha

### Ready / strong enough

- ✅ Reproducible production server deployment.
- ✅ Automatic rollback.
- ✅ Off-VM backup/DR foundation.
- ✅ Login/world/character/game flow.
- ✅ v95 server/client content baseline.
- ✅ Future Henesys/Stronghold/Fallen Cygnus implementation.
- ✅ Broad world-content structural integrity.
- ✅ Core custom progression.
- ✅ Strong static/server audit coverage.
- ✅ Substantial anti-dupe/reward/storage/merchant hardening.
- ✅ Native Discord Rich Presence integrated and client-published.
- ✅ Repository consolidated to one canonical branch.

### Remaining closed-alpha validation

- 🟡 Clean-machine launcher/client install.
- 🟡 Multi-character persistence/restart test.
- 🟡 Advancement playthroughs.
- 🟡 Major quest/boss prerequisite chains.
- 🟡 Boss/PQ real-client testing.
- 🟡 Direct trade/merchant/storage race testing.
- 🟡 Known-issues list.
- 🟡 Soak/load testing.

**Assessment:** EverLeaf remains closed-alpha capable, but is not yet public-beta hardened.

## Public Beta blockers

1. 🔴 Automated real-client/E2E coverage.
2. 🔴 Soak/load/concurrency testing.
3. 🟡 Boss/PQ live regression matrix.
4. 🟡 Combat formula/runtime parity.
5. 🟡 Trade/storage/merchant/Cash Shop race testing.
6. 🟡 Advancement/boss-prerequisite quest playthroughs.
7. 🟡 Clean-machine launcher install/update/repair.
8. 🟡 Website/account/rankings/channel integration verification.
9. 🟡 Packet/admin/web security pass.
10. 🟡 Economy/boss-drop/source-sink balance.
11. 🟡 Player/staff documentation/support procedures.

## Public Launch readiness

- 🟡 Critical/high-severity issues closed or consciously accepted.
- ✅ Canonical repository/release line consolidated to `master`.
- 🟡 Server/client/launcher artifacts reproducible from intended source/workflows.
- 🟡 Clean-install client/server assets validated.
- 🟡 Live channel count/config verified with actual player channel switching.
- 🟡 Website/CMS/auth/rankings/status verified.
- 🟡 Economy/security/performance/load validation complete.
- ✅ Backup/restore/rollback foundation validated.
- 🟡 Player/staff documentation published.
- 🟡 Final launch approval after beta telemetry/balance/security review.

## Post-launch operations

- 🔧 Define patch cadence/emergency-hotfix process.
- 🔧 Define launcher manifest/version policy.
- 🔧 Define DB migration/release process.
- 🔧 Monitor inflation/high-value item generation.
- 🔧 Monitor crashes/disconnect/channel health.
- 🔧 Monitor suspicious trade/storage/merchant/reward behavior.
- 🔧 Maintain public changelog/known issues.
- 🔧 Schedule recurring restore verification/security/performance/content audits.

---

# Recently Completed Major Work

- ✅ AP/SP reset and mastery-book hardening.
- ✅ PQ clear/event reward idempotency and storage settlement hardening.
- ✅ Aran High Defense damage-reduction fix.
- ✅ Duplicate Family Reputation and event unregister replay fixes.
- ✅ Event death/Wheel revive bypass fix.
- ✅ Production WZ staging hardlink fallback fix.
- ✅ Full canonical v95 WZ production baseline and deployment validation.
- ✅ Future Henesys / Stronghold / Fallen Cygnus implementation.
- ✅ OCI backup/DR foundation.
- ✅ Branch consolidation and stale-PR cleanup.
- ✅ Workflow-definition cleanup to reduce runner waste.
- ✅ Native Discord Rich Presence extraction from stale PR #366, Windows validation, and live managed-client publication.
- ✅ Website Git-backed migration with mutable state separated from Git.
- ✅ Final guarded production rebuild/restart from `92a646d6c42a4f5e100f8a0b2ccc6f1bfcabd45a`.
- ✅ Final runtime verification: login `8484`, channels `7575-7594`, and relay connectivity all healthy.

# Immediate Priority Queue

1. **Solo boss regression + boss prerequisite checks** — Zakum, Horntail, Papulatus, Pink Bean, Fallen Cygnus/Empress; lifecycle, death/re-entry, expedition/lockout, rewards.
2. **Systematic class/skill runtime matrix** — all supported class families, buffs/passives/summons/statuses/formulas, not just spot checks.
3. **Advancement + major quest chains** — Explorer/Cygnus/Aran/Evan progression and boss prerequisites under normal/relog/disconnect paths.
4. **NPC / portal / reactor runtime sweep** — high-risk travel, advancement, storage/shop, event, boss-access, and scripted state transitions.
5. **Transaction/exploit edge cases** — direct trade, storage, merchant/PlayerShop, Cash Shop transfer/re-entry, quest-reward replay, NPC shop bounds, drop/pickup/cross-system races.
6. **Clean-client/runtime regression** — clean install, launcher repair/update, Alt+Enter/windowing/multi-monitor, channel change, disconnect/crash behavior.
7. **Authentication/security audit** — source-first packet/session/admin/web review, followed by targeted runtime tests only where static proof is insufficient.
8. **Two-client social validation** — party, buddy, guild, trade, channel transitions.
9. **PQ multi-client validation** — full lifecycle/reconnect/leader/timeout/reward behavior.
10. **Website/account/launcher integration polish** — rankings/Wiki/login/auth/status/downloads plus stale/deleted-character behavior.
11. **Economy/balance pass** — post-200 EXP, rare scrolls, boss drops, currencies, mesos, Gachapon, sinks/sources, anti-RMT policy.
12. **Documentation/runbooks** — player install/progression/support plus GM/deploy/restore/exploit-response procedures.
13. **Load/concurrency/soak testing last** — only after core gameplay and transaction correctness are clean.
14. **Kaentake review → Phase 2 client decision** — only then revisit connected login/world/character panorama and broader visual redesign.

## Operating rule

Treat this file as the canonical EverLeaf roadmap/status document. Update it whenever a task materially changes state. Preserve meaningful historical/evidence context, but combine overlapping categories rather than duplicating the same task in multiple sections. Do not infer production truth from old PR bodies, stale branches, or historical workflow runs.