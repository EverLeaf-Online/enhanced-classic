# EverLeaf Master Development Checklist

Repository-backed working checklist for the current non-Empress EverLeaf release line.

Last synchronized: **2026-09-02** after repository consolidation, world-content hardening, reactor restoration, quest gameplay audits, and the current QoL/feature review.

## Scope and exclusions

- Primary release path: `release-dev` → `master`.
- Maintained client line: `client-dev`.
- `Community-files` is archive/reference-only and excluded from completion status.
- `empress-dev` and all Empress/Cygnus content are deferred/excluded.
- All `wz/*` work, especially `wz/v95-*`, belongs to the separate updated-WZ modernization effort and is protected from routine cleanup or unrelated rewrites.
- A repository/static audit can close structural integrity work, but live-client behavior remains `🟡` until tested in the packaged client/runtime.

## Status legend

- ✅ **Complete** — implemented and sufficiently evidenced on the maintained release path.
- 🟡 **Needs verification** — implementation exists or static integrity is proven, but live/runtime validation remains.
- 🔧 **Needs work** — incomplete, partially implemented, or still requires hardening/integration.
- 🐛 **Bug** — known defect requiring correction.
- ⏸ **Deferred** — intentionally postponed.
- 🚫 **Excluded** — intentionally outside this checklist.

---

# 1. Repository / Release Management

- ✅ `master`, `release-dev`, and `client-dev` are the intended long-lived branches.
- ✅ `Community-files` preserved as archive/reference.
- ✅ `empress-dev` preserved and excluded from the non-Empress release line.
- ✅ Repository consolidation/promotion work completed.
- ✅ Old `consolidation/*` and temporary cleanup branches retired.
- ✅ Branch lifecycle/cleanup policy documented.
- ✅ Updated-WZ/v95 work explicitly protected from cleanup.
- ✅ Required build gating and release workflows exist.
- ✅ Full Maven compile/test/package runs in the release build.
- ✅ Build manifest generation exists.
- 🟡 Continue reconciling useful historical branch-local work only when it is still intentionally unconsumed.
- 🟡 Final `release-dev` → `master` production promotion after runtime validation.
- 🟡 Confirm all production secrets/config overrides remain outside source control.

# 2. Core Server / Infrastructure

- ✅ Core server build/runtime baseline exists.
- ✅ MySQL persistence baseline exists.
- ✅ Oracle/staging deployment tooling exists.
- ✅ Backup tooling exists.
- ✅ Log rotation tooling exists.
- ✅ Disk monitoring exists.
- ✅ Production-readiness auditing exists.
- 🟡 Verify login server startup/shutdown cleanly.
- 🟡 Verify channel server startup/shutdown cleanly.
- 🟡 Verify Cash Shop server startup/shutdown cleanly.
- 🟡 Verify world/channel registration and deregistration under reconnects.
- 🟡 Verify public/LAN/localhost production topology.
- 🟡 Verify graceful recovery from DB reconnects/transient failures.
- 🟡 Run long-duration soak testing for memory leaks, deadlocks, scheduler drift, and thread growth.

# 3. Login / Accounts / Authentication

- ✅ Account/database framework exists.
- ✅ Launcher login integration framework exists.
- 🟡 Verify registration end-to-end.
- 🟡 Verify production registration policy/automatic registration setting.
- 🟡 Verify password hashing and legacy-account compatibility.
- 🟡 Verify bans, temporary bans, and IP/MAC restrictions.
- 🟡 Verify duplicate-login/session protection.
- 🟡 Verify PIC/PIN behavior if enabled.
- 🟡 Verify account persistence across restarts.
- 🟡 Verify launcher login → Play → client launch.
- 🐛 Document/mitigate players launching the raw EXE instead of the EverLeaf Launcher.

# 4. Character Creation / Persistence

- ✅ Character persistence framework exists.
- ✅ Character-persistence diagnostics exist.
- 🟡 Verify all intended starter paths.
- 🟡 Verify name validation/reserved names/duplicates.
- 🟡 Verify appearance, gender, and starting equipment against packaged client assets.
- 🟡 Verify character select/deletion/restoration policy.
- 🟡 Verify inventories, mesos, skills, quests, keybinds, buddy/guild state, pets, mounts, storage, and cooldowns survive relog/restart.
- 🟡 Verify persistence under production-like DB latency.

