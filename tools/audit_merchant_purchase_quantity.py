#!/usr/bin/env python3
"""Audit Hired Merchant purchase quantity arithmetic and ordering."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/server/maps/HiredMerchant.java"


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")

    required = (
        "if (item < 0 || item >= items.size())",
        "if (quantity < 1 || !pItem.isExist() || pItem.getBundles() < quantity)",
        "long totalQuantity = (long) pItem.getItem().getQuantity() * quantity;",
        "if (totalQuantity <= 0 || totalQuantity > Short.MAX_VALUE)",
        "newItem.setQuantity((short) totalQuantity);",
        "long grossPrice = (long) pItem.getPrice() * quantity;",
    )
    for fragment in required:
        if fragment not in text:
            raise SystemExit(f"FAIL merchant purchase quantity invariant missing: {fragment}")

    forbidden = (
        "newItem.setQuantity((short) ((pItem.getItem().getQuantity() * quantity)))",
        "newItem.setQuantity((short) (pItem.getItem().getQuantity() * quantity))",
    )
    for fragment in forbidden:
        if fragment in text:
            raise SystemExit("FAIL unchecked short quantity multiplication remains")

    validation = text.index("if (quantity < 1 || !pItem.isExist() || pItem.getBundles() < quantity)")
    multiply = text.index("long totalQuantity = (long) pItem.getItem().getQuantity() * quantity;")
    cast = text.index("newItem.setQuantity((short) totalQuantity);")
    guard = text.index("if (totalQuantity <= 0 || totalQuantity > Short.MAX_VALUE)")
    if not (validation < multiply < guard < cast):
        raise SystemExit("FAIL merchant quantity validation/multiply/guard/cast ordering is unsafe")

    print("EverLeaf merchant purchase quantity audit: PASS")
    print("  client bundle count is validated before quantity construction")
    print("  multiplication is long-width")
    print("  short range is checked before cast")
    print("  malformed wrapped/negative purchase quantities fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
