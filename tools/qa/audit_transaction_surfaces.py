#!/usr/bin/env python3
"""Audit high-value trade/storage/shop mutation surfaces.

This deliberately separates in-memory concurrency protection from database
transaction protection. The older deep-QA heuristic treated any English use of
"transaction" as protection and missed real locking primitives such as
ReentrantLock and the per-client mutation lock.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JAVA_ROOT = ROOT / "src" / "main" / "java"
SURFACE_WORDS = ("trade", "storage", "shop", "merchant")
MEMORY_MUTATIONS = ("gainmeso(", "removeitem", "additem", "removefromslot", "addfromdrop", "addbyid", "setmeso(")
CONCURRENCY_MARKERS = ("synchronized", "reentrantlock", ".lock()", "tryacquireclient(", "lockinventory(", "atomicboolean")
SQL_MUTATION_RE = re.compile(r"\b(?:delete\s+from|insert\s+into|update\s+[`a-z0-9_])", re.I)
DB_TX_MARKERS = ("setautocommit(false", "commit()", "rollback()")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def main() -> int:
    findings = []
    for path in sorted(JAVA_ROOT.rglob("*.java")):
        if not any(word in path.name.lower() for word in SURFACE_WORDS):
            continue
        body = path.read_text(encoding="utf-8", errors="replace")
        lower = body.lower()
        memory_mutations = sum(lower.count(marker) for marker in MEMORY_MUTATIONS)
        sql_mutations = len(SQL_MUTATION_RE.findall(body))
        concurrency = [marker for marker in CONCURRENCY_MARKERS if marker in lower]
        db_tx = [marker for marker in DB_TX_MARKERS if marker in lower]

        if memory_mutations >= 2 and not concurrency:
            findings.append({
                "status": "REVIEW",
                "kind": "unprotected-memory-mutation",
                "path": rel(path),
                "memory_mutations": memory_mutations,
                "sql_mutations": sql_mutations,
                "detail": "Multiple inventory/meso mutations found without a recognized lock or per-client mutation guard.",
            })
        if sql_mutations >= 2 and not db_tx:
            findings.append({
                "status": "REVIEW",
                "kind": "multi-sql-without-explicit-transaction",
                "path": rel(path),
                "memory_mutations": memory_mutations,
                "sql_mutations": sql_mutations,
                "concurrency_markers": concurrency,
                "detail": "Multiple SQL mutations found without explicit commit/rollback markers; inspect crash consistency and lost-update behavior.",
            })

    print(json.dumps({"review": len(findings), "findings": findings}, indent=2))
    # Review-only initially: this auditor names exact surfaces for manual hardening.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