# 5. Classes / Jobs / Skills / Advancement

- ✅ Broad class/skill integrity auditing exists.
- ✅ Evan release-support auditing exists.
- ✅ Evan Dragon Fury hardening exists.
- ✅ Evan Magic Resistance hardening exists.
- 🟡 Verify all intended v83-era classes/job branches live.
- 🟡 Verify 1st/2nd/3rd/4th job advancement quests and NPCs live.
- 🟡 Verify AP/SP assignment/reset behavior.
- 🟡 Verify mastery/passives, buff expiration, summons, transformations, charge skills, stance, dispels, seals, and status interactions.
- 🟡 Verify projectile/melee/magic/summon formulas.
- 🟡 Verify skill/mastery books and 4th-job unlocks.
- 🟡 Verify death, EXP loss, charms, resurrection, and revival interactions.
- 🐛 Fix ranged-class melee/"whack" fallback damage/animation where the client falls back to a melee swing.

# 6. Progression / Level Cap / EXP

- ✅ Level-cap policy/framework exists for level 250.
- ✅ Post-200 progression framework exists.
- ✅ Verdant Marks framework exists.
- ✅ Weekly progression framework exists.
- ✅ Endgame tier/reward-lane framework exists.
- ✅ Progress/weekly/Marks command support exists.
- 🟡 Verify 201–249 EXP requirements are valid and production-balanced.
- 🟡 Verify 199→200 and all post-200 milestones.
- 🟡 Verify level 250 cannot become 251.
- 🟡 Verify weekly reward budgets/double-claim protection live.
- 🟡 Verify Verdant Marks cannot move through unintended trade/storage paths.
- 🟡 Verify donation systems cannot convert into progression currency/power.

# 7. HP Washing Replacement / Survivability

- ✅ Enhanced survivability policy/service exists.
- ✅ Project direction is to make traditional HP washing unnecessary.
- 🟡 Finalize and verify replacement progression for all classes/level ranges.
- 🟡 Verify legacy washed characters do not gain unintended advantages.
- 🟡 Verify survivability floors remain idempotent.
- 🟡 Verify HP/MP reset items cannot bypass balance policy.

# 8. Combat / Damage / Status Effects

- ✅ Core combat framework exists.
- 🟡 Verify weapon/magic damage formulas.
- 🟡 Verify critical hits, elemental weakness/resistance/immunity, defense, accuracy, avoidability, and level penalties.
- 🟡 Verify knockback, invulnerability, weapon/magic cancel, reflect if present, and boss immunities.
- 🟡 Verify poison, freeze, stun, seal, darkness, curse, slow, doom, dispel, seduce, and zombify-style mechanics where applicable.
- 🟡 Verify boss HP bars/phase transitions.
- 🟡 Verify party EXP/leech rules.
- 🟡 Verify death/revive inside instances and boss maps.

# 9. Maps / Portals / Reactors

- ✅ **5,238 non-Empress maps structurally audited.**
- ✅ Global map-reference audit completed with zero hard structural failures in the current release pass.
- ✅ Broken/missing portal destination audit completed.
- ✅ Named exits and script map references audited.
- ✅ Portal script filename case audited.
- ✅ Return/death-map and forced-return validation completed.
- ✅ Hidden-street transition references structurally checked.
- ✅ NPC/mob/reactor asset references audited.
- ✅ Reactor script coverage classifier added.
- ✅ Proven missing server reactor handlers restored, including Zakum prequest, Horntail maze, Romeo/Juliet, Pink Bean transition, Sharenian/GPQ, and Hidden Street/drop reactors.
- ✅ Passive vs action-bearing scriptless reactors are classified for review.
- ✅ Event/map manager disposal framework exists for instance cleanup.
- 🟡 Traverse important travel/Hidden Street chains in the packaged client.
- 🟡 Verify scripted warps/NPC travel live.
- 🟡 Verify map ownership/instance behavior for bosses/PQs.
- 🟡 Verify reactor animation/trigger behavior live.
- 🟡 Verify cleanup after clear, timeout, disconnect, and re-entry.

# 10. NPCs / Spawn Placement

