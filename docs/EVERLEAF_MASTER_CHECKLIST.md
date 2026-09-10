# EverLeaf Master Development Checklist

Canonical repository-backed status for EverLeafMS.

Last synchronized: **2026-09-10** after branch consolidation, production rebuild/redeploy from canonical `master`, website Git migration, workflow cleanup, and native-client Rich Presence extraction.

## Current production baseline

- Repository: `EverLeaf-Online/enhanced-classic`
- Canonical production branch: `master`
- Production source baseline before this maintenance branch: `10adee94a13b1ab3f04a08e3dbc48f2f33de708d`
- Current live release: `/opt/everleaf/releases/10adee94a13b-master-20260910T113147Z`
- Production source checkout: `/opt/everleaf/server`
- Active release symlink: `/opt/everleaf/current`
- Game service: `everleaf.service`
- Website checkout: `/opt/everleaf/web-repo`
- Website runtime symlink: `/opt/everleaf/web -> /opt/everleaf/web-repo/web`
- Website mutable state: `/opt/everleaf/web-state`
- Website service: `everleaf-web.service`
- Player-facing relay: `129.159.114.146`
- Oracle origin / deployment host: `132.145.141.79`
- Public site: `https://everleafms.online`
- Login port: `8484`
- Channels: `7575-7594` (20 channels)

The consolidated `master` was rebuilt, staged as a release, switched live, restarted gracefully, and verified online. The previous release remains available for rollback.

## Status legend

- ✅ Complete / sufficiently evidenced
- 🟢 Live and verified on production
- 🟡 Needs runtime verification or final integration
- 🔧 Needs work
- ⏸ Intentionally paused/deferred

---

# 1. Repository / branch management

- ✅ `master` is the canonical production line.
- ✅ `release-dev` and obsolete development branches were retired.
- ✅ Remote branch count was reduced from the historical branch sprawl to the canonical line plus the remaining native-client donor branch.
- ✅ Useful branch-only audit/documentation/tooling work was preserved before deletion.
- ✅ Obsolete branch-consolidation workflows were removed.
- 🔧 Finish extracting useful work from PR #366 without merging its stale branch ancestry.
- 🔧 Close PR #366 and delete `client/everleaf-native-package-20260905` after validation.
- 🔧 Remove stale branch names from remaining docs/tooling.

# 2. Production deployment / runtime

- ✅ Release-based deployment under `/opt/everleaf/releases`.
- ✅ `/opt/everleaf/current` points to the active release.
- ✅ systemd runtime uses the active release JAR.
- ✅ Graceful shutdown verified across all 20 channels.
- ✅ Character save observed during controlled shutdown.
- 🟢 Consolidated `master` deployment is live and healthy.
- ✅ Rollback release retained.
- 🟡 Recheck full VM reboot behavior later as a disaster-recovery exercise.

# 3. Production configuration / network topology

- ✅ `HOST: 129.159.114.146`.
- ✅ `LANHOST: 129.159.114.146`.
- ✅ `LOCALHOST: 127.0.0.1`.
- ✅ `SPAWN_BOTS_ON_STARTUP: false`.
- ✅ `USE_DUEY: false`.
- ✅ `USE_ERASE_PERMIT_ON_OPENSHOP: false`.
- ✅ Origin/deployment host remains `132.145.141.79`.
- ✅ Player-facing client/game traffic uses relay `129.159.114.146`.
- 🔧 Remove remaining obsolete DuckDNS references from active workflows/scripts.
- 🔧 Audit remaining historical IP assumptions and keep only intentional migration/history references.

# 4. GitHub Actions / workflow policy

