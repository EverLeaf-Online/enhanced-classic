#!/usr/bin/env python3
"""Regression gate for repeat-safe Duey source transforms.

Production applies release transforms before staging and applies them again while
building the staged release. This test mirrors that composition and requires the
second ownership+settlement pass to leave DueyProcessor.java byte-identical.
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/client/processor/npc/DueyProcessor.java"


def sha256() -> str:
    return hashlib.sha256(TARGET.read_bytes()).hexdigest()


def run(script: str) -> None:
    subprocess.run(["python3", str(ROOT / "tools" / script)], cwd=ROOT, check=True)


def main() -> int:
    before = sha256()
    run("apply_duey_ownership_fixes.py")
    run("apply_duey_settlement_fixes.py")
    after = sha256()

    if before != after:
        raise SystemExit(
            "ERROR Duey ownership/settlement transforms mutated source on a repeat pass"
        )

    run("audit_duey_integrity.py")
    run("audit_duey_settlement.py")
    print("EverLeaf Duey transform idempotency: PASS")
    print("  repeat ownership + settlement pass: byte-identical")
    print("  ownership and settlement audits: PASS after repeat pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