- ✅ Global NPC presence/asset audit completed.
- ✅ NPC spawn coordinates and footholds audited.
- ✅ NPC roam ranges audited.
- ✅ Duplicate NPCs structurally classified.
- ✅ Active NPC script coverage audited.
- ✅ Quest-owner NPC references audited.
- ✅ Release-facing NPC integrity gate exists in CI.
- ✅ NPC audit/fix workflow infrastructure exists.
- 🟡 Visually verify NPC placement in packaged client.
- 🟡 Live-test travel, advancement, storage, shop, quest, and event NPC interactions.

# 11. Quests

- ✅ Global quest structural integrity audit completed.
- ✅ Maple Island beginner quest audit completed.
- ✅ Victoria Island quest audit completed.
- ✅ Classic mainland quest audit completed.
- ✅ Active quest content-reference audit completed.
- ✅ Scripted quest-handler audit completed.
- ✅ Quest NPC/prerequisite references audited.
- ✅ Item collection and mob/kill counter shape audited.
- ✅ EXP/item/meso/fame/skill reward/action structure audited.
- ✅ Reward quantity and overflow safety audited.
- ✅ Repeatable interval validity audited.
- ✅ Start-phase reward surfaces flagged for abandon/restart review.
- ✅ Quest gameplay-completeness audit is part of release CI.
- 🟡 Live-test repeatable/daily/weekly cooldown behavior.
- 🟡 Live-test abandon/restart exploit paths.
- 🟡 Verify scripted quest items cannot bypass restrictions through trade/storage/drop.
- 🟡 Live-test major class advancement and boss prerequisite chains.

# 12. Monsters / Spawns / Drops

- ✅ Spawn monster IDs audited against available monster data.
- ✅ Spawn coordinates/footholds audited.
- ✅ Roam ranges audited.
- ✅ Density review is surfaced by the world audit.
- ✅ Economy/global-drop audits exist.
- ✅ Ordinary global Chaos Scroll and White Scroll drop removal is implemented.
- 🟡 Verify actual respawn timing/density in live gameplay.
- 🟡 Verify elite/boss trigger behavior live.
- 🔧 Complete full mob-drop referential/parity review for missing, duplicate, impossible, and economy-breaking drops.
- 🟡 Verify meso drop ranges/global rules.
- 🟡 Verify quest-item drop conditions.
- 🟡 Verify party ownership, pickup rights, pet loot, and expiry.
- 🟡 Verify drop-rate modifiers stack safely without overflow.

# 13. Bosses / Expeditions

- ✅ Enhanced boss catalog/framework exists.
- ✅ Dedicated encounter framework exists.
- ✅ Rooted Zakum custom encounter exists.
- ✅ Boss/PQ event-manager linkage audit exists.
- ✅ Pink Bean transition reactor handler restored.
- 🟡 Audit/test all intended non-Empress bosses live.
- 🟡 Verify Zakum entry, arms/body lifecycle, drops, and reset.
- 🟡 Verify Horntail and other supported expeditions.
- 🟡 Verify expedition creation/signup/leader transfer/disconnect/rejoin/cleanup.
- 🟡 Verify entry limits and cooldowns transactionally.
- 🟡 Verify rewards cannot duplicate on reconnect/retry.
- 🚫 Empress/Cygnus boss content excluded.

# 14. Party Quests

- ✅ PQ Points persistence/service exists.
- ✅ Boss/PQ event-manager linkage audit exists.
- ✅ Relevant Romeo/Juliet and GPQ reactor handlers restored.
- 🟡 Audit/test all intended PQ stage transitions live.
- 🟡 Verify PQ Points award exactly once.
- 🟡 Verify party-size, entry, leader, timer, cleanup, reconnect, and failure-exit behavior.
- 🟡 Verify reward NPCs/exchange shops.
- 🟡 Regression-test Kerning, Ludibrium, Orbis, Henesys, Romeo & Juliet, GPQ, and other intended PQs.

# 15. Events / Minigames

- 🔧 Inventory event scripts and classify supported vs disabled.
- 🟡 Verify automated scheduling if enabled.
- 🟡 Verify event maps reset cleanly.
- 🟡 Verify minigames cannot duplicate rewards/trap characters.
- 🟡 Verify seasonal/event-only content stays disabled when inactive.

# 16. Items / Equipment / Scrolls