- ✅ Obsolete consolidation/client-dev workflows removed.
- ✅ Historical workflow-run cleanup reduced deleted-branch run count substantially.
- ⏸ Further run-history deletion paused by GitHub secondary API rate limiting.
- 🔧 Keep heavyweight build/deploy/QA workflows manual-only while hosted-runner limits make automatic execution noisy/unreliable.
- 🔧 Remove stale branch triggers.
- 🔧 Remove unnecessary scheduled and `workflow_run` fan-out.
- 🔧 Keep production deployment guarded and explicit.
- 🔧 Keep client build/publish explicit and separately invokable.

# 5. Backups / disaster recovery

- ✅ OCI Object Storage backup path exists.
- ✅ Daily backup timer exists.
- ✅ MySQL dumps included.
- ✅ Critical game/web/nginx/systemd/config data included.
- ✅ Broader weekly recovery archive includes client/WZ recovery data.
- ✅ Upload/download/hash/archive validation previously completed.
- ✅ Production deployment workflow invokes backup before release switch.
- 🟡 Perform another end-to-end restore rehearsal to a scratch target.
- 🟡 Review long-term retention and optional multi-region replication later.

# 6. Core login / account flow

- ✅ Login server works.
- ✅ World selection works.
- ✅ Character selection works.
- ✅ Character select to gameplay works.
- ✅ Channel switching works.
- 🟡 Verify registration end-to-end.
- 🟡 Verify password hashing/legacy compatibility.
- 🟡 Verify duplicate-login/session cleanup.
- 🟡 Verify PIN/PIC behavior if enabled.
- 🟡 Verify bans/IP/MAC restrictions and reconnect edge cases.

# 7. Character creation / persistence

- ✅ Beginner creation works.
- ✅ Beginner -> NPC -> Evan conversion works.
- ⏸ Direct modern class-card/direct Evan creation remains intentionally paused.
- 🟡 Verify name validation/reserved/duplicate-name rules.
- 🟡 Define and verify character/account deletion cleanup.
- 🟡 Verify full character state survives relog/restart: inventory, mesos, skills, quests, keybinds, social state, pets, mounts, cooldowns.

# 8. Classes / jobs / skills

- ✅ Explorer family supported.
- ✅ Cygnus Knights supported.
- ✅ Aran supported.
- ✅ Evan supported.
- ✅ Aran High Defense fix retained.
- ✅ Achilles reduction path retained.
- ✅ Multiple Evan skill hardening fixes retained.
- 🔧 Run a systematic runtime matrix for every class instead of spot checks.
- 🔧 Verify passives, buffs, summons, transforms, charge, stance, dispel, status effects, projectiles, melee, and magic interactions.

# 9. AP/SP reset / mastery books

- ✅ Reset validation/rollback hardening exists.
- ✅ Same-stat and same-skill invalid paths are rejected.
- ✅ HP/MP safety floors/caps are enforced.
- ✅ 4th-job mastery target validation exists.
- ✅ Failed reset paths do not consume items.
- 🟡 Live-test uncommon class/skill reset combinations.

# 10. Progression / level cap / EXP

- ✅ Level cap 250.
- ✅ Post-200 progression framework exists.
- ✅ 201-249 EXP curve and level-250 terminal behavior exist.
- ✅ Weekly progression/ledger framework exists.
- 🟡 Balance post-200 pacing with live telemetry.
- 🟡 Verify milestone rewards and budget limits live.

# 11. Survivability / HP-washing replacement

- ✅ Survivability policy/service exists.
- ✅ Applied on level-up/load.
- ✅ Existing legitimate high HP is not reduced.
- ✅ AP Reset cannot bypass survivability floor.
- 🟡 Tune final HP curves against actual boss damage.

# 12. Combat / damage / statuses

- ✅ Core combat framework present.
- ✅ Major monster/player status mechanics present.
- 🟡 Verify physical damage formulas.
- 🟡 Verify magic damage formulas.
- 🟡 Verify crit/accuracy/avoid/defense/elemental/level-penalty behavior.
- 🟡 Verify guards, cancels, reflects, invulnerability, knockback, summons, projectiles and boss phases.

