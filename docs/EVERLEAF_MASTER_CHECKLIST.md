# EverLeaf Master Development Checklist

Repository-backed working checklist for EverLeaf. This document is the source of truth for server completion work.

## Scope and exclusions

- **Included branches for implementation evidence:** `master`, `release-dev`, `client-dev`, `content-dev`, `progression-dev`, `enhanced-dev`, `qa-agent-hub`, `web-cms`, and focused feature/fix branches when relevant.
- **Excluded from completeness calculations:** `empress-dev` and all Empress content.
- **Excluded from completeness calculations:** `Community-files`.
- A feature can be **implemented somewhere** but still not be **release-ready** until it is integrated, regression-tested, and verified on the release path.

## Status legend

- ✅ **Complete** — implemented and sufficiently evidenced in the audited branch set.
- 🟡 **Needs verification** — implementation exists or legacy support is present, but end-to-end validation is still required.
- 🔧 **Needs work** — partially implemented or requires integration/hardening.
- 🐛 **Bug** — known defect requiring correction.
- ❌ **Missing** — no sufficient implementation evidence found during this audit.
- ⏸ **Deferred** — intentionally postponed.
- 🚫 **Excluded** — intentionally outside this checklist.

---

# 1. Repository / Integration / Release Management

- 🔧 Consolidate diverged EverLeaf development branches into a coherent release path.
- 🔧 Reconcile `client-dev`, `content-dev`, `progression-dev`, `enhanced-dev`, `qa-agent-hub`, and `web-cms` with `release-dev` without dropping working features.
- 🟡 Verify required build checks are green before promotion.
- 🟡 Verify the packaged build manifest matches commit, protocol, level cap, rates, and release configuration.
- 🔧 Establish a repeatable branch promotion policy: feature branch → integration/release branch → `master`.
- 🟡 Confirm all production-only secrets/config overrides stay outside source control.
- ✅ Build/release GitHub workflow infrastructure exists.
- 🚫 Ignore `Community-files` for completion status.
- 🚫 Ignore `empress-dev` and all Empress content for completion status.

# 2. Core Server / Infrastructure

- 🟡 Verify login server startup/shutdown cleanly.
- 🟡 Verify channel server startup/shutdown cleanly.
- 🟡 Verify Cash Shop server startup/shutdown cleanly.
- 🟡 Verify world/channel registration and deregistration under reconnects.
- 🔧 Standardize production runtime configuration through environment overrides.
- 🟡 Verify public/LAN/localhost host configuration for production topology.
- 🟡 Verify no server startup warnings remain unresolved.
- 🟡 Run long-duration soak testing for memory leaks, deadlocks, thread growth, and scheduler drift.
- 🟡 Verify graceful recovery from database reconnects and transient failures.

# 3. Login / Accounts / Authentication

- 🟡 Verify account registration flow end-to-end.
- 🟡 Verify public production registration policy and automatic registration setting.
- 🟡 Verify password hashing and legacy-account compatibility.
- 🟡 Verify account bans / temporary bans / IP or MAC restrictions as intended.
- 🟡 Verify duplicate-login/session protection.
- 🟡 Verify PIC/PIN behavior if enabled by the chosen client/server configuration.
- 🟡 Verify account persistence across server restarts.
- 🟡 Verify clean launcher login → Play → client launch flow.
- 🐛 Document/mitigate players launching the game EXE directly instead of using the launcher; this is primarily a user-side launch-path issue.

# 4. Character Creation / Character Persistence

- 🟡 Verify new-character creation for all intended starter paths.
- 🟡 Verify name validation, reserved names, duplicate names, and invalid character handling.
- 🟡 Verify appearance/gender/starting equipment parity with client assets.
- 🟡 Verify character select, deletion, restoration policy, and logout persistence.
- 🟡 Verify inventories, mesos, skills, quests, keybinds, buddy/guild state, pets, mounts, storage, and cooldowns survive relog/restart.
- 🟡 Verify character persistence diagnostics under production-like database latency.

# 5. Classes / Jobs / Skills / Advancement

