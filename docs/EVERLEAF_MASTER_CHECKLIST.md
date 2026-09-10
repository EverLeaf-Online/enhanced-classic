# EverLeaf Master Development Checklist

Canonical repository-backed status for EverLeafMS.

Last synchronized: **2026-09-10** after master consolidation, native Discord Rich Presence extraction/validation, live client publication, workflow-definition cleanup, website Git migration, branch cleanup, and the final canonical production rebuild.

## Current production baseline

- Repository: `EverLeaf-Online/enhanced-classic`
- Canonical branch: `master`
- Canonical master SHA: `92a646d6c42a4f5e100f8a0b2ccc6f1bfcabd45a`
- Running game release: `/opt/everleaf/releases/92a646d6c42a4f5e100f8a0b2ccc6f1bfcabd45a-34484572759-2`
- Running game release source SHA: `92a646d6c42a4f5e100f8a0b2ccc6f1bfcabd45a`
- Production source checkout: `/opt/everleaf/server`
- Active game release symlink: `/opt/everleaf/current`
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
- Canonical v95 XML baseline verified in the final deploy: `44,237` XML files.
- Live client overlay was rebuilt, verified, and published during the September 10 finalization.

The final canonical `master` was rebuilt and deployed after repository cleanup. GitHub `master`, `/opt/everleaf/server`, and the running production release are aligned to the same final source state. The deployment validated the canonical v95 content baseline, login listener, all 20 channel listeners, and every player-facing relay port.

## Status legend

- ✅ Complete / sufficiently evidenced
- 🟢 Live and verified on production
- 🟡 Needs runtime verification or final integration
- 🔧 Needs work
- ⏸ Intentionally paused/deferred

---

# 1. Repository and branch management

- ✅ `master` is the sole canonical production/development line.
- ✅ Historical `release-dev` and obsolete stacked development branches were retired.
- ✅ Useful branch-only audit/tooling work was preserved before cleanup.
- ✅ PR #380 replaced the stale native-client stack with a clean current-master integration.
- ✅ PR #366 was closed as superseded after its unique Discord work was extracted and validated.
- ✅ Final repository-maintenance automation completed branch cleanup.
- ✅ `master` is the only remaining remote branch.
- ✅ No open pull requests remain after finalization.
- ✅ Repository rules continue to require pull-request changes to protected `master`.

# 2. Production deployment and runtime

- ✅ Release-based deployment under `/opt/everleaf/releases`.
- ✅ `/opt/everleaf/current` points to the active release.
- ✅ `everleaf.service` runs the active release JAR.
- ✅ Graceful shutdown was verified across all 20 channels.
- ✅ Character persistence was observed during controlled shutdown.
- 🟢 Final canonical master `92a646d6c42a` is live and healthy.
- ✅ Final Maven package build succeeded from canonical master.
- ✅ Final production deployment validated login `8484` and channels `7575-7594`.
- ✅ Final deployment validated all player-facing relay ports on `129.159.114.146`.
- ✅ Previous release remains available for rollback.
- ✅ `/opt/everleaf/server` is synchronized to canonical `master`.
- 🟡 Perform another full VM reboot/DR exercise later as a deliberate resilience test.

# 3. Network topology and production configuration

- ✅ `HOST: 129.159.114.146`.
- ✅ `LANHOST: 129.159.114.146`.
- ✅ `LOCALHOST: 127.0.0.1`.
- ✅ `SPAWN_BOTS_ON_STARTUP: false`.
- ✅ `USE_DUEY: false`.
- ✅ `USE_ERASE_PERMIT_ON_OPENSHOP: false`.
- ✅ Oracle origin/deployment stays `132.145.141.79`.
- ✅ Player-facing game traffic uses relay `129.159.114.146`.
- ✅ Primary player/site domain is `everleafms.online`.
- ✅ Obsolete active DuckDNS checks were removed from maintained production workflows.
- 🟡 Historical migration docs may retain old hostnames/IPs where clearly labeled as history.

# 4. GitHub Actions and workflow policy

