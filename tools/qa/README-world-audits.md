# EverLeaf world audit gates

EverLeaf's static QA intentionally separates structural failures from review-only data differences.

The CI workflow runs:

- `tools/audit_world_integrity.py` for invalid WZ references, dead static map targets, portal-script coverage, and active Boss Rush progression integrity.
- `tools/audit_world_links.py` for named destination-portal validation and exact duplicate spawn/link records.
- `tools/qa/audit_trade_fm_integration.py` to ensure the v83 status-bar TRADE opcode remains wired to EverLeaf's guarded Free Market shortcut while legacy MTS remains disabled.
- `tools/qa/audit_ranged_whack_integration.py` to preserve the equipped-weapon-based server guard that rejects bow, crossbow, and claw close-range fallback packets before damage parsing without reintroducing the overly broad job-family guard.

World-link hard failures are mirrored to stderr in JSON mode so CI logs remain actionable even when GitHub artifact upload is unavailable or storage quotas are exhausted. Independent integration/deep-QA checks use `if: always()` so one world-content failure does not hide unrelated regressions in the same run.

Structural link failures are release gates only when the WZ data contains a concrete static target map and target portal name that cannot resolve. Ambiguous scripted, sentinel, legacy, duplicate, or reference-only differences remain review findings until evidence proves they are active player-facing defects.

Hard failures should represent conditions that cannot be healthy in the supported EverLeaf client/server data set. Ambiguous reference differences and exact duplicates that may be intentional remain review-only until runtime or authoritative reference data proves otherwise.

Empress/Cygnus expansion work is outside the EverLeaf release scope and should not be introduced to satisfy these audits.