# 13. Party EXP / leech / family

- ✅ Party EXP split and Holy Symbol handling exist.
- ✅ Leech interval/level-range logic exists.
- ✅ Duplicate Family Reputation award path was fixed.
- 🟡 Multi-client party EXP validation still needed.
- 🟡 Boss-party membership transition cases still needed.

# 14. Death / revive / charms

- ✅ Normal death path works.
- ✅ Wheel-related event bypass was hardened.
- ✅ Duplicate unregister callback replay was hardened.
- 🟡 Verify EXP loss and charm interactions.
- 🟡 Verify Resurrection and boss/PQ revive paths.
- 🟡 Verify disconnect while dead and re-entry semantics.

# 15. Maps / portals / reactors

- ✅ Broad world/map-reference audits completed.
- ✅ Portal case/reference audits completed.
- ✅ Return/death/forced-return references audited.
- ✅ Major missing reactor handlers restored.
- 🟡 Traverse major travel/Hidden Street chains in packaged client.
- 🟡 Verify reactor animation/state transitions live.
- 🟡 Verify cleanup after timeout/disconnect/re-entry.

# 16. Future Henesys / Stronghold / Fallen Cygnus / Empress

- ✅ Future Henesys implemented.
- ✅ Stronghold implemented.
- ✅ Fallen Cygnus/Empress content implemented.
- ✅ Associated maps, mobs, NPCs, scripts, portals, names and minimap content implemented.
- 🟡 Multiplayer runtime/balance validation remains.

# 17. NPCs

- ✅ Global NPC presence/asset/script audits exist.
- ✅ Coordinates/footholds/roam ranges audited.
- 🟡 Visually verify important NPC placement.
- 🟡 Live-test travel, advancement, storage, shop, quest, boss and event NPCs.

# 18. Quests

- ✅ Broad structural quest audits completed.
- ✅ Maple Island/Victoria/mainland/scripted quest audit tooling exists.
- ✅ Reward/reference/repeatability checks exist.
- 🟡 Live-test job advancement chains.
- 🟡 Live-test boss prerequisite chains.
- 🟡 Live-test abandon/restart/relog replay paths.
- 🟡 Verify repeatable/daily/weekly cooldown behavior.

# 19. Monsters / spawns / drops

- ✅ Spawn IDs/footholds/coordinates audited.
- ✅ Economy/global-drop auditing exists.
- ✅ Ordinary global Chaos/White Scroll drops removed.
- 🟡 Verify respawn timing/density live.
- 🟡 Verify elite/boss trigger behavior.
- 🟡 Verify meso/quest/global drop conditions and modifiers.

# 20. Bosses / expeditions

- ✅ Zakum implementation exists.
- ✅ Horntail implementation exists.
- ✅ Papulatus implementation exists.
- ✅ Pink Bean implementation exists.
- ✅ Fallen Cygnus/Empress implementation exists.
- ✅ Rooted Zakum exists.
- 🔧 Run solo-boss regression suite first.
- 🔧 Run full party lifecycle later: signup, leader transfer, disconnect/rejoin, death/re-entry, lockouts and rewards.

# 21. Party Quests

- ✅ PQ persistence/points and idempotent reward protections exist.
- 🔧 Multi-participant runtime coverage needed for major PQs.
- 🔧 Verify leader/member disconnect, timeout, stage cleanup and reward duplication protections.

# 22. Events / minigames

- ✅ Event manager framework exists.
- 🟡 Verify scheduled and GM events.
- 🟡 Verify timeout/disconnect/map cleanup and duplicate reward paths.

# 23. Travel systems

- 🟡 Verify Victoria/Orbis/Ludi/Ellinia/Ariant/Leafre/Mu Lung travel paths.
- 🟡 Verify departure/arrival timers.
- 🟡 Verify disconnect/channel-change mid-travel.

# 24. Drops / pickup