- ✅ Obsolete branch-consolidation and client-dev workflows removed.
- ✅ `run-build.yml` is manual-only.
- ✅ `everleaf-qa.yml` is manual-only.
- ✅ production monitoring is manual-only; server-side systemd timers remain the normal health path.
- ✅ production-readiness audit is manual-only.
- ✅ web data-Wiki, ranking-avatar, public-portal, and post-deploy v95 verification workflows no longer fan out via `workflow_run`.
- ✅ version bumping is explicit/manual instead of creating skipped jobs on every push.
- ✅ Discord status-monitor deployment is explicit/manual.
- ✅ heavy client build/publish operations are narrowly scoped and explicit.
- ✅ Client v2 integration, diagnostics, frame-limiter, and WASD guards are retained but converted to manual-only checks after final validation.
- ✅ Native Discord validation has a dedicated Windows workflow.
- ✅ Final repository-maintenance workflow completed successfully after handling already-absent refs correctly.
- ✅ Historical deleted-branch run cleanup was reduced substantially; further history deletion remains optional and rate-limit-sensitive.

# 5. Native client and launcher

- ✅ Current source-built Win32 client builds successfully on GitHub-hosted Windows runner.
- ✅ Client v2 integration guard passed during finalization.
- ✅ WASD guard passed during finalization.
- ✅ Frame-limiter guard passed during finalization.
- ✅ Diagnostics guard passed during finalization.
- ✅ Native Discord Rich Presence validation passed after the packaging/rebrand transform was included.
- ✅ Live client publication rebuilt and verified `dinput8.dll`, generated the managed overlay, updated the patch manifest, published to Oracle patch storage, and verified public endpoints.
- ✅ Launcher/update infrastructure remains authoritative for distributing managed client files.
- ✅ Player-facing client bootstrap uses relay `129.159.114.146`.
- ✅ Community UI preference remains the packaged default.
- ✅ Safe windowed defaults remain in place; borderless/Alt+Enter support is reversible.
- ⏸ Broader login/world/character-select visual overhaul remains deferred until Kaentake review.

# 6. Discord Rich Presence

- ✅ Native local Discord IPC implementation is now on canonical `master`.
- ✅ Uses the EverLeaf Discord application ID and local named-pipe IPC.
- ✅ Does not ship a bot token, OAuth secret, Yuna runtime, or `discord_game_sdk.dll`.
- ✅ Reconnect behavior handles Discord not running at client startup.
- ✅ Presence can be disabled with `DiscordRichPresence=false`.
- ✅ Default activity contains EverLeaf website and Discord buttons.
- ✅ IPC frame/escaping/acknowledgement tests passed on Windows runner.
- ✅ Win32 client compiled with `DiscordPresence.cpp` wired through current `dllmain.cpp`.
- 🟡 Character/job/map-specific presence remains intentionally unhooked until v83 memory contracts are verified safely.

# 7. Website / CMS

- ✅ Website is Git-backed from `/opt/everleaf/web-repo`.
- ✅ Runtime points through `/opt/everleaf/web` symlink.
- ✅ Mutable `.env` and data live outside Git in `/opt/everleaf/web-state`.
- ✅ `everleaf-web.service` is active.
- ✅ Public site uses `https://everleafms.online`.
- ✅ Rankings, Wiki, downloads, login, registration, account recovery, terms, rules, news, and help routes exist.
- ✅ Local WZ character-avatar renderer exists and rankings use it.
- 🟡 Continue page-by-page visual polish as a separate product/UI stream.
- 🟡 Continue validating stale/deleted/renamed-character ranking behavior.

# 8. Backups and disaster recovery

- ✅ OCI Object Storage backup path exists.
- ✅ Backup timer exists.
- ✅ MySQL dumps are included.
- ✅ Critical game/web/nginx/systemd/config data are included.
- ✅ Broader recovery data includes client/WZ recovery material.
- ✅ Production deployment has rollback behavior.
- ✅ Production-readiness tooling contains backup-integrity and isolated restore checks.
- ✅ Final canonical deployment completed its backup step before switching the release.
- 🟡 Periodically perform a full documented restore rehearsal rather than relying only on static backup existence.