- 🟡 Audit all intended v83-era classes and job branches available to EverLeaf.
- 🟡 Verify 1st/2nd/3rd/4th job advancement quests and NPCs.
- 🟡 Verify AP/SP assignment and reset behavior.
- 🟡 Verify mastery/passive skills and buff expiration.
- 🟡 Verify summons, transformations, charge skills, stance, dispels, seals, and status interactions.
- 🟡 Verify multi-target, projectile, melee, magic, and summon damage formulas.
- 🐛 Remove ranged-class melee fallback/"whack" damage and animation for Bowman/Assassin-style ranged classes where the client falls back to a melee swing.
- 🟡 Verify skills with custom/client-sensitive animations do not crash or desync.
- 🟡 Verify skill books/mastery books and 4th-job unlock flows.
- 🟡 Verify death, EXP loss, safety charm, resurrection, and revival interactions.

# 6. Progression / Level Cap / EXP

- ✅ Level-cap policy work exists for level 250.
- ✅ Post-200 progression framework exists.
- ✅ Verdant Marks framework exists.
- ✅ Weekly progression framework exists.
- ✅ Endgame tier/reward-lane framework exists.
- 🟡 Verify EXP requirements from 201–249 are valid, monotonic, and production-balanced.
- 🟡 Verify 199→200 and all post-200 milestones.
- 🟡 Verify level 250 cannot gain an invalid 251st level.
- 🟡 Verify `@progress`, `@weekly` / `@weeklies`, and Marks reporting in live gameplay.
- 🟡 Verify account-bound weekly reward budgets and double-claim protection.
- 🟡 Verify Verdant Marks cannot be traded/transferred through unintended paths.
- 🟡 Verify donation systems cannot convert into progression currencies.

# 7. HP Washing Replacement / Survivability

- ✅ Enhanced survivability policy/service work exists.
- 🟡 Verify replacement progression for all classes and level ranges.
- 🟡 Verify legacy washed characters do not gain unintended advantages.
- 🟡 Verify load-time survivability floors are idempotent and safe.
- 🟡 Verify HP/MP reset items and related Cash Shop behavior cannot bypass EverLeaf balance rules.

# 8. Combat / Damage / Status Effects

- 🟡 Verify weapon/magic damage formulas against intended v83 behavior plus EverLeaf changes.
- 🟡 Verify critical hits, elemental weaknesses/resists/immunities, defense, accuracy, avoidability, and level penalties.
- 🟡 Verify monster knockback, invulnerability, weapon/magic cancel, damage reflect if present, and status immunity.
- 🟡 Verify poison, freeze, stun, seal, darkness, curse, slow, doom, dispel, seduce, and zombify-style mechanics where applicable.
- 🟡 Verify boss HP bars and phase transitions.
- 🟡 Verify party EXP distribution and leech rules.
- 🟡 Verify death/revive inside instances and boss maps.

# 9. Maps / Portals / Reactors

- 🔧 Perform repository-wide map reference audit.
- 🔧 Perform portal destination audit for broken/missing links.
- 🔧 Perform reactor script/trigger audit.
- 🔧 Validate map return points, death returns, field limits, forced returns, and hidden-street transitions.
- 🟡 Verify map ownership/instance behavior for PQs and bosses.
- 🟡 Verify scripted portals and warp NPCs cannot send players to invalid maps.
- 🟡 Verify map object cleanup after instance completion or disconnect.
- ✅ Perion map reference checking workflow evidence exists.

# 10. NPCs / Spawn Placement

- 🔧 Complete full NPC presence and placement audit.
- 🐛 Fix misplaced NPCs.
- 🐛 Restore missing NPCs.
- 🟡 Verify duplicate NPCs are intentional.
- 🟡 Verify NPC scripts correspond to the correct NPC IDs/maps.
- 🟡 Verify essential travel, advancement, storage, shop, quest, and event NPCs are reachable.
- ✅ NPC reference/presence/spawn audit workflows exist.
- ✅ Automated NPC spawn-fix workflow evidence exists.

# 11. Quests

- 🔧 Audit all intended quests for start/complete conditions.
- 🟡 Verify quest NPC references and prerequisite chains.
- 🟡 Verify item collection counters and mob-kill counters.
- 🟡 Verify reward EXP/items/mesos/fame/skills.
- 🟡 Verify repeatable/daily/weekly cooldowns.
- 🟡 Verify abandoned/restarted quests do not duplicate rewards.
- 🟡 Verify scripted quest items cannot be exploited through trade/storage/drop paths.
- 🟡 Verify major class advancement and boss prerequisite quests.