- ✅ Item/equipment integrity audit exists in release CI.
- ✅ Item transfer/stack integrity audit exists.
- 🟡 Verify all item IDs referenced by scripts, shops, rewards, and drops.
- 🟡 Verify equip requirements/class restrictions.
- 🟡 Verify slots, scroll success/fail, curse/destruction, Clean Slate if supported, and stat persistence.
- 🟡 Verify throwing stars/bullets and projectile consumption.
- 🟡 Verify expiration.
- 🟡 Verify untradeable/account-bound/quest flags across trade/storage/merchant/drop/Cash Shop.
- 🟡 Verify unique/equip restrictions.
- 🟡 Verify cloning/serialization cannot create malformed equips.

# 17. Pets / Mounts

- ✅ Pet Vac safety audit exists.
- 🟡 Verify pet summon/equip/hunger/closeness/commands/expiry/revive.
- 🟡 Verify pet item/meso pickup rules.
- 🟡 Verify multi-pet if enabled.
- 🟡 Verify mounts, saddles, fatigue, skills, and unlock quests.
- 🟡 Verify mount/pet state across channel change/relog.

# 18. Cash Shop / NX

- ✅ NX reward framework exists.
- ✅ NX/global-drop balance audit exists.
- 🟡 Verify Cash Shop entry/exit and character state.
- 🟡 Verify NX balances/scopes.
- 🟡 Verify gifting/wishlist/storage/purchase history if enabled.
- 🟡 Verify paid rate coupons stay disabled.
- 🟡 Verify cosmetic transfer rules.
- 🟡 Verify no P2W donation path.
- 🟡 Verify vote/reward NX idempotency.

# 19. Economy / Mesos / Custom Currencies

- ✅ Verdant Marks framework exists.
- ✅ PQ Points framework exists.
- ✅ NX reward framework exists.
- ✅ Reward-source/economy audits exist.
- ✅ Maple Leaf exchange audit exists.
- ✅ Ordinary global Chaos/White Scroll drops removed.
- 🔧 Complete full economy source/sink balance pass.
- 🟡 Verify meso cap/overflow.
- 🟡 Verify shop pricing/quantity validation.
- 🟡 Verify custom currency concurrency/anti-duplication.
- 🟡 Finalize explicit Chaos/White Scroll source policy.
- 🟡 Monitor inflation/high-value item generation under player load.

# 20. Trade / Free Market / Merchants

- ✅ Duey ownership/settlement integrity audits exist.
- ✅ Merchant recovery/persistence/seller-credit/purchase-quantity/snapshot audits exist.
- ✅ PlayerShop transaction/snapshot audits exist.
- 🟡 Verify direct trade end-to-end.
- 🟡 Verify trade cancellation/rollback/item/meso validation.
- 🔧 Make the **Trade** button take players to the Free Market as planned.
- 🟡 Verify FM entrances/exits/channel behavior.
- 🟡 Verify hired merchants/player shops live.
- 🟡 Verify merchant persistence on disconnect/restart.
- 🟡 Verify untradeable/account-bound/custom-currency restrictions.
- 🟡 Run trade/merchant race/dupe tests.

# 21. Shops / Exchanges / Crafting / Maker

- ✅ Rooted Forge framework exists.
- 🟡 Audit standard shop inventory mappings.
- 🟡 Verify buy/sell quantity, meso, inventory-space checks, and rollback.
- 🟡 Verify exchange/token shops.
- 🟡 Audit Maker/crafting if enabled.
- 🟡 Verify Rooted Forge fulfillment, persistence, stat application, retry/failure, and exploit resistance live.
- 🟡 Verify custom-material acquisition/consumption.

# 22. Gachapon / Fishing / Random Rewards

- ✅ Gachapon/reward-source audit coverage exists.
- 🟡 Verify reward pools and invalid/duplicate handling.
- 🟡 Verify ticket consumption/inventory-full rollback.
- 🔧 Decide whether fishing is supported, reworked, or disabled.
- 🟡 Verify random rewards cannot be rerolled by disconnect/packet retry.

# 23. Party / Guild / Alliance / Buddy / Fame

- 🟡 Verify party lifecycle and leader migration.
- 🟡 Verify party HP/status/map updates.
- 🟡 Verify guild creation/emblem/ranks/invite/kick/leave/contribution/disband.
- 🟡 Verify alliances if enabled.
- 🟡 Verify buddy lifecycle/capacity/offline state.
- 🟡 Verify fame limits/anti-abuse.
- 🟡 Verify cross-channel social updates.

# 24. Inventory / Storage