# 9. Database and account administration

- ✅ DBeaver remote administration path is configured.
- ✅ Core account/character database is operational.
- ✅ Class changes can be performed without server restart.
- 🟡 Review account deletion semantics so character rows do not remain unexpectedly when an account is intentionally purged.
- 🟡 Continue relationship-integrity checks for inventory/equipment/quest/account records.

# 10. v95 content / Future Henesys / Stronghold / Fallen Cygnus

- ✅ Canonical full-v95 XML baseline is stored on production.
- ✅ Final deployment verified `44,237` XML files.
- ✅ Production release staging injects the canonical v95 baseline rather than relying on a partial repository WZ tree.
- ✅ Future Henesys/Henesys Ruins map set is present.
- ✅ Stronghold/Fallen Cygnus required map/mob/NPC/quest content is present in the canonical baseline.
- ✅ Production deployment validates expected map/mob/NPC/quest invariants.
- 🟡 Continue targeted gameplay regression of boss/map transitions and quest prerequisites rather than redoing completed import work.

# 11. Free Market / merchants / storage / Duey

- ✅ Free Market Cash Shop field-limit fix is live with corresponding client WZ patch.
- ✅ Regular Store Permit behavior is corrected.
- ✅ Duey is disabled in production.
- ✅ Storage fee handling is fixed and verified.
- ✅ Hired Merchant recovery/persistence/credit/quantity/snapshot hardening exists.
- ✅ PlayerShop transaction/snapshot hardening exists.
- 🟡 Continue edge-case race/disconnect testing across trade, merchant, storage, and Cash Shop transitions.

# 12. Economy / transaction exploit coverage

- ✅ Storage race/failure cases covered.
- ✅ Normal direct trade covered.
- ✅ Merchant settlement covered.
- ✅ Normal Cash Shop behavior covered.
- ✅ Timed-stack expiration/slot-cap integrity hardening is applied.
- ✅ Direct-trade untradeable-item enforcement is applied.
- ✅ Duey ownership/settlement hardening is applied even though Duey is disabled in production.
- ✅ Hired Merchant listing persistence, compensation, credit concurrency, quantity arithmetic, and snapshot integrity hardening is applied.
- ✅ PlayerShop listing source, transaction, rollback, and snapshot integrity hardening is applied.
- 🟡 Trade transition/disconnect race cases remain targeted.
- 🟡 Cash Shop disconnect transfer/re-entry remains targeted.
- 🟡 Quest reward replay after disconnect/relog remains targeted.
- 🟡 NPC shop extreme quantity and meso-cap handling remains targeted.
- 🟡 Drop/pickup races and cross-system persistence races remain under-tested.

# 13. Classes and skills

- ✅ Core class/skill integrity tooling exists.
- ✅ Evan safe creation/progression fallback remains supported.
- ✅ Evan skill data and progression transforms pass final deployment checks.
- ✅ Evan Slow/Soul Arrow and Phantom Imprint/Aran Combo fallthrough fixes are applied.
- ✅ Evan Soul Stone, Killer Wings, Critical Magic, Dragon Fury, Magic Resistance, and mastery progression fixes are applied.
- ✅ Achilles / Aran High Defense behavior was runtime-tested.
- 🟡 Run a systematic class/skill runtime matrix rather than ad-hoc spot testing.
- 🟡 Verify advancement gates and major boss prerequisite quest chains.
- ⏸ Direct Evan class-card character creation remains deferred; current beginner-to-Evan NPC path is acceptable for now.

# 14. NPC / portal / reactor / quest integrity

- ✅ Portal filename case issue `Depart_topFloor.js` is fixed.
- ✅ Static world, script-map, quest, event-manager, and active-NPC audit tooling exists.
- 🟡 Continue runtime sweep of high-risk NPCs/portals/reactors where static references cannot prove behavior.
- 🟡 Verify quest reward replay and advancement/boss prerequisite chains under disconnect/relog.

# 15. Client runtime stability