- 🟡 Verify ownership/party rights/pet loot/expiry.
- 🔧 Test simultaneous pickup races.
- 🔧 Test map change, inventory-full and disconnect during pickup.
- 🔧 Test rollback/persistence race cases.

# 25. Inventory

- 🟡 Verify all inventory categories and stack merge/sort.
- 🟡 Verify expiration/untradeable/cash/pet metadata.
- 🟡 Verify scrolling, stars/bullets/rechargeables.
- 🔧 Verify inventory-full transaction failure safety.

# 26. Economy

- 🟡 Verify meso cap/overflow paths.
- 🟡 Verify NPC buy/sell, merchant, storage and trade meso handling.
- 🟡 Review taxes/fees and high-value transfers.
- 🔧 Search for infinite-meso and overflow edge cases.

# 27. Player shops / hired merchants

- ✅ Store Permit consumption behavior corrected.
- ✅ Merchant persistence/recovery work retained.
- 🔧 Test owner/buyer disconnect, stack splitting, partial purchase, max-meso, restart settlement, duplicate retrieval and stale cleanup.

# 28. Storage

- ✅ Storage works.
- ✅ Storage fee behavior corrected.
- ✅ Race/failure handling was hardened.
- 🔧 Test full storage/inventory, max mesos, metadata preservation, pets/cash items, disconnect/restart during transaction.

# 29. Cash Shop

- ✅ Normal access works outside FM.
- ✅ Basic entry/exit flow covered.
- 🔧 Test disconnect entering/leaving, re-entry, state restoration, inventory transfer, gifts, wishlist, packages, pets, NX edge cases and transaction replay.

# 30. Trade / transaction integrity

- ✅ Normal direct trade works.
- 🔧 Test accept/cancel timing races.
- 🔧 Test disconnect during trade.
- 🔧 Test channel change during pending transactions.
- 🔧 Test server shutdown during transaction.
- 🔧 Test cross-system persistence races involving storage/merchant/Cash Shop.

# 31. Social systems

- 🔧 Multi-client party testing.
- 🔧 Buddy add/remove and presence testing.
- 🔧 Guild create/invite/kick/leave/rank testing.
- 🔧 Alliance/family/messenger/marriage systems if enabled.
- 🔧 Whisper/blacklist behavior.

# 32. Pets

- 🟡 Verify summon/dismiss/food/closeness/level/expiration/revive/name/equip.
- 🔧 Verify pet-loot races and storage/trade/Cash Shop interactions.

# 33. Mounts

- 🟡 Verify acquisition/summon/fatigue/feeding/map restrictions/death/relog/channel switch.

# 34. Character stats

- 🟡 Verify AP allocation/auto-assign/HP-MP behavior/stat caps/equipment requirements.
- 🟡 Verify recalculation after class change.

# 35. Equipment / scrolling

- 🟡 Verify equip/unequip and scroll success/failure.
- 🟡 Verify White Scroll/Clean Slate/Chaos/Hammer only where supported.
- 🟡 Verify stars, cash covers, expiration and weapon restrictions.

# 36. Buffs / debuffs

- 🟡 Verify overwrite/strongest-buff rules.
- 🟡 Verify dispel/death/map/channel/Cash Shop transitions.
- 🟡 Verify party aura/summon/status timer behavior.

# 37. Authentication / security

- 🔧 Source-first authentication audit.
- 🔧 Session fixation/invalidation.
- 🔧 Password-reset abuse.
- 🔧 PIN/PIC bypass logic.
- 🔧 brute-force throttling/account lockout.
- 🔧 duplicate session/HWID/IP policy.
- 🔧 GM/admin authorization boundaries.
- 🔧 SQL injection/XSS/path traversal/secret scanning where applicable.

# 38. GM / admin

- 🟡 Audit permissions by GM tier.
- 🟡 Audit destructive commands and item/character mutation.
- 🟡 Audit ban/mute/warp/hide/summon/shutdown logging.
- ✅ Known command set includes `!maxskill`, `!resetskill`, `!warp`; no `!skill` command.