- ✅ Item transfer/stack integrity framework exists.
- 🟡 Verify inventory categories, slot expansion, sorting, and movement.
- 🟡 Verify storage item/meso deposit/withdraw.
- 🟡 Verify account-shared storage.
- 🟡 Verify restricted/custom items cannot bypass policy through storage.
- 🟡 Verify inventory-full/disconnect rollback.

# 25. Rankings / Website-visible Character Data

- ✅ Website rankings implementation exists.
- 🟡 Verify post-200 sorting.
- 🟡 Verify GM/test exclusions.
- 🟡 Verify stale/deleted/renamed characters.
- 🟡 Verify website exposes no sensitive account data.

# 26. Commands / GM Tools / Permissions

- ✅ EverLeaf ops command work exists.
- ✅ Progress/weekly/Marks/vote command work exists.
- 🟡 Audit player commands for intended availability.
- 🟡 Audit GM levels for every privileged command.
- 🟡 Verify commands cannot bypass progression/reward/trade/item rules.
- 🟡 Log destructive/privileged GM actions.
- 🟡 Verify malformed aliases/packets cannot access admin commands.

# 27. Custom EverLeaf Progression / Endgame Features

- ✅ Level 250.
- ✅ Post-200 progression.
- ✅ Weekly progression.
- ✅ Verdant Marks.
- ✅ Endgame reward lanes.
- ✅ Rooted content framework.
- ✅ Rooted Forge.
- ✅ Rooted materials framework.
- ✅ Rooted Zakum.
- ✅ Dedicated encounter framework.
- 🟡 Live balance, persistence, and anti-abuse validation.

# 28. Planned Boss / Endgame Features

- 🔧 Boss Codex: kills, clears, difficulty, milestones.
- 🔧 Boss Reward Boxes with controlled progression-material sources.
- 🔧 Boss Timers / cooldown tracking UI.
- 🔧 Personal lockout/reset display.
- 🔧 Reconnect to still-active boss/PQ instances with strict identity/eligibility rules.

# 29. QoL — Combat / Movement

- 🔧 Attack while moving for eligible skills while preserving intentional cast/channel locks.
- 🔧 No-breath-lock / remove unnecessary post-hit or weapon-swap friction without bypassing control states.
- 🔧 Flash Jump for every class with balanced unlock level/MP cost/animation/class exceptions.
- 🔧 Infinite Throwing Stars for normal PvE once the relevant star type is owned/equipped, preserving star identity/damage.

# 30. QoL — HP / Long-term Progression

- 🔧 Finalize no-HP-washing progression path.
- 🔧 Monster Book Ring / Quest Ring with meaningful permanent HP/stat progression.
- 🔧 Evolving Rings with defined tiers/stat ceilings/replacement rules.
- 🔧 Linked Level account progression; audit existing linked-level code/data before creating anything duplicate.

# 31. QoL — Inventory / Storage / Shops / Trading

- 🔧 Storage at any level.
- 🔧 Remote Storage / Merchant access restricted away from boss/PQ/event/instance abuse.
- 🔧 Sell All with locked/favorite/quest/cash/high-value exclusions and confirmation summary.
- 🔧 Buyback with bounded history, expiry, persistence, and anti-dupe logic.
- 🔧 Safe allowlist for droppable/tradeable NX cosmetics/convenience items; sensitive/progression items remain restricted.

# 32. QoL — Pets / Loot

- 🔧 Pet Vac as universal/earnable/progression-unlocked convenience rather than VIP-only power.
- ✅ Pet Vac safety audit exists.
- 🔧 Define range/pickup rate while preserving ownership/quest restrictions.

# 33. QoL — Bossing / PQ

- 🔧 Boss Codex.
- 🔧 Boss Reward Boxes.
- 🔧 Boss cooldown/respawn timers.
- 🔧 Reconnect to boss/PQ run with party/character/instance identity and no death/entry/loot reset exploit.

# 34. QoL — UI / Chat / Enhancements

- 🔧 Optional overlay widgets for boss info/timers, reliable DPS/combat stats, and progression/codex information.
- 🔧 Loosen overly aggressive chat spam restrictions while retaining flood/bot/packet-abuse protection.
- 🔧 Custom scrolling/enhancement review.
- 🔧 Final Chaos Scroll/White Scroll protection/source policies.
- ✅ Chaos Scroll 60% removed from ordinary global monster drops.
- ✅ White Scroll removed from ordinary global monster drops.

# 35. Client / Server Asset Parity

