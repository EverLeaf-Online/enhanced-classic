# EverLeaf world audit gates

EverLeaf's static QA intentionally separates structural failures from review-only data differences.

The CI workflow runs:

- `tools/audit_world_integrity.py` for invalid WZ references, dead static map targets, portal-script coverage, and active Boss Rush progression integrity.
- `tools/audit_world_links.py` for named destination-portal validation and exact duplicate spawn/link records.
- `tools/qa/audit_trade_fm_integration.py` to ensure the v83 status-bar TRADE opcode remains wired to EverLeaf's guarded Free Market shortcut while legacy MTS remains disabled.

Hard failures should represent conditions that cannot be healthy in the supported EverLeaf client/server data set. Ambiguous reference differences and exact duplicates that may be intentional remain review-only until runtime or authoritative reference data proves otherwise.

Empress/Cygnus expansion work is outside the EverLeaf release scope and should not be introduced to satisfy these audits.