- ✅ Source-built client startup/bootstrap hardening exists.
- ✅ Race-safe dinput8 proxy logic exists.
- ✅ Crash/freeze diagnostics exist without automatic telemetry upload.
- ✅ Presentation-only FPS limiter preserves Maple's game-logic timing.
- ✅ Windowed/borderless/Alt+Enter behavior is separated from game logic.
- 🟡 Continue live crash/windowing/channel-switch/disconnect regression tests on clean client installs.
- 🟡 Validate any future Windows toolset changes against the x86 v83 client before adopting them globally.

# 16. Authentication / security

- ✅ Production web secrets are externalized.
- ✅ Password mode uses bcrypt in production.
- ✅ MySQL is expected to remain non-public.
- ✅ SSH hardening checks exist in production-readiness tooling.
- ✅ Launcher-ticket enforcement is part of current client bootstrap contract.
- 🟡 Continue source-first auth/security audit with targeted runtime confirmation only where necessary.
- 🟡 Continue exploit review for packet/state transitions that cannot be proven by static inspection alone.

# 17. Social and multi-client systems

- 🟡 Perform two-client party regression.
- 🟡 Perform buddy regression.
- 🟡 Perform guild regression.
- 🟡 Perform direct-trade transition/disconnect regression.
- 🟡 Perform PQ multi-client regression after core two-client systems are clean.

# 18. SoloMapling QA bots

- ✅ QA bot provisioning normalized.
- ✅ Bot persistence disabled.
- ✅ Empty-map travel routing implemented.
- ✅ Travel graph, potion restock, combat reachability, distant-target handling, projectile supply, loadout reapply, and untargetable-map rerouting implemented.
- ✅ Basic hunt/death/fleet/soak/class behavior was live-tested.
- ✅ Final deployment revalidated the committed SoloMapling integration guardrails.
- ⏸ Further bot pathfinding/terrain/long-soak work is intentionally parked unless the project returns to it.

# 19. Performance / concurrency

- ✅ Current production runs 20 channels.
- ✅ Health tooling verifies channel/listener topology.
- 🟡 Leave load/concurrency stress testing until gameplay, transaction, and multi-client correctness passes are complete.
- 🟡 Measure before changing JVM/runtime tuning; do not optimize from guesswork.

# 20. Phase 2 client direction

- ⏸ Review Kaentake before committing to the broader Phase 2 client overhaul.
- ⏸ Connected login/world/character panorama remains deferred.
- ⏸ Login/world/character-select branding overhaul remains deferred.
- ⏸ Direct Evan/future class-card selector remains deferred.
- ✅ Native Discord Rich Presence was separated from that deferred visual scope and shipped independently.

---

# Current priority order

1. ✅ Repository/workflow/branch cleanup complete; `master` is the only active branch.
2. ✅ Native Discord Rich Presence shipped and validated on the managed client.
3. ✅ Final canonical production rebuild/deploy complete from `92a646d6c42a`.
4. 🟡 Solo boss regression and major boss prerequisite checks.
5. 🟡 Systematic class/skill runtime matrix.
6. 🟡 Advancement and boss prerequisite quest validation.
7. 🟡 Targeted NPC/portal/reactor runtime sweep.
8. 🟡 Remaining transaction/exploit edge cases.
9. 🟡 Client crash/windowing/channel-switch/disconnect regression on clean installs.
10. 🟡 Source-first authentication/security audit plus targeted runtime checks.
11. 🟡 Two-client party/buddy/guild/trade validation.
12. 🟡 PQ multi-client validation.
13. 🟡 Website/CMS page-by-page polish and ranking edge-case cleanup.
14. 🟡 Account deletion / relational integrity cleanup.
15. 🟡 Full VM reboot and documented disaster-recovery restore rehearsal.
16. 🟡 Load/concurrency testing last.
17. ⏸ Kaentake review, then decide Phase 2 client visual direction.

## Operating rule

Treat this file as the canonical roadmap/status document. Update it when a task materially changes state; do not infer production state from old PR bodies, stale branches, or historical workflow runs.