# EverLeaf Documentation

This directory contains the maintained documentation for EverLeafMS.

## Source-of-truth order

1. [`EVERLEAF_MASTER_CHECKLIST.md`](EVERLEAF_MASTER_CHECKLIST.md) — authoritative roadmap, implementation status, production baseline, and priority queue.
2. Maintained topic guides below — current policy, operating guidance, and technical design.
3. [`KNOWN_ISSUES.md`](KNOWN_ISSUES.md) — current human-readable confirmed defects, user-visible limitations, and unresolved validation risks; [`known-issues.json`](known-issues.json) is the machine-readable companion.
4. [`archive/`](archive/) — dated audits, superseded plans, donor research, and historical evidence. Archive material is **not** a statement of current production state.
5. [`../handbook/`](../handbook/) — large upstream/reference ID tables and protocol/game-data references. These are reference data, not EverLeaf status documents. See [`../handbook/README.md`](../handbook/README.md) before using them; legacy command labels/listings there do not define current EverLeaf permissions or monetization policy.

## Maintained documentation

### Operations

- [`operations/PRODUCTION_AND_RELEASE.md`](operations/PRODUCTION_AND_RELEASE.md) — canonical production topology, release policy, deployment gates, rollback, backup, and operational checks.
- [`operations/CHANGE_PATCH_AND_MIGRATION_POLICY.md`](operations/CHANGE_PATCH_AND_MIGRATION_POLICY.md) — routine patch cadence, emergency hotfix flow, managed-client/launcher manifest versioning, coordinated release surfaces, and database migration release policy.

### Gameplay and economy

- [`gameplay/PROGRESSION_AND_REWARDS.md`](gameplay/PROGRESSION_AND_REWARDS.md) — internal/maintainer design for level 200–250 progression, Verdant Marks, PQ Points, NX rewards, survivability/no-HP-washing policy, and reward-economy rules.
- [`gameplay/CONTENT_AND_VALIDATION.md`](gameplay/CONTENT_AND_VALIDATION.md) — Future Henesys/Stronghold/Fallen Cygnus content state and the remaining runtime validation boundary.
- [`design/QOL_AND_FUTURE.md`](design/QOL_AND_FUTURE.md) — design notes for future QoL work. This is not a status tracker; implementation status belongs in the master checklist.

### Client and QA engineering

- [`client/ENGINEERING.md`](client/ENGINEERING.md) — current native v83 client architecture, diagnostics, frame timing, launcher boundary, and deferred Phase 2 UI scope.
- [`engineering/QA_AUTOMATION.md`](engineering/QA_AUTOMATION.md) — static/deep/runtime QA tooling and the parked SoloMapling gameplay-agent layer.

### Player documentation

- [`player/INSTALLATION_AND_SUPPORT.md`](player/INSTALLATION_AND_SUPPORT.md) — launcher-first installation/support guidance, crash reporting, and antivirus false-positive handling.
- [`player/PROGRESSION_AND_CONTENT.md`](player/PROGRESSION_AND_CONTENT.md) — player-facing rates, level 200–250 progression, Verdant Marks, PQ Points, survivability/no-HP-washing policy, bosses/PQs, and major custom content.
- [`player/ACCOUNT_RECOVERY.md`](player/ACCOUNT_RECOVERY.md) — current staff-reviewed account-recovery flow, what players should provide, and what secrets they should never send.

### Staff documentation

- [`staff/OPERATIONS_AND_INCIDENTS.md`](staff/OPERATIONS_AND_INCIDENTS.md) — staff-facing operational, incident, evidence-preservation, rollback, and support principles.
- [`staff/GM_COMMANDS_AND_PERMISSIONS.md`](staff/GM_COMMANDS_AND_PERMISSIONS.md) — source-verified numeric GM command ranks and operational restrictions; replaces legacy handbook role labels as the permission reference.
- [`staff/MODERATION_AND_APPEALS.md`](staff/MODERATION_AND_APPEALS.md) — ban, unban, containment, evidence, compromise, and appeal procedure.
- [`staff/ACCOUNT_RECOVERY_PROCEDURE.md`](staff/ACCOUNT_RECOVERY_PROCEDURE.md) — staff workflow for reviewing the current CMS recovery queue, ownership verification boundaries, status transitions, compromise cases, and audit trail.
- [`staff/DATABASE_ADMINISTRATION.md`](staff/DATABASE_ADMINISTRATION.md) — safe DBeaver/private-tunnel administration, read-only inspection, transactional corrections, migration application, deletion/economy safeguards, and credential hygiene.
- [`staff/EVENT_OPERATIONS.md`](staff/EVENT_OPERATIONS.md) — joinable GM/classic event preparation, execution, rewards, abort, cleanup, and validation procedure.
- [`staff/RECOVERY_AND_RESTORE.md`](staff/RECOVERY_AND_RESTORE.md) — command-level service recovery, backup, release rollback, database-restore decision gates, and restore rehearsal procedure.
- [`staff/EMERGENCY_SHUTDOWN.md`](staff/EMERGENCY_SHUTDOWN.md) — emergency stop/containment, evidence preservation, backup, and controlled reopen procedure for incidents where continued writes are unsafe.

## Documentation maintenance rules

- Do not create another roadmap/status file. Update `EVERLEAF_MASTER_CHECKLIST.md` when project state changes.
- Keep `KNOWN_ISSUES.md` and `known-issues.json` synchronized; neither replaces the roadmap.
- Do not put dated live snapshots beside maintained docs. Put evidence captures under `archive/audits/`.
- Do not let donor/reverse-engineering research masquerade as production behavior. Put it under an appropriate archive research folder.
- Keep player-facing guidance separate from staff/production procedures.
- Keep implementation details only when they remain useful for maintaining the current system; archive superseded implementation plans.
- When moving or replacing a maintained document, update repository links in the same change.
- When command registration changes, re-audit `staff/GM_COMMANDS_AND_PERMISSIONS.md` against `CommandsExecutor.java`.
- When patch/launcher/migration behavior changes, update `operations/CHANGE_PATCH_AND_MIGRATION_POLICY.md` in the same change.

The missing-document follow-up from the September 10 audit is complete. The original gap list and same-day completion record are preserved in [`archive/DOCUMENTATION_AUDIT_2026-09-10.md`](archive/DOCUMENTATION_AUDIT_2026-09-10.md). Any remaining red/yellow items in the master checklist are implementation, runtime-validation, security, balance, or operations work rather than missing baseline documentation.
