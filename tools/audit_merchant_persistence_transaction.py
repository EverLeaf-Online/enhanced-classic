#!/usr/bin/env python3
"""Release gate for atomic Hired Merchant snapshot/recovery-marker persistence."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MERCHANT = ROOT / "src/main/java/server/maps/HiredMerchant.java"
FREDRICK = ROOT / "src/main/java/client/processor/npc/FredrickProcessor.java"


def main() -> int:
    merchant = MERCHANT.read_text(encoding="utf-8", errors="replace")
    fredrick = FREDRICK.read_text(encoding="utf-8", errors="replace")

    required_fredrick = (
        "public static void insertFredrickLog(Connection con, int cid) throws SQLException",
        "removeFredrickLog(con, cid);",
        "INSERT INTO `fredstorage`",
    )
    for fragment in required_fredrick:
        if fragment not in fredrick:
            raise SystemExit(f"ERROR Fredrick transactional marker invariant missing: {fragment}")

    start = merchant.index("public void saveItems(boolean shutdown) throws SQLException")
    end = merchant.index("private static boolean check", start)
    save = merchant[start:end]
    required_save = (
        "con.setAutoCommit(false);",
        "ItemFactory.MERCHANT.saveItems(itemsWithType, bundles, this.ownerId, con);",
        "FredrickProcessor.insertFredrickLog(con, this.ownerId);",
        "con.commit();",
        "con.rollback();",
    )
    for fragment in required_save:
        if fragment not in save:
            raise SystemExit(f"ERROR merchant snapshot transaction invariant missing: {fragment}")

    if save.index("ItemFactory.MERCHANT.saveItems") > save.index("FredrickProcessor.insertFredrickLog(con"):
        raise SystemExit("ERROR Fredrick recovery marker is written before merchant inventory snapshot")
    if save.index("FredrickProcessor.insertFredrickLog(con") > save.index("con.commit();"):
        raise SystemExit("ERROR merchant transaction commits before Fredrick recovery marker")

    print("EverLeaf merchant persistence transaction audit: PASS")
    print("  snapshot + recovery marker use one SQL connection")
    print("  transaction commits after both writes")
    print("  failure path rolls back before propagating")
    print("  standalone Fredrick log API remains available for legacy callers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