# 12. Monsters / Spawns / Drops

- 🔧 Audit mob spawn data against intended map content.
- 🟡 Verify respawn timing and density.
- 🟡 Verify elite/boss spawn triggers where applicable.
- 🔧 Audit drop tables for missing, duplicate, impossible, or economy-breaking drops.
- 🟡 Verify meso drop ranges and global drop rules.
- 🟡 Verify quest-item drop conditions.
- 🟡 Verify party ownership, pickup rights, pet loot, and expiry.
- 🟡 Verify drop-rate modifiers stack correctly and cannot overflow.

# 13. Bosses / Expeditions

- 🟡 Audit all intended non-Empress bosses.
- 🟡 Verify Zakum entry, arms/body lifecycle, drops, and reset behavior.
- 🟡 Verify Horntail/other major expeditions supported by the chosen baseline.
- ✅ Enhanced boss catalog/framework exists.
- ✅ Dedicated encounter framework exists.
- ✅ Rooted Zakum custom encounter implementation exists.
- 🟡 Verify expedition creation, signup, leader transfer, disconnect/rejoin, and cleanup.
- 🟡 Verify entry limits/cooldowns are enforced transactionally.
- 🟡 Verify boss rewards cannot be duplicated by reconnect/retry.
- 🚫 Empress/Cygnus boss content excluded.

# 14. Party Quests

- 🟡 Audit all intended PQ scripts and stage transitions.
- ✅ PQ Points persistence/service work exists in `release-dev`.
- 🟡 Verify PQ point awards exactly once per eligible clear.
- 🟡 Verify lobby creation, minimum/maximum party size, entry checks, and leader handling.
- 🟡 Verify stage timers, object cleanup, reconnect behavior, and failure exits.
- 🟡 Verify reward NPCs and exchange shops.
- 🟡 Regression-test Kerning/Ludi/Orbis/Henesys/etc. PQs that are intended to be playable.

# 15. Events / Minigames

- 🔧 Inventory all event scripts and decide supported vs disabled.
- 🟡 Verify automated event scheduling if enabled.
- 🟡 Verify event maps reset cleanly.
- 🟡 Verify minigames do not duplicate rewards or trap characters.
- 🟡 Verify seasonal/event-only content is disabled when not active.

# 16. Items / Equipment / Scrolls

- 🟡 Audit all item IDs referenced by scripts, shops, rewards, and drops.
- 🟡 Verify equip requirements and class restrictions.
- 🟡 Verify upgrade slots, scroll success/fail, curse/destruction, clean slate behavior if supported, and stat persistence.
- 🟡 Verify rechargeable stars/bullets and projectile consumption.
- 🟡 Verify item expiration.
- 🟡 Verify untradeable/account-bound/quest flags across trade, storage, merchant, drop, and Cash Shop.
- 🟡 Verify unique-item/equip restrictions.
- 🟡 Verify item cloning/serialization cannot create malformed equips.

# 17. Pets / Mounts

- 🟡 Verify pet equip, summon, hunger/closeness, commands, expiry, and revive behavior.
- 🟡 Verify pet loot and meso/item pickup rules.
- 🟡 Verify multi-pet behavior if enabled.
- 🟡 Verify mounts, saddles, fatigue, skill requirements, and quest unlocks.
- 🟡 Verify mount/pet state survives channel change and relog.

# 18. Cash Shop / NX

- ✅ NX reward service/framework exists.
- 🟡 Verify Cash Shop entry/exit and character state preservation.
- 🟡 Verify NX balances and account/character scopes.
- 🟡 Verify gifting, wishlist, storage, and purchase history if enabled.
- 🟡 Verify paid rate coupons remain disabled.
- 🟡 Verify cosmetic inventory transfer rules.
- 🟡 Verify no pay-to-win donation path into progression power/currencies.
- 🟡 Verify vote/reward NX transaction idempotency.

# 19. Economy / Mesos / Currencies

