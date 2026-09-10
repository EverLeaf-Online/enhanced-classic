# EverLeaf Documentation

This directory contains the maintained documentation for EverLeafMS.

## Source-of-truth order

1. [`EVERLEAF_MASTER_CHECKLIST.md`](EVERLEAF_MASTER_CHECKLIST.md) — authoritative roadmap, implementation status, production baseline, and priority queue.
2. Maintained topic guides below — current policy, operating guidance, and technical design.
3. [`archive/`](archive/) — dated audits, superseded plans, donor research, and historical evidence. Archive material is **not** a statement of current production state.
4. [`../handbook/`](../handbook/) — large upstream/reference ID tables and protocol/game-data references. These are reference data, not EverLeaf status documents. See [`../handbook/README.md`](../handbook/README.md) before using them; legacy command labels/listings there do not define current EverLeaf permissions or monetization policy.

## Maintained documentation

### Operations

- [`operations/PRODUCTION_AND_RELEASE.md`](operations/PRODUCTION_AND_RELEASE.md) — canonical production topology, release policy, deployment gates, rollback, backup, and operational checks.

### Gameplay and economy

- [`gameplay/PROGRESSION_AND_REWARDS.md`](gameplay/PROGRESSION_AND_REWARDS.md) — level 200–250 progression, Verdant Marks, PQ Points, NX rewards, survivability/no-HP-washing policy, and reward-economy rules.
- [`gameplay/CONTENT_AND_VALIDATION.md`](gameplay/CONTENT_AND_VALIDATION.md) — Future Henesys/Stronghold/Fallen Cygnus content state and the remaining runtime validation boundary.
- [`design/QOL_AND_FUTURE.md`](design/QOL_AND_FUTURE.md) — design notes for future QoL work. This is not a status tracker; implementation status belongs in the master checklist.

### Client and QA engineering

- [`client/ENGINEERING.md`](client/ENGINEERING.md) — current native v83 client architecture, diagnostics, frame timing, launcher boundary, and deferred Phase 2 UI scope.
- [`engineering/QA_AUTOMATION.md`](engineering/QA_AUTOMATION.md) — static/deep/runtime QA tooling and the parked SoloMapling gameplay-agent layer.

### Player and staff

- [`player/INSTALLATION_AND_SUPPORT.md`](player/INSTALLATION_AND_SUPPORT.md) — launcher-first installation/support guidance and antivirus false-positive handling.
- [`staff/OPERATIONS_AND_INCIDENTS.md`](staff/OPERATIONS_AND_INCIDENTS.md) — staff-facing operational, incident, evidence-preservation, rollback, and support principles.

## Documentation maintenance rules

- Do not create another roadmap/status file. Update `EVERLEAF_MASTER_CHECKLIST.md` when project state changes.
- Do not put dated live snapshots beside maintained docs. Put evidence captures under `archive/audits/`.
- Do not let donor/reverse-engineering research masquerade as production behavior. Put it under an appropriate archive research folder.
- Keep player-facing guidance separate from staff/production procedures.
- Keep implementation details only when they remain useful for maintaining the current system; archive superseded implementation plans.
- When moving or replacing a maintained document, update repository links in the same change.

See [`archive/DOCUMENTATION_AUDIT_2026-09-10.md`](archive/DOCUMENTATION_AUDIT_2026-09-10.md) for the consolidation audit that established this structure.