# 39. Logging / observability

- ✅ Startup/shutdown/systemd logging exists.
- ✅ health/disk monitoring services exist.
- 🟡 Review auth/trade/merchant/storage/Cash Shop/GM exploit logging coverage.
- 🟡 Review CPU/memory/thread/socket/DB-pool observability.

# 40. Performance / load

- ⏸ Run after correctness work.
- 🔧 10/25/50/100-client staged load tests.
- 🔧 login bursts/channel distribution/boss/merchant load.
- 🔧 memory leak/GC/thread/file-descriptor/DB-connection soak tests.

# 41. SoloMapling / QA bots

- ✅ Runtime integration exists.
- ✅ QA bot provisioning normalized.
- ✅ persistence prevention, travel graph, potion restock, combat reachability, distant targets, projectile supplies and alt-map routing work retained.
- ✅ Hunt/death/fleet/multi-class short soak previously verified.
- ⏸ Further pathfinding and long-duration bot work parked.

# 42. Client runtime baseline

- ✅ Widescreen support present.
- ✅ Alt+Enter/borderless work present.
- ✅ Win32/Winsock hook work present.
- ✅ Loader/bootstrap cleanup present.
- ✅ WASD option present but remains conservative/opt-in where applicable.
- ✅ Relay address is used for player-facing bootstrap.

# 43. Native Discord Rich Presence / PR #366

- 🔧 PR #366 donor branch is stale relative to current master and must not be merged wholesale.
- ✅ Discord local IPC implementation extracted onto a fresh branch based on current master.
- ✅ No Discord SDK DLL, bot token or OAuth secret required.
- ✅ Config toggle `DiscordRichPresence=true` added.
- ✅ Startup/stop wiring added to the current bootstrap.
- ✅ Windows IPC regression test extracted.
- 🔧 Run Windows build/test validation.
- 🔧 Merge only the clean extracted implementation.
- 🔧 Close PR #366 and delete the obsolete donor branch after successful validation.
- ⏸ Character/map/job Rich Presence details remain deferred until verified memory contracts exist.

# 44. Client visual overhaul / Phase 2

- ⏸ Login/world/character-select redesign intentionally deferred until after Kaentake review.
- ⏸ Connected panorama, branding package and related clean-client E2E remain deferred.
- 🔧 Finish structured Kaentake comparison before resuming this phase.

# 45. Client assets / WZ

- ✅ Asset audit/reference documents exist.
- 🔧 Complete canonical asset inventory and package conventions.
- 🔧 Normalize transparency/padding/anchors/frame sizes/resolution.
- 🔧 Classify replacements requiring no native change vs WZ vs native code.
- 🔧 Remove duplicate/low-quality/stale donor presentation assets deliberately.

# 46. Client branding cleanup

- 🔧 Remove player-visible Ezorsia/Yuna/legacy donor branding where inappropriate.
- 🔧 Preserve historical/upstream attribution where technically useful.
- 🔧 Audit executable/window/error/launcher/URL strings.

# 47. Launcher / patcher

- ✅ Launcher update path works.
- ✅ Live manifest/client distribution exists.
- 🟡 Verify fresh install, repair, interrupted download, corrupted file recovery and rollback behavior.
- 🟡 Verify EXE/DLL/WZ update behavior and authoritative hashes.
- 🟡 Verify user configuration is not overwritten incorrectly.

# 48. Website / CMS

- ✅ Website is Git-backed under `/opt/everleaf/web-repo`.
- ✅ Runtime state separated under `/opt/everleaf/web-state`.
- ✅ Website service healthy and public site reachable.
- ✅ Dependency install previously reported 0 vulnerabilities during migration.
- 🔧 Full page-by-page polish remains.
- 🔧 Rankings/wiki/account/mobile/error-state passes remain.
- 🔧 Security headers/CSP/rate limiting/session/admin-route review remain.
- 🟡 Backup/restore verification for mutable CMS state.

