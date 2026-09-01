#!/usr/bin/env python3
"""Release gate for race-safe offline Hired Merchant seller credits."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/server/maps/HiredMerchant.java"


def main() -> int:
    text = TARGET.read_text(encoding="utf-8", errors="replace")
    start = text.index("public void buy(Client c, int item, short quantity)")
    end = text.index("private void announceItemSold", start)
    buy = text[start:end]

    atomic_sql = "UPDATE characters SET MerchantMesos = LEAST(CAST(COALESCE(MerchantMesos, 0) AS SIGNED) + ?, ?) WHERE id = ?"
    if atomic_sql not in buy:
        raise SystemExit("ERROR offline merchant seller credit is not an atomic SQL increment")
    if "SELECT MerchantMesos FROM characters WHERE id = ?" in buy:
        raise SystemExit("ERROR race-prone offline MerchantMesos SELECT remains")
    if "if (ps.executeUpdate() != 1)" not in buy:
        raise SystemExit("ERROR offline merchant seller credit does not verify the owner row update")
    if "ps.setInt(2, Integer.MAX_VALUE);" not in buy:
        raise SystemExit("ERROR offline merchant seller credit lacks int overflow clamp")

    print("EverLeaf merchant seller-credit concurrency audit: PASS")
    print("  offline credit: atomic SQL increment")
    print("  stale SELECT -> UPDATE race: removed")
    print("  signed-int overflow: clamped")
    print("  missing seller row: detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