- 🔧 Perform economy source/sink audit.
- 🟡 Verify meso cap/overflow handling.
- 🟡 Verify shop buy/sell prices and quantity validation.
- 🟡 Verify repair/recharge/sink systems if present.
- ✅ Verdant Marks account currency framework exists.
- ✅ PQ Points account/reward framework exists.
- 🟡 Verify all custom currencies have immutable ledgers or equivalent anti-duplication controls.
- 🟡 Verify donation rewards remain non-P2W.

# 20. Trade / Free Market / Merchants

- 🟡 Verify direct player trade end-to-end.
- 🟡 Verify trade item/meso validation and cancellation/rollback.
- 🔧 Make the **Trade** button take players to the Free Market as planned.
- 🟡 Verify Free Market entrances/exits and channel behavior.
- 🟡 Verify hired merchants/player shops if enabled.
- 🟡 Verify merchant persistence across disconnect/restart if enabled.
- 🟡 Verify untradeable/account-bound/custom-currency restrictions.
- 🟡 Run trade/merchant race-condition and duplication testing.

# 21. Shops / Exchanges / Crafting / Maker

- 🟡 Audit standard shops and shop inventory mappings.
- 🟡 Verify buy/sell quantity, meso checks, inventory-space checks, and rollback.
- 🟡 Verify exchange NPCs and token shops.
- 🟡 Audit Maker/crafting implementation if enabled.
- ✅ Rooted Forge framework exists.
- 🟡 Verify Rooted Forge fulfillment, persistence, stat application, failure/retry behavior, and exploit resistance in live gameplay.
- 🟡 Verify custom material acquisition and consumption.

# 22. Gachapon / Fishing / Reward Randomization

- 🟡 Audit Gachapon scripts and reward pools.
- ✅ Gachapon-related script/test work exists on content development path.
- 🟡 Verify duplicate/banned/invalid item handling.
- 🟡 Verify ticket consumption and inventory-full rollback.
- 🔧 Audit fishing implementation and decide whether it is supported, reworked, or disabled.
- 🟡 Verify random reward systems cannot be rerolled by disconnect/packet retry.

# 23. Party / Guild / Alliance / Buddy / Fame

- 🟡 Verify party create/invite/kick/leave/disband and leader migration.
- 🟡 Verify party HP/status/map updates.
- 🟡 Verify guild creation, emblem, rank, invite/kick/leave, contribution, and disband.
- 🟡 Verify alliance features if enabled.
- 🟡 Verify buddy add/accept/delete/capacity/offline state.
- 🟡 Verify fame daily limits and anti-abuse.
- 🟡 Verify cross-channel social updates.

# 24. Inventory / Storage

- 🟡 Verify all inventory categories, slot expansion, sorting, and movement.
- 🟡 Verify storage deposit/withdraw mesos/items.
- 🟡 Verify storage across characters on the same account.
- 🟡 Verify locked/untradeable/custom items cannot bypass restrictions via storage.
- 🟡 Verify inventory-full and disconnect rollback paths.

# 25. Rankings / Website-visible Character Data

- 🟡 Verify in-game ranking data and post-200 sorting.
- ✅ Website rankings implementation exists on `web-cms`.
- 🟡 Verify excluded GM/test accounts are handled properly.
- 🟡 Verify stale/deleted/renamed characters.
- 🟡 Verify website does not leak sensitive account fields.

# 26. Commands / GM Tools / Permissions

- 🟡 Audit all player commands for intended availability.
- 🟡 Audit GM level requirements for every privileged command.
- ✅ EverLeaf ops command work exists.
- ✅ Progress/weekly/marks/vote command work exists across progression/content branches.
- 🟡 Verify commands cannot bypass progression, reward, trade, or item restrictions.
- 🟡 Log destructive/privileged GM actions.
- 🟡 Verify admin commands are unavailable to normal players even with malformed packets/command aliases.

# 27. Client / Server Asset Parity

- ✅ Managed client source/import work exists in `client-dev`.
- ✅ Client WZ baseline/repair tooling exists.
- 🟡 Verify WZ files match server data IDs and scripts.
- 🟡 Verify map/NPC/mob/item/skill assets required by server exist in distributed client.
- 🟡 Verify protocol/version compatibility.
- 🟡 Test from a clean machine, not only the development machine.
- 🟡 Verify no server-side content references assets missing from the packaged client.

