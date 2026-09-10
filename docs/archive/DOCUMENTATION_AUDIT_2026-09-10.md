# EverLeaf Documentation Audit — 2026-09-10

## Scope

Audited the repository-level `README.md`, all files under `docs/`, the `docs/client-v2/` subfolder, the stray `docs/area_bosses/AreaBoss.js`, `handbook/`, and the top-level `deploy/` layout.

The audit found that `handbook/` is primarily large ID/reference tables and should remain separate from authored EverLeaf documentation. `deploy/` contains operational assets rather than a competing authored documentation set.

## Main problems found

1. **Status duplication:** multiple files described release/branch/content state independently of the canonical master checklist.
2. **Stale production facts:** older files referenced 44,225/44,236 XML baselines, older release SHAs, retired branches, and older origin/relay assumptions.
3. **Historical plans beside current docs:** Empress/Future Henesys files still said not to activate content that is now implemented/live.
4. **QA evidence mixed with runbooks:** dated test results and integration milestones sat beside evergreen QA instructions.
5. **Client reverse engineering mixed with maintained client docs:** donor inventories, memory-address analysis, and copycat/Yuna research looked like current client documentation.
6. **Legacy upstream notes:** inherited HeavenMS/Cosmic feature/issue/leftover/reference files could easily be mistaken for EverLeaf status.
7. **Over-splitting:** progression/rewards/survivability/NX and client-v2 diagnostics/frame-timing were split across many small overlapping files.
8. **Audience mixing:** player support, staff operations, engineering notes, and historical evidence were not clearly separated.

## New maintained structure

- `docs/README.md` — documentation index and source-of-truth rules.
- `docs/EVERLEAF_MASTER_CHECKLIST.md` — unchanged canonical roadmap/status document.
- `docs/operations/PRODUCTION_AND_RELEASE.md` — consolidated current branch/production/deployment/DR guidance.
- `docs/gameplay/PROGRESSION_AND_REWARDS.md` — consolidated post-200, Verdant, PQ Points, NX, survivability, and reward-economy policy.
- `docs/gameplay/CONTENT_AND_VALIDATION.md` — current content baseline and runtime-validation boundary.
- `docs/design/QOL_AND_FUTURE.md` — future design notes without duplicating roadmap status.
- `docs/client/ENGINEERING.md` — consolidated maintained native-client architecture/diagnostics/frame-timing guidance.
- `docs/engineering/QA_AUTOMATION.md` — maintained static/deep/runtime QA and gameplay-agent guidance.
- `docs/player/INSTALLATION_AND_SUPPORT.md` — launcher-first player support and antivirus guidance.
- `docs/staff/OPERATIONS_AND_INCIDENTS.md` — staff operations/incident baseline.

## Historical/audit files moved to `archive/audits/`

- `CLASS_SKILL_BOSS_PQ_VALIDATION.md`
- `COMMUNITY_LIVE_AUDIT_2026-09-03.md`
- `COMMUNITY_MYSQL_PARITY_FINAL_2026-09-03.md`
- `EVAN_LIVE_SKILL_EQUIVALENCE_2026-09-03.md`
- `EVENT_MINIGAME_AUDIT_2026-09-06.md`
- `LIVE_JOB_CLASS_AUDIT.md`
- `LIVE_NETWORK_DIAGNOSTIC.md`
- `LIVE_RELEASE_STATUS.md`
- `M0_BASELINE_AUDIT.md`
- `PRODUCTION_RUNTIME_SNAPSHOT.md`
- `SOLOMAPLING_LATEST_SUITE.md`
- `WORLD_CONTENT_AUDIT_STATUS.md`

## Client research moved to `archive/client-research/`

- `CLIENT_SELECTOR_DONOR_INVENTORY.md`
- `CLIENT_SELECTOR_LIVE_STRUCTURE.md`
- `CLIENT_UI_MODERNIZATION.md`
- `CLIENT_UI_OVERLAY_STRUCTURE.md`
- `CLIENT_V83_EVAN_SELECTOR_RESOLUTION.md`
- `CLIENT_V83_SELECTOR_CONTROL_ANALYSIS.md`
- `COPYCAT_CLIENT_AUDIT_20260905.md`

These remain useful for Kaentake/Phase 2 client work, but are not current runtime truth.

## Content research moved to `archive/content-research/`

- `EMPRESS_CANDIDATE_ASSET_INVENTORY.md`
- `EMPRESS_CONTENT.md`

Both predate the implemented/live Future Henesys/Stronghold/Fallen Cygnus state.

## Project-history material moved to `archive/project-history/`

- `BRANCH_CONSOLIDATION.md`
- `BRANCH_POLICY.md`
- `ENHANCED_CLASSIC.md`
- `FEATURE_LEDGER.md`
- `SOLOMAPLING_QA_INTEGRATION.md`

These preserve useful development history but contain retired branch/status assumptions.

## Source documents consolidated and retained under `archive/merged-source/`

- `AI_QA_AGENT_HUB.md`
- `DEPLOYMENT_CHECKLIST.md`
- `EVERLEAF_QOL_BACKLOG.md`
- `EVERLEAF_REWARD_ECONOMY.md`
- `HP_WASHING_REPLACEMENT.md`
- `NX_REWARDS.md`
- `PRODUCTION_CONTRACT.md`
- `PROGRESSION_200_250.md`
- `client-v2/README.md`
- `client-v2/DIAGNOSTICS.md`
- `client-v2/FRAME-LIMITER.md`

The maintained portions were rewritten into the new topic guides; the originals remain directly accessible for implementation/history details.

## Upstream/reference material moved to `archive/upstream/`

- `feature_list.md`
- `fieldlimits.txt`
- `issues.txt`
- `leftover.txt`
- `localhost_minimum_specs.txt`
- `moveactions.txt`
- `mychanges_ptbr.txt`
- `npcmarkups.txt`
- `wzchanges_gist.txt`
- `area_bosses/AreaBoss.js`

This material is inherited/reference content and is not EverLeaf's current known-issues/feature status.

## Not combined deliberately

- The master checklist remains separate because it is the authoritative roadmap/status ledger.
- `handbook/` remains separate because it is reference data, not prose documentation.
- Historical audit evidence remains as individual files to preserve provenance.
- Large client reverse-engineering reports remain individual archived files because combining them would make later address/provenance research harder, not easier.

## Ongoing rule

Future documentation changes should update an existing maintained guide whenever possible. New dated audits go straight to `archive/audits/` after their conclusions are reflected in the master checklist or a maintained guide.