# 49. Rankings / avatar renderer

- ✅ Rankings and WZ avatar service exist.
- 🔧 Verify all jobs/equipment/NX/pets/weapons/capes/effects/unusual IDs.
- 🔧 Verify deletion/rename/class-change refresh and stale-cache handling.
- 🔧 Verify sorting/tie correctness.

# 50. Database / account administration

- ✅ Remote administration path exists.
- ✅ Class/job admin edits work without server restart.
- 🔧 Define and fix deleted-account/character residue behavior.
- 🔧 Audit orphan rows/foreign keys/least-privilege DB permissions.
- 🟡 Repeat backup/restore test.

# 51. Build / reproducibility

- ✅ Maven production package works.
- ✅ Full Maven test suite previously passed after consolidation/preservation work.
- ✅ Release deployment is commit-based.
- 🔧 Document pinned Java/Maven/Windows toolchain.
- 🔧 Standardize artifact checksums/release metadata.
- 🔧 Continue reducing manual deployment/release steps in favor of guarded workflows.

# 52. v95 / backport references

- ✅ v95 research/backport reference work exists.
- ✅ Future Henesys/Stronghold/Empress work is already incorporated.
- ⏸ No full protocol/server upgrade to v95 is planned by default.
- 🔧 Keep donor data organized and only backport intentionally selected content.

# 53. Known v83 bugs / exploit ledger

- 🔧 Maintain a permanent source-backed vulnerability/bug ledger.
- 🔧 Classify findings as exploit, dupe, corruption, crash, cosmetic or client-only.
- 🔧 Mark EverLeaf exposure and link fixes/regression coverage.

# 54. Current exploit / dupe testing priorities

- ✅ Storage basic race/failure coverage.
- ✅ Normal trade coverage.
- ✅ Merchant settlement coverage.
- ✅ Normal Cash Shop coverage.
- 🔧 Trade state-transition races.
- 🔧 Cash Shop disconnect/re-entry transfer paths.
- 🔧 Quest reward replay after disconnect/relog.
- 🔧 NPC shop extreme quantity / meso cap paths.
- 🔧 Drop/pickup and cross-system persistence races.

# 55. Release-readiness gate

Before EverLeaf is treated as broadly stable:

- 🔧 Complete core login E2E matrix.
- 🔧 Complete major class/skill runtime matrix.
- 🔧 Complete job advancement and major boss prerequisite chains.
- 🔧 Complete major boss lifecycle testing.
- 🔧 Complete NPC/portal/reactor live sweep.
- 🔧 Complete storage/trade/Cash Shop/merchant edge testing.
- 🔧 Complete two-client social-system testing.
- 🔧 Complete major PQ testing.
- 🔧 Complete launcher clean-install/repair test.
- 🔧 Complete authentication/security pass.
- 🔧 Complete backup restore rehearsal.
- 🔧 Complete long-duration load/soak last.

# 56. Priority order

1. Finish workflow-definition cleanup so routine pushes stop producing junk runs.
2. Validate and merge the clean native Discord Rich Presence extraction.
3. Close PR #366 and delete the obsolete donor branch so only the canonical line remains.
4. Keep production Git/live release synchronized after the final merge.
5. Solo-boss regression testing.
6. Full class/skill runtime matrix.
7. Job advancement + boss prerequisite quests.
8. NPC/portal/reactor live sweep.
9. Drop/pickup + transaction/exploit edge testing.
10. Client crash/windowing/disconnect testing.
11. Authentication/security source audit + targeted runtime checks.
12. Two-client party/buddy/guild/trade tests.
13. PQ multi-client testing.
14. Load/concurrency/soak testing last.
15. Then resume Kaentake review -> Phase 2 client redesign.
