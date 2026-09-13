# EverLeaf Master Development Checklist

Repository-backed working checklist for the current EverLeaf release line.

Last synchronized: **2026-09-13** after a direct live-server audit, the latest server deployment, and the Alt+Enter client hotfix. Production game runtime is healthy on source SHA `0139ded506923a05fddbc81379f1564545c480be`; login plus all 20 channels and every player-facing relay port were re-verified live. The current `master` is ahead only in client, web, and audit-tooling files, with no newer Java/server-runtime changes pending deployment.

## Current production baseline

- Primary repository: `EverLeaf-Online/enhanced-classic`
- Canonical branch: `master`
- Repository branch state: **`master` is the sole canonical line; temporary documentation refs may remain but contain no unique work**
- Open pull requests: **none**
- Current running game release source SHA: `0139ded506923a05fddbc81379f1564545c480be`
- Current running game release: `/opt/everleaf/releases/0139ded506923a05fddbc81379f1564545c480be-manual-20260913T061035Z`.
- Previous rollback release is preserved at `/opt/everleaf/releases/1d50c3aec0e615d58b24a349e84451381bc1115d-manual-20260913T060452Z`.
- Current canonical `master` is ahead of the deployed server SHA only in client, web, and audit-tooling files; no newer Java/server-runtime file changes are pending deployment.
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
- September 13 production deployment rebuilt the server JAR, staged the canonical v95 WZ tree, backed up production, switched `/opt/everleaf/current`, restarted `everleaf.service`, verified login + all 20 local channels, verified all relay ports, and recorded the deployed release.
- Live server audit on September 13 re-verified `everleaf.service`, `everleaf-web.service`, `everleaf-discord.service`, `everleaf-wz-avatar.service`, MySQL, and nginx as active; root/`/opt` disk usage was 54% with about 89 GB free.
- `everleaf-healthcheck.timer`, `everleaf-disk-monitor.timer`, and `everleaf-backup.timer` are active and their latest runs succeeded.
- Live managed client patch manifest is currently `v180-quickslot-panel-fix-20260913-5fd625532` with 38 managed files. The published `EverLeafMS.dll` SHA-256 is `3e23f5819e69737ab350352ce290f5635c50aa718c8a8d70151d8274d1e5dd37`.
- Alt+Enter stable borderless fullscreen was fixed, rebuilt, published, and then runtime-verified by the user on the live client on September 13.
- Production website home, launcher-manifest, and status endpoints returned HTTP 200 during the September 13 live audit.

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
- 🟢 Latest production deployment succeeded from `0139ded506923a05fddbc81379f1564545c480be`; the previous release is preserved for rollback.
- ✅ Comparison from deployed SHA to current `master` shows only client, web, and audit-tooling changes; no newer Java/server-runtime files are waiting for deployment.

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
- 🟢 Current release passed production restart/runtime validation.
- 🟢 September 13 live audit re-verified login server `8484`.
- 🟢 September 13 live audit re-verified all 20 channel listeners on `7575-7594`.
- 🟢 September 13 live audit re-verified all player-facing relay ports on `129.159.114.146`.
- 🟢 `everleaf.service` is active with the expected JAR from `/opt/everleaf/current`; no fatal/error/exception lines were found in the current boot journal beyond one duplicate `vote` command-registration warning.
- ✅ Disk usage is healthy at 54% used with about 89 GB free as of the September 13 audit.
- ✅ Multi-hour/day production soak has been runtime-verified on the current baseline.
- 🟡 Verify reconnect behavior under transient DB/network failures.
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
- ✅ September 13 production deployment backup stage completed successfully before release switch.
- ✅ Scheduled production backup last completed successfully at 06:18 UTC on September 13; newer web backup snapshots were also present at 07:25 UTC.
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
- ✅ Managed stock-client startup requires the launcher's one-time handoff in canonical source.
- ✅ Canonical source enforces one EverLeaf client per machine with launcher process/mutex checks plus a native lifetime mutex.
- ✅ Current staff-reviewed account recovery flow is documented for players/support.
- ✅ Registration/login against the production game database has been runtime-verified.
- 🟡 Runtime-verify launcher-only/direct-EXE rejection and single-client/race rejection on a clean player machine; the hardened launcher/client is already published.
- 🟡 If public-beta policy requires tamper-resistant proof against modified local binaries, design a server-validated launch-session protocol.
- 🟡 Verify password hashing and legacy-account compatibility across older accounts.
- 🟡 Verify bans, temporary bans, IP/MAC restrictions, and duplicate-login/session protection.
- 🟡 Verify PIC/PIN behavior if enabled.
- 🟡 Verify account persistence across restart/reconnect conditions.
- 🟡 Complete source-first authentication/security review with targeted runtime confirmation.