- ✅ Managed client source/import work exists.
- ✅ Client WZ baseline/repair tooling exists.
- ✅ Updated-WZ/v95 modernization is active in the separate protected WZ workstream.
- 🟡 Verify WZ/server IDs/scripts match in the final distributed build.
- 🟡 Verify required map/NPC/mob/item/skill assets exist in the packaged client.
- 🟡 Verify protocol/version compatibility.
- 🟡 Clean-machine parity test.

# 36. Client Bugs / Client QoL

- 🔧 Complete known-client-bug sweep against MapleEzorsia v2 references/TODOs.
- 🐛 Fix ranged whack/melee fallback visual behavior.
- 🟡 Verify resolution/window/fullscreen behavior.
- 🟡 Verify alt-tab/minimize/restore stability.
- 🟡 Verify chat/whisper/buddy/party/guild/trade UI.
- 🟡 Verify Cash Shop transitions.
- 🟡 Verify clean disconnect/crash exit.
- 🟡 Verify EverLeaf web links/buttons and login branding.

# 37. EverLeaf Branding

- ✅ EverLeaf branding work exists.
- ✅ WorldConfig/welcome branding work exists.
- 🟡 Verify **Welcome to EverLeaf** everywhere intended.
- 🟡 Verify executable/window/resource strings consistently use EverLeaf.
- 🟡 Remove remaining player-facing MapleEzorsia/Ezorsia branding where appropriate.
- 🟡 Verify installer/launcher/download naming consistency.

# 38. Launcher / Patcher / Auto-Updater

- ✅ EverLeaf launcher project exists.
- ✅ Patch service and tests exist.
- ✅ Launcher update service exists.
- ✅ Build/publish workflows exist.
- ✅ Patch manifest tooling exists.
- ✅ Installer script exists.
- 🔧 Complete production auto-update pipeline/endpoint configuration.
- 🟡 Verify launcher self-update.
- 🟡 Verify client manifest/hash validation and damaged-file repair.
- 🟡 Verify atomic interrupted-update behavior and rollback/retry.
- 🟡 Verify login/Play launches the correct executable/config.
- 🟡 Add clear handling for users launching the raw EXE.
- 🟡 Verify signing/provenance strategy.

# 39. Channels / World Capacity

- 🔧 Target approximately **8 production channels**.
- 🟡 Verify server exposes configured channel count.
- 🟡 Verify website reads live/configured channel count rather than stale hardcoded values.
- 🟡 Verify channel change across all channels.
- 🟡 Verify capacity/failure messaging.
- 🟡 Load-test multi-channel concurrency.

# 40. Website / CMS

- ✅ Public website/CMS implementation exists.
- ✅ Home, downloads, news, community, help, account, rankings, support, terms, login/register routes exist.
- ✅ Admin post-management UI exists.
- ✅ Oracle/nginx/systemd deployment tooling exists.
- ✅ Website backup/DB helper work exists.
- ✅ Major UI/UX redesign work exists.
- 🟡 Verify registration/login against production game DB.
- 🟡 Verify site/game password compatibility.
- 🟡 Verify rankings/server status/live channel count.
- 🟡 Verify download links/launcher manifests use production artifacts.
- 🟡 Verify admin auth/session/CSRF/rate-limit/security controls.
- 🟡 Verify account pages expose only safe operations.

# 41. Discord / Community

- ✅ Discord organization/bot cleanup work exists.
- ✅ Forum-aware reconciliation work exists.
- ✅ Discord deployment/operations tooling exists.
- 🟡 Verify live reporting, moderation, suggestions, and support workflows.

# 42. Database / Migrations / Backups

- ✅ Base DB/drop/shop/admin SQL exists.
- ✅ EverLeaf migration framework exists.
- ✅ Weekly progression migration exists.
- ✅ Verdant Marks migration exists.
- ✅ PQ Points migration exists.
- ✅ Rooted migration work exists.
- ✅ Backup tooling exists.
- 🟡 Test every migration from a clean baseline.
- 🟡 Test sequential upgrade from current production/staging schema.
- 🟡 Verify migration idempotency/safe failure semantics.
- 🟡 Perform backup restore drill before public beta.
- 🟡 Verify constraints/indexes/uniqueness for reward/currency systems.
- 🟡 Verify DB least privilege and no public MySQL exposure.
- 🟡 Define orphaned/deleted-account character cleanup policy.