# 28. Client Bugs / QoL

- 🔧 Perform complete known-client-bug sweep against MapleEzorsia v2 baseline/issues/TODO references.
- 🐛 Fix ranged-class whack/melee fallback visual behavior where applicable.
- 🟡 Verify resolution/window/fullscreen behavior.
- 🟡 Verify alt-tab/minimize/restore stability.
- 🟡 Verify chat, whisper, buddy, party, guild, and trade UI.
- 🟡 Verify Cash Shop transitions.
- 🟡 Verify client exits cleanly after disconnect/crash.
- 🟡 Verify custom EverLeaf web links/buttons.
- 🟡 Verify intended login-layout branding.

# 29. EverLeaf Branding

- ✅ EverLeaf client branding work exists.
- ✅ `WorldConfig.java` branding/welcome changes exist on development paths.
- 🟡 Verify server welcome text displays **Welcome to EverLeaf** everywhere intended.
- 🟡 Verify executable/window/title/resource strings are consistently EverLeaf.
- 🟡 Verify legacy MapleEzorsia/Ezorsia names are removed from player-facing surfaces where legally/technically appropriate.
- 🟡 Verify installer/launcher/download page naming consistency.

# 30. Launcher / Patcher / Auto-Updater

- ✅ EverLeaf launcher project exists.
- ✅ Patch service tests exist.
- ✅ Launcher update service exists.
- ✅ Launcher build/publish workflows exist.
- ✅ Patch manifest build/test scripts exist.
- ✅ Installer script exists.
- 🔧 Complete production auto-update pipeline and endpoint configuration.
- 🟡 Verify launcher self-update.
- 🟡 Verify client file manifest/hash validation.
- 🟡 Verify damaged/missing file repair.
- 🟡 Verify atomic update behavior so interrupted patches do not corrupt the client.
- 🟡 Verify rollback/retry behavior.
- 🟡 Verify launcher login and Play button launch the correct executable/config.
- 🟡 Add clear handling/instructions for users who bypass the launcher and start the client EXE directly.
- 🟡 Verify launcher update signing/provenance strategy.

# 31. Channels / World Capacity

- 🔧 Confirm intended production channel count; current project direction is approximately **8 channels** rather than assuming the website's previous value of 3.
- 🟡 Verify game server actually exposes the configured channel count.
- 🟡 Verify website status reads live/configured channel state correctly rather than a hardcoded value.
- 🟡 Verify channel change across all configured channels.
- 🟡 Verify channel capacity limits and failure messaging.
- 🟡 Load-test multi-channel concurrency.

# 32. Website / CMS

- ✅ Web CMS implementation exists on `web-cms`.
- ✅ Public routes/pages exist for home, downloads, news, community, help, account, rankings, support, terms, login/register.
- ✅ Admin post-management route/UI exists.
- ✅ Oracle deployment, nginx, systemd, backup, and DB helper work exists.
- 🔧 Integrate current web/CMS work with the release path.
- 🟡 Verify registration/login against production game DB safely.
- 🟡 Verify password compatibility between site and game login.
- 🟡 Verify rankings and server-status data.
- 🟡 Verify status page displays the correct number of live channels.
- 🟡 Verify download links and launcher manifests point to production artifacts.
- 🟡 Verify admin auth/session/CSRF/rate-limit/security controls.
- 🟡 Verify account page exposes only safe operations.

# 33. Database / Migrations / Backups

- ✅ Base database/drop/shop/admin SQL exists.
- ✅ EverLeaf migration framework/files exist.
- ✅ Weekly progression migration exists.
- ✅ Verdant Marks migration exists.
- ✅ PQ Points migration exists.
- ✅ Rooted Forge/material/encounter/NX migration work exists across branches.
- ✅ Database backup tooling exists.
- 🟡 Test every migration from a clean baseline.
- 🟡 Test sequential upgrade from the current production/staging schema.
- 🟡 Verify migration idempotency or safe failure semantics.
- 🟡 Perform backup restore drill before public beta.
- 🟡 Verify foreign keys/indexes/unique constraints for reward and currency systems.
- 🟡 Verify database user uses least privilege and MySQL is not publicly exposed.

