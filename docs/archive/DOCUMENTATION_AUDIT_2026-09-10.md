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
- `handbook/README.md` — boundary warning for legacy lookup/reference data, including legacy command labels that must not be treated as current EverLeaf policy.

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
- `handbook/` remains separate because it is reference data, not prose documentation, and existing tooling may depend on its paths.
- Historical audit evidence remains as individual files to preserve provenance.
- Large client reverse-engineering reports remain individual archived files because combining them would make later address/provenance research harder, not easier.

## Remaining documentation gaps after consolidation

The reorganization does **not** mean every documentation item in the master checklist is complete. The audit leaves these genuine gaps visible rather than manufacturing replacement documents just to reduce the checklist:

- authoritative GM command and permission reference verified against current source;
- complete ban/appeal/moderation procedure beyond the new evidence-handling baseline;
- detailed event-operation runbook beyond the new staff baseline;
- command-level restore/recovery rehearsal runbook beyond the current production/DR guide;
- public player-facing progression/content guide for rates, level 200–250 progression, Verdant Marks, PQ Points, survivability, bosses, and PQs;
- maintained known-issues list separate from inherited/upstream `issues.txt`;
- final account-recovery/support instructions after recovery behavior is fully settled.

The new `player/INSTALLATION_AND_SUPPORT.md` does provide the installation/launcher baseline, explicit launcher-first/raw-EXE guidance, safe antivirus false-positive guidance, crash-report guidance, and gameplay/security reporting guidance. The new `staff/OPERATIONS_AND_INCIDENTS.md` provides the baseline for player-support triage, exploit/dupe response, rollback vs persistent-state remediation, evidence preservation, and incident severity.

## Merge result

The consolidation was merged into canonical `master` through PR #385 on 2026-09-10. The two temporary branch refs used during the work were subsequently fast-forwarded to the merged `master` commit so they contain no unique work; branch-ref deletion remains housekeeping only.

## Same-day follow-up completion

After the consolidation audit, the missing-document list above was worked through directly against the current source and production workflow. The original list is preserved above as the point-in-time audit result; the following records what was completed afterward:

- `docs/staff/GM_COMMANDS_AND_PERMISSIONS.md` — source-verified numeric command ranks and privilege boundaries derived from `CommandsExecutor.java` rather than legacy handbook labels.
- `docs/staff/MODERATION_AND_APPEALS.md` — ban/unban, containment, evidence, compromise, economy-abuse, and appeal procedure.
- `docs/staff/ACCOUNT_RECOVERY_PROCEDURE.md` — staff handling for the current CMS recovery queue and ownership-verification/privacy boundaries.
- `docs/staff/EVENT_OPERATIONS.md` — event preparation, operation, reward, abort, cleanup, and validation runbook.
- `docs/staff/RECOVERY_AND_RESTORE.md` — command-level service recovery, backup, immutable-release rollback, restore decision gates, and isolated restore-rehearsal procedure.
- `docs/staff/EMERGENCY_SHUTDOWN.md` — explicit emergency production stop/containment and controlled-reopen procedure.
- `docs/player/PROGRESSION_AND_CONTENT.md` — player-facing rates, level 200–250 progression, Verdant Marks, PQ Points, no-HP-washing policy, bosses/PQs, and custom-content guidance.
- `docs/player/ACCOUNT_RECOVERY.md` — accurate player-facing description of the current staff-reviewed recovery flow without claiming an automated reset-email system that does not exist.
- `docs/KNOWN_ISSUES.md` and `docs/known-issues.json` — human-readable and machine-readable current issue registers, clearly separated from inherited `archive/upstream/issues.txt`.
- `docs/README.md` and related support/operations guides were cross-linked so the new documents are part of the maintained documentation surface rather than orphan files.
- `docs/EVERLEAF_MASTER_CHECKLIST.md` Sections 42–43 were reconciled after the documents existed; the documentation-baseline items are now complete rather than merely planned.

The source review performed while writing the command reference also uncovered a **real code-level authorization defect**: `mobskill` is placed in the GM2 command package but registered through the rank-0 overload in `CommandsExecutor`, with no internal GM guard in `MobSkillCommand`. `gachalist` and `loot` use the same rank-0 registration pattern and need intended-rank review. This was **not** hidden by the documentation pass: it is tracked in both known-issues registers and promoted into the master checklist Security/Public Beta priorities. The event documentation also records the source-level `!startevent` one-argument participant-limit parsing defect.

This follow-up remained documentation/status-only. It did not modify game/runtime authorization behavior and did not deploy or restart production.

## Ongoing rule

Future documentation changes should update an existing maintained guide whenever possible. New dated audits go straight to `archive/audits/` after their conclusions are reflected in the master checklist or a maintained guide.