# 43. Security / Exploit Resistance

- ✅ Extensive transaction-integrity auditing is part of CI.
- ✅ Duey hardening exists.
- ✅ Merchant hardening exists.
- ✅ PlayerShop hardening exists.
- ✅ Item transfer/stack hardening exists.
- ✅ Economy/reward audits exist.
- 🔧 Complete packet-validation audit.
- 🔧 Complete broad dupe/race-condition audit.
- 🟡 Validate item/meso/NX/currency quantities server-side.
- 🟡 Validate NPC/quest/shop/map proximity/state where required.
- 🟡 Verify packet replay cannot duplicate purchases/rewards.
- 🟡 Verify concurrent weekly/reward claims transactionally.
- 🟡 Verify trade/storage/merchant concurrency.
- 🟡 Verify malformed inventory/equip packets cannot corrupt state.
- 🟡 Verify unauthorized GM/admin commands are rejected.
- 🟡 Verify web rate limiting/session/cookie security.
- 🟡 Verify logs never expose secrets/sensitive account data.

# 44. Concurrency / Transaction Safety

- ✅ Merchant seller-credit/persistence/purchase/snapshot audits exist.
- ✅ PlayerShop transaction/snapshot audits exist.
- ✅ Duey ownership/settlement audits exist.
- 🟡 Double-claim test for weeklies/custom rewards.
- 🟡 Concurrent Verdant Marks earn/spend.
- 🟡 Concurrent PQ Points award/spend.
- 🟡 Trade + disconnect race.
- 🟡 Storage + disconnect race.
- 🟡 Merchant + restart/disconnect race live.
- 🟡 Cash Shop retry/replay.
- 🟡 Boss reward retry/disconnect.
- 🟡 DB rollback tests for failed multi-step rewards.

# 45. Logging / Monitoring / Diagnostics

- ✅ Log rotation exists.
- ✅ Disk monitoring exists.
- ✅ Character-persistence diagnostics exist.
- ✅ Production-readiness auditing exists.
- ✅ CI world/NPC/portal/quest/reactor audits exist.
- 🟡 Verify structured login/channel/DB/gameplay/reward logs.
- 🟡 Add/verify production health probes/alerts.
- 🟡 Verify log retention/disk alerts.
- 🟡 Define client crash/diagnostic collection strategy.

# 46. Automated QA / Agent Testing

- ✅ QA agent infrastructure exists.
- ✅ Static/deep QA tooling exists.
- ✅ Runtime QA tooling exists.
- ✅ Game-agent tooling exists.
- ✅ Staging probe/Windows client bridge exists.
- ✅ QA Docker/staging stack exists.
- ✅ Major release CI suite is integrated.
- ✅ Current world/content hardening passes QA + Maven compile/test/package.
- 🟡 Run automated gameplay QA against the actual packaged client/release candidate.
- 🟡 Add regression tests for every fixed exploit/critical bug.
- 🟡 Maintain a machine-readable known-issues list.

# 47. Performance / Stability

- 🟡 Soak test with realistic player counts.
- 🟡 Profile database query hotspots.
- 🟡 Profile map/mob scheduler load.
- 🟡 Test simultaneous logins/channel changes.
- 🟡 Test concurrent boss/PQ instances.
- 🟡 Test cross-channel social broadcasts.
- 🟡 Monitor GC pauses, heap, threads, sockets, DB pool, and file descriptors.
- 🟡 Establish restart/recovery procedures.

# 48. Production Hardening

- ✅ Deployment checklist/tooling exists.
- ✅ Staging deployment tooling exists.
- ✅ Oracle web deployment tooling exists.
- ✅ Production-readiness checks exist.
- 🟡 Final production release build/promotion.
- 🟡 Dedicated DB user/strong secret management.
- 🟡 Firewall/SSH hardening.
- 🟡 MySQL private-only exposure.
- 🟡 Scheduled backups and successful restore drill.
- 🟡 Monitoring/alerting/log rotation live.
- 🟡 Clean-machine client/launcher install passes.

# 49. Player Documentation

- 🔧 Definitive installation/launcher guide.
- 🔧 Clearly instruct players to launch via **EverLeaf Launcher**, not raw EXE.
- 🟡 Document account creation/recovery/support.
- 🟡 Document rates, level 250, post-200 progression, Verdant Marks, PQ Points, and custom systems.
- 🟡 Document non-P2W donation policy.
- 🟡 Document known issues/reporting.
- 🟡 Document antivirus false-positive guidance without recommending global antivirus disablement.