# 34. Security / Exploit Resistance

- 🔧 Full packet-validation audit.
- 🔧 Full dupe/race-condition audit.
- 🟡 Validate item/meso/NX/currency quantities server-side.
- 🟡 Validate NPC/quest/shop/map proximity and state server-side where required.
- 🟡 Verify packet replay cannot duplicate purchases/rewards.
- 🟡 Verify concurrent weekly/reward claims are transactional.
- 🟡 Verify trade/storage/merchant concurrency.
- 🟡 Verify malformed inventory/equip packets cannot corrupt state.
- 🟡 Verify unauthorized GM/admin commands are rejected.
- 🟡 Verify web endpoints use rate limiting and secure session/cookie settings.
- 🟡 Verify logs do not expose passwords, tokens, secrets, or sensitive account data.

# 35. Concurrency / Transaction Safety

- 🟡 Double-claim test for weeklies and custom rewards.
- 🟡 Concurrent Verdant Marks earn/spend test.
- 🟡 Concurrent PQ Points award/spend test.
- 🟡 Trade + disconnect race test.
- 🟡 Storage + disconnect race test.
- 🟡 Merchant + restart/disconnect race test if merchants are enabled.
- 🟡 Cash Shop purchase retry/replay test.
- 🟡 Boss reward retry/disconnect test.
- 🟡 Database rollback tests for failed multi-step rewards.

# 36. Logging / Monitoring / Diagnostics

- ✅ Log rotation configuration/test work exists.
- ✅ Disk-usage monitoring script exists.
- ✅ Character-persistence diagnostic workflow exists.
- ✅ Production-readiness audit workflow exists.
- 🟡 Verify structured logs for login, channel, DB, gameplay exceptions, and reward transactions.
- 🟡 Add/verify production health probes.
- 🟡 Verify log retention and disk alerts.
- 🟡 Verify crash dumps/client diagnostic collection strategy where appropriate.

# 37. Automated QA / Agent Testing

- ✅ QA agent hub branch exists.
- ✅ Static/deep QA tooling exists.
- ✅ Runtime QA tooling exists.
- ✅ Game-agent tooling exists.
- ✅ Staging probe and Windows client bridge exist.
- ✅ QA Docker/staging stack exists.
- 🔧 Integrate QA suite into release branch/CI.
- 🟡 Run QA suite against the actual integrated release build.
- 🟡 Add regression cases for every fixed exploit/critical bug.
- 🟡 Maintain a machine-readable known-issues list for automated checks.

# 38. Performance / Stability

- 🟡 Soak test with realistic player counts.
- 🟡 Profile database query hotspots.
- 🟡 Profile map/mob scheduler load.
- 🟡 Test many simultaneous logins/channel changes.
- 🟡 Test boss/PQ instance creation at concurrency.
- 🟡 Test guild/party/buddy broadcasts across channels.
- 🟡 Monitor GC pauses, heap growth, thread count, socket count, DB pool exhaustion, and file descriptors.
- 🟡 Establish restart/recovery procedures.

# 39. Deployment / Production Hardening

- ✅ Deployment checklist exists.
- ✅ Staging deployment tooling exists on development branches.
- ✅ Web Oracle deployment tooling exists.
- 🟡 Production build check green.
- 🟡 Dedicated DB user configured.
- 🟡 Strong DB password outside repository.
- 🟡 Firewall exposes only required ports.
- 🟡 SSH key authentication and hardened server access.
- 🟡 MySQL not publicly exposed.
- 🟡 Backups scheduled and restore-tested.
- 🟡 Monitoring/log rotation enabled.
- 🟡 Clean-machine client/launcher install test passes.

# 40. Player Documentation

- 🔧 Create definitive installation/launcher guide.
- 🔧 Clearly tell players to launch through **EverLeaf Launcher**, not the raw client EXE.
- 🟡 Document account creation and password recovery/support flow.
- 🟡 Document rates, level cap, progression, Verdant Marks, PQ Points, and major custom systems.
- 🟡 Document non-P2W donation policy.
- 🟡 Document known issues and reporting process.
- 🟡 Document antivirus false-positive guidance without telling players to disable antivirus globally.