# 5. Character Creation / Persistence

- ✅ Character persistence framework exists.
- ✅ Character-persistence diagnostics exist.
- ✅ Beginner creation works.
- ✅ Beginner → NPC → Evan conversion works.
- ✅ Controlled graceful shutdown preserved character persistence during production testing.
- ✅ Preventive account/character relationship guard migration and read-only orphan audit exist on canonical `master`.
- ⏸ Direct modern class-card/direct Evan creation remains intentionally paused.
- 🟡 Verify name validation/reserved names/duplicates.
- 🟡 Verify character deletion/restoration policy and remaining edge cases.
- ✅ September 13 production orphan audit found **0 orphan characters**, **0 orphan character-owned inventory rows**, and **0 orphan account-owned inventory rows**.
- 🔧 The same audit found **191 orphan `inventoryequipment` rows** whose parent `inventoryitems` rows no longer exist; these are historical child-row residue and require deliberate cleanup/constraint review.
- 🟡 The account→character `ON DELETE RESTRICT / ON UPDATE RESTRICT` guard is not installed in production yet; apply and verify it after the orphan-equipment cleanup/review is handled.
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
- 🟢 Account-wide Monster Book milestone rings are live, using unique-card thresholds of 50 / 150 / 300.
- 🟢 Account-wide quest milestone rings are live, using unique completed-quest thresholds of 50 / 150 / 300.
- 🟢 Bounded evolving milestone rings are live using the existing Moon Stone, Shining Star, and Gold Heart three-tier client assets with EverLeaf-only owner markers.
- 🟢 Account Legacy linked-level progression is live: only the top four non-GM characters count, each is capped at level 200, tracked score caps at 800, and reward tiers unlock at 200 / 400 / 600.
- 🟢 `@progress milestones` exposes account progress and `@progress milestones sync [all|book|quest|legacy]` synchronizes earned rings; synchronization is idempotent, add-before-remove, refuses unsafe equipped-ring evolution, and never consumes unrelated vanilla ring copies.
- ✅ Account milestone progression is derived from existing persisted Monster Book, quest-completion, and character-level data; no new production schema migration is required.
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
- ✅ The prior 45 action-bearing scriptless-reactor findings were classified: 34 dormant/legacy assets and 11 retained-content reactors with verified event/NPC/WZ-state owners.
- 🔧 September 13 live audit found one separate WZ integrity issue: map `211070101` (Lion King's Castle — Aerial Prison) contains ten reactor spawns using ID `2112018`, but the canonical v95 `Reactor.wz` tree has no `2112018.img.xml`. No incoming WZ portal or source/script reference into that map was found, so this currently looks like unreachable legacy/import residue rather than an active travel path, but it must be reconciled instead of suppressing the audit.
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
- ✅ Quest reward replay/disconnect source audit is complete: quest state is marked completed before reward actions, preventing packet/reconnect replay duplication; the remaining crash window is potential partial/lost reward, not a dupe.
- ✅ Quest-item transfer source audit is complete across direct Trade, PlayerShop/Hired Merchant, Duey, ground drops, and same-account Storage policy.
- ✅ September 13 audit corrected a stale quest-item audit assertion from the retired `ivItem` local to the hardened locked `sourceItem` path; the live source still rejects `sourceItem == null || sourceItem.isUntradeable()`.
- 🟡 Live-test advancement quest chains.
- 🟡 Live-test boss prerequisite chains.
- 🟡 Live-test abandon/restart exploit paths.
- 🟡 Live-test repeatable/daily/weekly cooldown behavior.
- 🟡 Runtime-test process-crash/disconnect reward delivery behavior; static replay/duplication protection is already verified.
- 🟡 Runtime-fuzz quest-item transfer restrictions; static transfer gates are already verified.

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
- ✅ Boss prerequisite source cross-check completed for Zakum, Horntail, Papulatus, and Empress; Empress recruiter now requires Stronghold completion plus weekly account lockout.
- ✅ Pink Bean entry behavior is explicitly documented as a level/map-progression gate with no additional invented quest/item prerequisite; adding one remains a design decision.
- ✅ Major boss reward-table audit exists and verifies final reward-bearing IDs.
- 🟢 Papulatus controlled Chaos/White Scroll drops are corrected in the production DB to final body `8500002`; transitional `8500001` has no managed rare-scroll rows.
- 🟢 September 13 DB audit re-verified the controlled Chaos/White rows for Papulatus, Pianus, Zakum, Horntail, Pink Bean, Empress, Targa, and Scarlion.
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
- ✅ `!startevent [playerLimit]` source handling corrected: no argument defaults to 50; exactly one positive integer is accepted; invalid/extra input is rejected; regression coverage added.
- ✅ The `!startevent` limit fix is deployed in the current production game release.
- 🟡 Live-smoke the deployed `!startevent` limit fix with a controlled GM event.
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
- ✅ Normal storage use has been runtime-verified.
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
- ✅ Normal Hired Merchant flow has been runtime-verified.
- ✅ Normal PlayerShop flow has been runtime-verified.
- 🟢 PlayerShop/Hired Merchant listing-source integrity hardening is live: invalid inventory types fail closed, quantities use checked arithmetic, the exact source item is revalidated under inventory lock, stale source state rolls the listing back, and Hired Merchant persistence compensation/open-persistence gates are deployed.
- 🟡 Cancel/disconnect/channel-change races.
- 🟡 Simultaneous merchant/PlayerShop purchase races.
- 🟡 Merchant restart/recovery live test.
- 🟡 Fredrick recovery live test.
- 🟡 Restricted/custom currency transfer fuzzing.

# 24. Shops / Exchanges / Crafting / Rooted Forge

- ✅ Rooted Forge framework exists.
- ✅ Standard NPC shop inventory mapping audit is complete: **113 shops / 3,998 listings / 0 failures / 0 reviews** after correcting the one duplicate-position seed collision.
- ✅ Maker/crafting source-integrity audit is complete for recipe, ingredient, meso, level, Maker skill, reagent, output-space, serialization, and disassembly checks.
- 🟡 Maker remains non-durable across a process crash between input consumption and output insertion; this is a possible item-loss window, not a duplication path.
- 🟡 Verify buy/sell quantity, meso, inventory-space checks, and rollback live.
- 🟡 Verify extreme quantity and meso-cap handling in NPC shops.
- 🟡 Verify exchange/token shops.
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
- ✅ All 16 previously identified duplicate local Gachapon entries were removed; current audit reports zero duplicate IDs while retaining the expected 90/8/2 machine split.
- ✅ Major-boss reward-source audit is in place; controlled rare-scroll source ownership and the Papulatus corrective migration are consistent.
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
- ✅ Cash Shop transfer/re-entry and character-state return behavior have been runtime-verified.
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
- 🟢 September 13 live audit passed runtime/public-port validation for all 20 channels plus login `8484`.
- ✅ Simultaneous login/channel-change behavior has been runtime-verified.
- ✅ Full player channel switching across the configured channel set has been runtime-verified.
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
- ✅ Canonical source requires a launcher-issued one-time handoff for the managed stock client.
- ✅ Canonical source enforces one stock client per machine with `Global\EverLeafMS.Client.SingleInstance` and exclusive ticket consumption.
- ✅ Crash/freeze diagnostics exist without automatic telemetry upload.
- ✅ Presentation-only frame limiter preserves game-logic timing.
- ✅ Windowed/borderless/Alt+Enter support is separated from game logic.
- ✅ Client v2 integration guard covers the launcher-ticket and single-client native contract.
- ✅ WASD guard passed during September 10 finalization; WASD remains optional/opt-in rather than release-critical.
- ✅ Frame-limiter guard passed during September 10 finalization.
- ✅ Diagnostics guard passed during September 10 finalization.
- ✅ Source-built Win32 client compiled successfully on the GitHub-hosted Windows runner.
- ✅ Current managed client/native overlay rebuilt, packaged, published, and public-endpoint verified on September 11.
- ✅ Current launcher/native hardening is built and published.
- ✅ Native resolution-selector/HD display implementation compiled and shipped in the current managed client.
- 🟢 Alt+Enter stable borderless fullscreen was corrected to size the HWND to the full current monitor while leaving the crash-prone live Gr2D/D3D reset path disabled; the corrected client was built, published, public-endpoint verified, and then confirmed working by the user on the live client September 13.
- 🟡 Runtime-test direct EXE rejection plus second-client/race rejection on the published build.
- 🟡 Continue resolution-selector coverage across clean installs and non-default resolutions; Alt+Enter itself is now live-verified.
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
- ✅ IPC framing/escaping/acknowledgement tests passed on the published Windows baseline.
- ✅ Win32 client compiled with `DiscordPresence.cpp` wired through the current `dllmain.cpp`.
- 🟢 Basic Rich Presence code is included in the currently published managed client overlay.
- ✅ Required GMS v83 character/level/job/field contracts are pinned from the project-supplied `Angel.idb` and independently cross-checked against v83 client references.
- ✅ Canonical source samples richer activity from `CUserLocal::Update()` on Maple's game thread; the Discord IPC worker does not read Maple objects.
- ✅ Canonical source reads character name, level, job and field ID through verified getters, cross-checks local/context field IDs, and fails closed to generic activity on invalid/transitional state.
- ✅ `CWvsContext::OnLeaveGame()` clears rich activity so logout cannot leave stale character/map text behind.
- ✅ Activity revisions push changed character/job/level/map state promptly while retaining the normal Discord heartbeat.
- ✅ Source regression coverage includes EverLeaf job labels/gameplay formatting/activity revision behavior; the native Discord guard protects the pinned addresses, map cross-check and logout hook.
- ✅ Richer character/level/job/field Discord activity is built and published in the current managed client.
- 🟡 Runtime-verify login, character entry, level/job updates, map changes, channel changes, logout, reconnect and Discord reconnect behavior.
- 🟡 Final visual presence-card check on a clean player machine remains useful.

# 32. Launcher / Patcher / Auto-Updater

- ✅ EverLeaf launcher project exists.
- ✅ Patch service exists.
- ✅ Patch manifest tooling exists.
- ✅ Production patch hosting exists.
- ✅ Managed-client baseline exists.
- ✅ Launcher/update infrastructure exists.
- ✅ September 13 client publications generated the managed overlay, updated the patch manifest, published to Oracle patch storage, and verified public patch endpoints.
- 🟢 Current live patch manifest is `v180-quickslot-panel-fix-20260913-5fd625532` with 38 managed files; the public manifest endpoint returned HTTP 200 during the audit.
- ✅ Player-facing bootstrap/default game IP uses relay `129.159.114.146`.
- ✅ Launcher-only policy is documented and source-enforced for the managed stock client through the one-time handoff.
- ✅ Launcher refuses Play while an existing EverLeaf process/native client mutex is present.
- ✅ Native client holds a machine-wide single-client mutex for its lifetime and consumes the launch ticket exclusively/single-use.
- ✅ `ClientLaunchPolicyTests` cover the launcher-side single-client decision contract.
- ✅ Launcher build/tests, self-contained publish, Inno installer compile, security invariants, and portable packaging passed on the Windows runner.
- ✅ Hardened launcher/client artifacts are published.
- ✅ EverLeaf application icon is embedded in the live `EverLeaf.exe` and the public patch artifact was verified.
- 🟡 Clean-machine runtime-verify direct-EXE rejection, normal launcher launch, second-launch rejection, and rapid/race second-launch rejection.
- 🟡 Decide/implement server-validated launcher-session proof only if modified-local-client resistance is required as a public-beta security property.
- ✅ Launcher self-update has been runtime-verified.
- ✅ Damaged-file repair/hash validation has been runtime-verified.
- 🟡 Verify interrupted update atomicity/rollback/retry.
- 🟡 Verify Play launches the correct executable/config.
- 🟡 Verify signing/provenance strategy.
- ✅ Clean-machine installation has been runtime-verified.

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
- ✅ Registration/login against production game DB verified.
- ✅ Live server/channel status integration verified.
- ✅ Production download/launcher manifest links verified.
- ✅ Current production web deployment is active; `everleaf-web.service` and `everleaf-wz-avatar.service` are running.
- 🟢 September 13 audit confirmed public home, `/v1/launcher/manifest`, and status endpoints all return HTTP 200.
- 🟡 Final page-by-page visual polish, especially rankings, Wiki, and login presentation.
- 🟡 Verify rankings stale/deleted/renamed character behavior.
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
- ✅ Safe DBeaver/database administration workflow is documented in `docs/staff/DATABASE_ADMINISTRATION.md`.
- ✅ Class changes can be applied without server restart.
- ✅ Read-only account/character orphan audit exists: `tools/everleaf-ops/audit-account-character-integrity.sql`.
- ✅ Fail-closed account/character relationship migration exists using `ON DELETE RESTRICT / ON UPDATE RESTRICT` and refuses to install over dirty/unexpected relationship state.
- ✅ Migration smoke coverage includes the account/character guard, raw-delete rejection for accounts with characters, and allowed deletion of an empty account.
- ✅ Check EverLeaf Migrations #23 passed the migration suite on MySQL 8, including the account/character relationship guard coverage.
- 🟡 Test sequential upgrade from current production schema.
- 🟡 Verify migration idempotency/safe-failure behavior against the current production-shaped schema.
- 🟡 Verify constraints/indexes/uniqueness for reward/currency systems.
- 🟡 Verify least privilege and no public MySQL exposure.
- ✅ Production account/character orphan audit completed September 13: 0 orphan characters, 0 orphan character inventory rows, 0 orphan account inventory rows.
- 🔧 Production has 191 orphan `inventoryequipment` rows with missing `inventoryitems` parents (IDs span 5285–23359); clean/review these historical child rows and add the appropriate relationship protection.
- 🟡 Account→character relationship FK count is still 0 in production; deliberately apply and verify the prepared `ON DELETE RESTRICT / ON UPDATE RESTRICT` guard after review.
- 🟡 Continue relationship-integrity review for equipment/quest/social rows belonging to deleted accounts/characters.

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
- ✅ Normal storage/direct-trade/merchant/PlayerShop/Cash-Shop paths have targeted runtime evidence.
- ✅ Cash Shop transfer/re-entry has been runtime-verified.
- ✅ Canonical `master` registers `gachalist`, `loot`, and `mobskill` at GM rank 2, with a regression guard preventing rank-0 fallback.
- ✅ GM2 permission fix is deployed in the current production game release.
- ✅ Managed stock-client launcher-only/single-client enforcement is hardened and published.
- ✅ Quest-item transfer static gate was revalidated after shop source-lock hardening; the audit itself was corrected to follow the new `sourceItem` variable rather than a retired local name.
- 🟡 Live-smoke ordinary-player rejection and GM2+ access for `gachalist`, `loot`, and `mobskill`.
- 🟡 Runtime-verify the published direct-EXE/single-client/race behavior; server-backed authorization remains a separate future layer if required against modified clients.
- 🔧 Complete broad packet-validation audit.
- 🔧 Malformed packet fuzzing.
- 🔧 Broad dupe/race-condition matrix.
- 🟡 Trade transition/disconnect race cases.
- 🟡 Quest reward replay after disconnect/relog.
- 🟡 NPC shop extreme quantity and meso-cap paths.
- 🟡 Drop/pickup races and cross-system persistence races.
- 🟡 Verify quantities server-side across item/meso/NX/custom currencies.
- 🟡 Verify NPC/quest/shop/map proximity/state validation where required.
- 🟡 Continue broad unauthorized GM/admin command rejection testing beyond the corrected GM2 registrations.
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
- ✅ Native Discord Windows validation passed for the published presence build.
- ✅ Client v2 integration/WASD/frame-limiter/diagnostics guards passed during finalization.
- ✅ Heavy QA/build workflows were converted to manual-only where continuous execution was generating unnecessary runner usage.
- ✅ Maintained human-readable `docs/KNOWN_ISSUES.md` and machine-readable `docs/known-issues.json` registers exist.
- ✅ GM2 command-registration regression guard covers `gachalist`, `loot`, and `mobskill`.
- ✅ `StartEventCommandTest` covers default/custom participant limits and invalid input rejection.
- ✅ `ClientLaunchPolicyTests` cover launcher single-client allow/reject behavior and the machine-wide mutex contract.
- ✅ Manual client-v2 integration guard checks launcher-ticket enforcement, native single-client mutex enforcement, and exclusive ticket consumption.
- ✅ Consolidated feature audit treats `origin/master` as canonical for client/server/web and checks the new launcher/native guard markers.
- ✅ Richer Discord source regression coverage and native contract guards cover job/activity formatting, activity revisions, verified v83 address markers, field-ID agreement, and logout clearing.
- ✅ MySQL migration, launcher, native-client, richer Discord, packaging, and production deployment workflows have passed on actual runners for the current release line.
- ✅ September 13 live audit passed reward-source, major-boss reward-table, NPC shop, boss-prerequisite, shop-listing, Maker, and quest-reward source checks; the quest-item audit false failure was traced to a stale variable-name assertion and corrected on `master`.
- 🔧 Reactor classification currently exposes the real `2112018`/Aerial Prison missing-definition residue described in section 13; do not suppress it until the map/WZ data is reconciled.
- 🟡 Continue targeted runtime/gameplay regression where static/build CI cannot substitute for live behavior.
- 🟡 Run automated gameplay QA against the actual packaged client/release when valuable.
- 🟡 Add regression tests for every fixed exploit/critical bug.

# 39. Performance / Stability / Soak

- 🔴 Realistic concurrent player load test.
- ✅ Multi-hour/day soak test completed successfully.
- 🔴 Concurrent boss/PQ instance load.
- ✅ Simultaneous login/channel-change behavior verified.
- 🔴 Database hotspot profiling.
- 🔴 Map/mob scheduler profiling.
- 🔴 GC/heap/thread/socket/file-descriptor telemetry under load.
- 🔴 Reconnect/network-failure simulation.
- 🟡 Leave the remaining heavy load/resource stress testing until gameplay, transaction, and multi-client correctness passes are substantially complete.
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
- 🟢 September 13 audit verified the latest healthcheck and disk-monitor runs exited `0/SUCCESS`, and the backup timer remains scheduled/healthy.
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
- ✅ Clear launcher-only/raw-EXE-blocked and one-client-at-a-time guidance.
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
- ✅ Safe production database/DBeaver administration procedure: `docs/staff/DATABASE_ADMINISTRATION.md`.

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
- ✅ Production registration/login, live server/channel status integration, and download/manifest links verified.
- ✅ Multi-hour/day soak and simultaneous login/channel-change behavior verified.
- ✅ Launcher self-update, damaged-file repair, and clean-machine installation verified.
- ✅ Full player channel switching verified.
- ✅ Normal Trade, storage, Hired Merchant, PlayerShop, and Cash Shop transfer/re-entry flows verified.
- ✅ v95 server/client content baseline.
- ✅ Future Henesys/Stronghold/Fallen Cygnus implementation.
- ✅ Broad world-content structural integrity.
- ✅ Core custom progression.
- ✅ Strong server audit/test coverage.
- ✅ Substantial anti-dupe/reward/storage/merchant hardening.
- ✅ Native Discord Rich Presence, including richer character/level/job/field activity, is built and published in the current managed client.
- ✅ One canonical branch line and clean repository structure.
- ✅ Maintained player/staff documentation baseline and known-issues register.
- ✅ `gachalist`, `loot`, and `mobskill` are corrected to GM rank 2, regression-covered, and deployed to production.
- ✅ `!startevent` optional participant-limit parsing is corrected, regression-covered, and deployed to production.
- ✅ Account/character raw-delete prevention is implemented as a fail-closed migration with a read-only orphan audit.
- ✅ Launcher-only and one-client-per-machine policy is source-hardened, built, and published for the managed stock launcher/client.
- ✅ Native HD resolution/fullscreen implementation is built and published.

## Remaining closed-alpha validation

- 🟡 Clean-machine runtime-verify launcher-only direct-EXE rejection, normal launcher launch, and second-client/race rejection.
- 🟡 Runtime-verify the published richer Discord character/level/job/field activity, including logout/channel/map transitions and Discord reconnect.
- 🟢 Alt+Enter stable borderless fullscreen is live-verified by the user; continue only broader resolution/multi-monitor/minimize/restore coverage.
- 🟡 Multi-character persistence/restart test.
- 🟡 Advancement playthrough.
- 🟡 Major quest chains.
- 🟡 Boss/PQ real-client testing.
- 🟡 Explicit disconnect/race/replay transaction edge cases not covered by the verified normal paths.
- 🟡 Realistic concurrent load plus detailed DB/scheduler/resource-growth and reconnect/network-failure profiling.
- 🟡 Live-smoke the deployed GM2 command-permission and `!startevent` fixes before broad external testing.
- ✅ Production account/character orphan audit completed clean for accounts/characters themselves.
- 🔧 Clean/review the 191 orphan `inventoryequipment` child rows, then apply/verify the account→character relationship guard.

**Assessment:** EverLeaf is closed-alpha capable, but not yet public-beta hardened.

# 46. Public Beta Readiness

Main remaining blockers:

1. 🟡 Live-smoke the deployed GM2 restriction for `gachalist`, `loot`, and `mobskill`; confirm ordinary-player rejection and GM2+ access, plus controlled `!startevent` custom-limit behavior.
2. 🔧 Clean/review the 191 orphan `inventoryequipment` child rows, then apply/verify the account→character `ON DELETE RESTRICT / ON UPDATE RESTRICT` guard; the account/character orphan audit itself is already clean.
3. 🔧 Reconcile the unreachable Aerial Prison (`211070101`) reactor `2112018` references with the canonical Reactor WZ data so the reactor classification gate is clean again.
4. 🟡 Clean-machine runtime-verify the published launcher-only + single-client enforcement, including rapid/race second-launch rejection.
5. 🟡 Runtime-verify richer Discord gameplay activity and broader resolution/multi-monitor transitions; Alt+Enter fullscreen itself is already live-verified.
6. 🔴 Automated live-client/E2E coverage if we choose to make that a beta gate.
7. 🔴 Realistic concurrent-player/boss-PQ load plus DB/scheduler/resource-growth and reconnect/network-failure testing.
8. 🟡 Boss/PQ live regression matrix.
9. 🟡 Combat formula/runtime parity.
10. 🟡 Remaining explicit disconnect/replay/race transaction edge cases.
11. 🟡 Advancement/boss-prerequisite quest playthroughs.
12. 🟡 Rankings stale/deleted/renamed behavior plus final website admin/session/CSRF/rate-limit checks.
13. 🟡 Packet/admin/web security pass.
14. 🟡 Economy/boss-drop/source-sink balance.

# 47. Public Launch Readiness

- 🟡 Critical/high-severity issues closed or consciously accepted.
- ✅ Game release line consolidated into canonical `master`.
- ✅ Current server release reproducible and deployed through the guarded workflow.
- ✅ Current managed client overlay reproducible/published through the maintained client workflow.
- ✅ Production registration/login, live server/channel status integration, and download/manifest links verified.
- ✅ Clean-machine installation verified.
- 🟡 Launcher-only/single-client enforcement still requires runtime verification on the newly published hardened managed build.
- ✅ Live channel count/config verified with actual client channel switching across all channels.
- 🟡 Remaining website/CMS validation is rankings stale/deleted/renamed behavior plus final admin/session/CSRF/rate-limit checks.
- 🟡 Complete remaining economy/security/performance/load validation.
- ✅ Backup/restore/rollback foundation validated.
- ✅ Player/staff documentation baseline published and indexed.
- 🟡 Final launch approval after beta telemetry/balance/security review.

# 48. Post-Launch Operations

- ✅ Patch cadence/emergency hotfix process documented in `docs/operations/CHANGE_PATCH_AND_MIGRATION_POLICY.md`.
- ✅ Launcher manifest/version policy documented in `docs/operations/CHANGE_PATCH_AND_MIGRATION_POLICY.md`.
- ✅ DB migration/release process documented in `docs/operations/CHANGE_PATCH_AND_MIGRATION_POLICY.md` and `docs/staff/DATABASE_ADMINISTRATION.md`.
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
- ✅ Richer Discord character/level/job/field support from verified `Angel.idb` v83 contracts was built and published in the September 11 managed client; runtime gameplay verification remains.
- ✅ Old client/maintenance branches removed; repository returned to one canonical `master` line.
- ✅ September 11 production rebuild/restart deployed exact source SHA `b20fcc8c48acca3325ddb45f5daf48ea78c480a5`.
- ✅ September 11 production release validated 44,237 v95 XML files, login 8484, all 20 channels, and all player-facing relay ports.
- ✅ Documentation audit/consolidation completed and merged through PR #385.
- ✅ Maintained player installation/support, progression/content, and account-recovery guides completed.
- ✅ Maintained GM permissions, moderation/appeals, staff account-recovery, event operations, recovery/restore, emergency-shutdown, and database-administration runbooks completed.
- ✅ Maintained human-readable and machine-readable known-issues registers created and resynchronized after the September 11 rollout.
- ✅ `gachalist`, `loot`, and `mobskill` corrected to GM rank 2, regression-covered, and deployed; controlled live permission smoke remains.
- ✅ `!startevent [playerLimit]` parsing corrected, regression-covered, and deployed; controlled live custom-limit smoke remains.
- ✅ Preventive account/character integrity guard and read-only orphan audit added to canonical `master`; production audit is now complete and clean for account/character ownership, while 191 orphan equipment child rows plus guard application remain pending.
- ✅ Patch/hotfix, launcher manifest/version, and DB migration release policy documented.
- ✅ Production registration/login, live server/channel status integration, and download/manifest links runtime-verified.
- ✅ Multi-hour/day soak and simultaneous login/channel-change behavior runtime-verified.
- ✅ Launcher self-update, damaged-file repair, clean-machine installation, and full player channel switching runtime-verified.
- ✅ Normal Trade, storage, Hired Merchant, PlayerShop, and Cash Shop transfer/re-entry flows runtime-verified.
- ✅ Managed stock launcher/client hardened to require launcher handoff and block multi-client with process/mutex checks, native lifetime mutex, and exclusive single-use launch-ticket consumption; hardened artifacts are published.
- ✅ Native HD resolution/fullscreen work compiled and shipped in the current managed client.
- 🟢 Stable borderless Alt+Enter fullscreen corrected and live-verified September 13.
- ✅ Live `EverLeaf.exe` icon publication and public artifact verification completed.
- ✅ September 11 website CMS and production web deployment completed green.
- ✅ Consolidated feature audit corrected from retired `origin/client-dev` to canonical `origin/master` and extended with launcher/single-client guard markers.

# Immediate Priority Queue

1. **Live-smoke deployed command fixes** — verify ordinary-player rejection plus GM2+ access for `gachalist`, `loot`, and `mobskill`, and verify default/custom `!startevent` capacities.
2. **Production DB integrity cleanup** — review/clean the 191 orphan `inventoryequipment` rows, then apply and verify the prepared account→character `ON DELETE RESTRICT / ON UPDATE RESTRICT` guard.
3. **Aerial Prison reactor reconciliation** — resolve map `211070101`'s ten `2112018` spawns against canonical Reactor WZ data; keep the release audit failing until the residue is deliberately fixed/classified.
4. **Runtime-verify published launcher/client enforcement** — direct `EverLeaf.exe` rejection, normal launcher launch, second-client rejection, rapid/race second-launch rejection, interrupted-update handling, and crash/disconnect behavior on a clean player machine.
5. **Boss runtime regression** — Zakum, Horntail, Papulatus, Pink Bean, Fallen Cygnus/Empress, plus prerequisite/entry/death/re-entry behavior.
6. **Systematic class/skill runtime matrix** — Explorer, Cygnus, Aran, Evan; attacks, buffs, passives, summons, movement, party effects, status interactions.
7. **Advancement + boss-prerequisite quests** — live progression, repeat/abuse/disconnect paths.
8. **NPC / portal / reactor runtime sweep** — focus on high-impact travel, advancement, boss, storage/shop/event/custom paths.
9. **Transaction/exploit edge cases** — runtime crash/delivery behavior, NPC-shop extremes, drop/pickup races, cross-system persistence races, and explicit disconnect/race paths not already verified.
10. **Client runtime regression** — resolution selector, multi-monitor/minimize/restore, launcher-only/single-client enforcement, and richer Discord gameplay activity; Alt+Enter fullscreen is already live-verified.
11. **Source-first authentication/security audit** — packet/state/admin/web review with targeted live confirmation only where static inspection cannot prove behavior; decide whether server-backed launcher-session proof is required.
12. **Two-client social/transaction matrix** — party, buddy, guild, cross-channel updates, and remaining transaction edge cases using separate test machines/approved QA setup rather than player multi-client on one machine.
13. **PQ multi-client regression** — after core two-client systems are clean, using separate test machines/approved QA setup.
14. **Website rankings/admin-security final verification and page-by-page polish** — registration/login, live status, download/manifest integration, CMS CI, and production web deployment are already verified.
15. **Economy/balance pass** — post-200 pacing, boss rewards, rare scrolls, Verdant/PQ Points, meso generation/sinks, Gachapon.
16. **Remaining performance/load/network testing last** — realistic concurrent load, boss/PQ load, DB/scheduler/resource-growth profiling, and reconnect/network-failure testing; soak and simultaneous login/channel-change behavior are already verified.
17. **Kaentake review → Phase 2 client decision** — connected login/world/character panorama, broader branding/UI redesign, direct Evan/future class cards remain deferred until that review.

# Current Completion Assessment

EverLeaf has moved beyond repository consolidation, broad static-content import, the first major transaction-hardening stage, and the documentation cleanup stage. Core v95 backport work, Future Henesys/Stronghold/Fallen Cygnus, backup/DR, level-250 progression, survivability replacement, AP/SP/mastery hardening, Aran High Defense, PQ/event reward idempotency, storage settlement, Family Reputation duplication, event unregister replay, Wheel/event death bypass, native Discord Rich Presence, richer Discord character/level/job/field support, native HD display work, client publication, Git-backed website deployment, workflow cleanup, branch consolidation, player/staff runbooks, maintained known-issues documentation, the GM2 restriction for `gachalist`, `loot`, and `mobskill`, corrected `!startevent` limit parsing, the preventive account/character relationship guard/audit, and launcher-only/one-client-per-machine stock-client hardening are implemented on canonical `master`. Production registration/login, live server/channel status integration, download/manifest links, multi-hour/day soak, simultaneous login/channel-change behavior, launcher self-update, damaged-file repair, clean-machine installation, full player channel switching, normal Trade/storage/Hired Merchant/PlayerShop flows, and Cash Shop transfer/re-entry have also been runtime-verified.

The September 13 production deployment rebuilt and deployed exact server source SHA `0139ded506923a05fddbc81379f1564545c480be`; the release is healthy with the canonical 44,237-file v95 XML baseline, login server, all 20 channels, and every player-facing relay port re-verified. Current `master` is ahead only in client, web, and audit-tooling files, so there is no newer Java/server-runtime change waiting to be deployed. The live client has since been republished through newer managed-overlay versions; stable borderless Alt+Enter fullscreen is now confirmed working on the live client.

The September 13 live audit also closed the production account/character orphan question: there are 0 orphan characters and 0 orphan account/character inventory rows. It did surface two concrete cleanup items that now belong near the top of the roadmap: 191 orphan `inventoryequipment` child rows with missing parent inventory rows, and ten `2112018` reactor references in unreachable Lion King's Castle map `211070101` with no matching canonical Reactor WZ definition. The largest remaining uncertainty beyond those findings is **runtime behavior under broader multi-client gameplay and heavier load**: boss/PQ lifecycle, full class/combat parity, advancement/prerequisite quest behavior, remaining persistence/concurrency and anti-dupe race testing, launcher-only/single-client enforcement on a clean player machine, richer Discord activity, rankings/admin-security website checks, realistic concurrent load, DB/scheduler/resource-growth profiling, and reconnect/network-failure behavior. The GM2 and `!startevent` fixes are deployed but still need controlled live smoke verification.

## Operating rule

Treat this file as the canonical EverLeafMS roadmap/status document. Preserve its detailed section structure, update statuses when work materially changes state, and do not replace it with a condensed rewrite. Do not infer current production state from old PR bodies, stale branches, or historical workflow runs.