# 50. Staff / GM Documentation

- 🔧 GM command/permission reference.
- 🔧 Player-support procedures.
- 🔧 Rollback/economy incident procedures.
- 🔧 Ban/appeal/evidence procedures.
- 🔧 Event-operation procedures.
- 🔧 Deploy/restart/backup/restore runbook.
- 🔧 Exploit-response/emergency shutdown procedure.

# 51. Closed Alpha Readiness

- ✅ Integrated release branch builds successfully.
- ✅ Repository/static world-content baseline substantially hardened.
- 🟡 Clean client/launcher installation succeeds.
- 🟡 Invite-only account flow works.
- 🟡 Critical login/character persistence behavior verified.
- 🟡 Normal advancement/combat/maps/NPCs/quests progression playthrough succeeds.
- 🟡 Major non-Empress bosses/PQs playable or explicitly disabled.
- 🟡 Backup/logging enabled live.
- 🟡 Known-issues list published.
- 🟡 QA agents run against staging/package.

# 52. Public Beta Readiness

- 🟡 Public registration/auth hardened.
- 🟡 Website/launcher/channel integration correct.
- 🟡 Economy/source/sink review complete.
- 🟡 Exploit/dupe/concurrency pass complete.
- 🟡 Backup restore drill complete.
- 🟡 Monitoring/alerting active.
- 🟡 Donation system confirmed non-P2W.
- 🟡 Staff/support procedures ready.
- 🟡 Major client crashes/critical bugs resolved.

# 53. Public Launch Readiness

- 🟡 Critical/high-severity issues closed or consciously accepted.
- 🟡 Release is consolidated/reproducible.
- 🟡 Server/client/launcher artifacts reproducible from source/workflows.
- 🟡 Client/server assets verified from a clean install.
- 🟡 Live channel count/config verified.
- 🟡 Website/CMS/auth/rankings/status verified.
- 🟡 Economy/security/performance/load validation complete.
- 🟡 Backup/restore/rollback procedures validated.
- 🟡 Player/staff documentation published.
- 🟡 Final launch approval after beta telemetry/balance/security/operations review.

# 54. Post-Launch Operations

- 🔧 Define patch cadence/emergency hotfix process.
- 🔧 Define launcher manifest/version policy.
- 🔧 Define DB migration/release process.
- 🔧 Monitor inflation/high-value item generation.
- 🔧 Monitor crashes/disconnect/channel health.
- 🔧 Monitor suspicious trade/storage/merchant/reward behavior.
- 🔧 Maintain public changelog/known issues.
- 🔧 Schedule recurring backups/restore verification.
- 🔧 Schedule recurring security/performance/content audits.

---

# Immediate Priority Queue

1. **Live packaged-client world/content verification** — traversal, NPC placement/interaction, quest chains, boss/PQ teardown and reconnect behavior.
2. **Client QoL + known client bugs** — especially ranged whack/melee fallback, movement/combat QoL, storage/shop QoL, boss timers/codex/reconnect.
3. **Updated-WZ/client-server parity** — continue only in the protected updated-WZ workstream.
4. **Full drop/economy/source-sink balance** — including explicit rare-scroll sources.
5. **Trade/storage/Cash Shop concurrency and anti-dupe testing**.
6. **Launcher production auto-update/repair/signing path**.
7. **Clean-machine client/launcher install**.
8. **Production website/auth/rankings/status/channel integration**.
9. **Database migration + backup restore drill**.
10. **Performance/soak/load testing**.
11. **Documentation and closed-alpha operations readiness**.

# Current Completion Assessment

EverLeaf has moved beyond the earlier repository-consolidation and broad static world-content-audit stage. The maintained release line now includes strong CI coverage for economy, rewards, items, transaction safety, world data, NPCs, portals, quests, class/skill integrity, boss/PQ links, and the full Maven build.

The biggest remaining uncertainty is no longer whether the repository contains obvious broken world references; it is **live packaged-client behavior, persistence/concurrency under real runtime conditions, client QoL/bug work, final asset parity, production integration, and load/operations validation**.

A single launch-readiness percentage is still intentionally avoided until the next integrated packaged-client QA/closed-alpha run provides runtime evidence.
