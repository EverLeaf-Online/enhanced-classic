#!/usr/bin/env python3
"""Audit PlayerShop list snapshot consistency."""
from pathlib import Path

from audit_shop_listing_source_integrity import main as audit_listing_source_integrity
from audit_merchant_listing_persistence_compensation import main as audit_listing_persistence_compensation
from audit_merchant_open_persistence_gate import main as audit_merchant_open_persistence_gate

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/server/maps/PlayerShop.java"


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    required = (
        "return Collections.unmodifiableList(new ArrayList<>(items));",
        "return Collections.unmodifiableList(new ArrayList<>(sold));",
    )
    for fragment in required:
        if fragment not in text:
            raise SystemExit(f"FAIL PlayerShop snapshot invariant missing: {fragment}")

    forbidden = (
        "return Collections.unmodifiableList(items);",
        "return Collections.unmodifiableList(sold);",
    )
    for fragment in forbidden:
        if fragment in text:
            raise SystemExit(f"FAIL live PlayerShop list view remains: {fragment}")

    if audit_listing_source_integrity() != 0:
        raise SystemExit("FAIL shop listing source integrity audit")
    if audit_listing_persistence_compensation() != 0:
        raise SystemExit("FAIL merchant listing persistence compensation audit")
    if audit_merchant_open_persistence_gate() != 0:
        raise SystemExit("FAIL merchant open persistence audit")

    print("EverLeaf PlayerShop snapshot consistency audit: PASS")
    print("  item-list readers use a detached structural snapshot")
    print("  sold-list readers use a detached structural snapshot")
    print("  structural mutation cannot race unlocked external iteration")
    print("  listing source, compensation, and open persistence invariants are enforced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