# 41. Staff / GM Documentation

- 🔧 Create GM command and permission reference.
- 🔧 Create player-support procedures.
- 🔧 Create rollback/economy incident procedures.
- 🔧 Create ban/appeal/evidence handling procedures.
- 🔧 Create event operation procedures.
- 🔧 Create deployment/restart/backup/restore runbook.
- 🔧 Create exploit-response and emergency shutdown procedure.

# 42. Closed Alpha Readiness

- 🟡 Integrated release branch builds successfully.
- 🟡 Client/launcher clean install succeeds.
- 🟡 Invite-only account flow works.
- 🟡 Critical login/character persistence bugs resolved.
- 🟡 Core advancement/combat/maps/NPCs/quests function for normal progression.
- 🟡 Major non-Empress bosses/PQs are playable or explicitly disabled.
- 🟡 Backup and logging enabled.
- 🟡 Known-issues list published to testers.
- 🟡 QA agent suite running against staging.

# 43. Public Beta Readiness

- 🟡 Public registration/auth hardened.
- 🟡 Website/launcher/channel status integration correct.
- 🟡 Economy/source/sink review complete.
- 🟡 Exploit/dupe/concurrency pass complete.
- 🟡 Backup restore drill complete.
- 🟡 Monitoring and alerting active.
- 🟡 Donation system confirmed non-P2W.
- 🟡 Staff/support procedures ready.
- 🟡 Major known client crashes resolved.

# 44. Public Launch Readiness

- 🟡 All critical/high-severity issues closed or consciously accepted.
- 🟡 Release branch consolidated and reproducible.
- 🟡 Production build and launcher artifacts reproducible from source/workflows.
- 🟡 Client/server assets verified from a clean install.
- 🟡 Live channel count/configuration verified.
- 🟡 Website/CMS/auth/rankings/status verified.
- 🟡 Economy/security/performance/load validation complete.
- 🟡 Backup/restore/rollback procedures validated.
- 🟡 Player and staff documentation published.
- 🟡 Launch owner approval after beta telemetry, balance, security, operational cost, and legal-risk review.

# 45. Post-Launch Operations

- 🔧 Define patch cadence and emergency hotfix process.
- 🔧 Define launcher manifest/version policy.
- 🔧 Define database migration/release process.
- 🔧 Monitor economy inflation and high-value item generation.
- 🔧 Monitor crashes/disconnect rates and channel health.
- 🔧 Monitor suspicious trade/storage/merchant/reward behavior.
- 🔧 Maintain public known-issues/changelog.
- 🔧 Schedule recurring backups and restore verification.
- 🔧 Schedule recurring security, performance, and content audits.

---

# Immediate Priority Queue

1. **Branch consolidation/integration plan** — current functionality is fragmented across diverged branches.
2. **Build + clean-install baseline** — integrated server, launcher, client, and web stack must build and run together.
3. **NPC/map/portal/reactor/quest audit** — resolve missing/misplaced/broken world content.
4. **Class/skill/combat regression audit** — including ranged whack/melee fallback bug.
5. **Launcher production auto-update + repair path** — ensure launcher is the canonical player entry point.
6. **Correct channel count everywhere** — target configuration around 8 channels and make website reflect the live server rather than a stale/hardcoded count.
7. **Trade → Free Market QoL change**.
8. **Boss/PQ/event regression pass excluding Empress**.
9. **Economy/security/dupe/concurrency pass**.
10. **Run QA-agent suite against integrated staging build**.
11. **Closed alpha clean-machine test**.

# Current Completion Assessment

A precise percentage is intentionally **not** assigned yet. The audit shows substantial implementation across multiple branches, including launcher/updater work, client management, web CMS, post-200 progression, custom currencies, enhanced encounters, Rooted Forge/Rooted Zakum, QA automation, migrations, deployment tooling, and release checks. However, several of these branches have materially diverged from one another. Until they are reconciled into one integrated release candidate and the checklist is validated against runtime tests, counting branch-local implementations as fully complete would overstate launch readiness.

The next meaningful percentage should be calculated only after branch consolidation and the first integrated QA run.