#!/usr/bin/env python3
"""Make Hired Merchant snapshots and Fredrick recovery markers one SQL transaction."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MERCHANT = ROOT / "src/main/java/server/maps/HiredMerchant.java"
FREDRICK = ROOT / "src/main/java/client/processor/npc/FredrickProcessor.java"


def replace_once(text: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if new in text:
        print(f"OK already fixed: {label}")
        return text, False
    if old not in text:
        raise SystemExit(f"ERROR expected merchant persistence snippet not found: {label}")
    print(f"FIXED: {label}")
    return text.replace(old, new, 1), True


def patch_fredrick() -> None:
    text = FREDRICK.read_text(encoding="utf-8")
    old = """    public static void insertFredrickLog(int cid) {
        try (Connection con = DatabaseConnection.getConnection()) {

            removeFredrickLog(con, cid);
            try (PreparedStatement ps = con.prepareStatement(\"INSERT INTO `fredstorage` (`cid`, `daynotes`, `timestamp`) VALUES (?, 0, ?)\")) {
                ps.setInt(1, cid);
                ps.setTimestamp(2, new Timestamp(System.currentTimeMillis()));
                ps.executeUpdate();
            }
        } catch (SQLException sqle) {
            sqle.printStackTrace();
        }
    }
"""
    new = """    public static void insertFredrickLog(int cid) {
        try (Connection con = DatabaseConnection.getConnection()) {
            insertFredrickLog(con, cid);
        } catch (SQLException sqle) {
            log.error(\"Failed to insert Fredrick recovery log for cid {}\", cid, sqle);
        }
    }

    public static void insertFredrickLog(Connection con, int cid) throws SQLException {
        removeFredrickLog(con, cid);
        try (PreparedStatement ps = con.prepareStatement(\"INSERT INTO `fredstorage` (`cid`, `daynotes`, `timestamp`) VALUES (?, 0, ?)\")) {
            ps.setInt(1, cid);
            ps.setTimestamp(2, new Timestamp(System.currentTimeMillis()));
            ps.executeUpdate();
        }
    }
"""
    text, changed = replace_once(text, old, new, "connection-aware Fredrick recovery log")
    if changed:
        FREDRICK.write_text(text, encoding="utf-8")


def patch_merchant() -> None:
    text = MERCHANT.read_text(encoding="utf-8")
    old = """        try (Connection con = DatabaseConnection.getConnection()) {
            ItemFactory.MERCHANT.saveItems(itemsWithType, bundles, this.ownerId, con);
        }

        FredrickProcessor.insertFredrickLog(this.ownerId);
"""
    new = """        try (Connection con = DatabaseConnection.getConnection()) {
            con.setAutoCommit(false);
            try {
                ItemFactory.MERCHANT.saveItems(itemsWithType, bundles, this.ownerId, con);
                FredrickProcessor.insertFredrickLog(con, this.ownerId);
                con.commit();
            } catch (SQLException | RuntimeException ex) {
                try {
                    con.rollback();
                } catch (SQLException rollbackEx) {
                    ex.addSuppressed(rollbackEx);
                }
                throw ex;
            }
        }
"""
    text, changed = replace_once(text, old, new, "atomic merchant snapshot plus Fredrick marker")
    if changed:
        MERCHANT.write_text(text, encoding="utf-8")


def main() -> int:
    patch_fredrick()
    patch_merchant()

    merchant = MERCHANT.read_text(encoding="utf-8")
    fredrick = FREDRICK.read_text(encoding="utf-8")
    required = (
        (fredrick, "public static void insertFredrickLog(Connection con, int cid) throws SQLException"),
        (fredrick, "removeFredrickLog(con, cid);"),
        (merchant, "con.setAutoCommit(false);"),
        (merchant, "ItemFactory.MERCHANT.saveItems(itemsWithType, bundles, this.ownerId, con);"),
        (merchant, "FredrickProcessor.insertFredrickLog(con, this.ownerId);"),
        (merchant, "con.commit();"),
        (merchant, "con.rollback();"),
    )
    for data, fragment in required:
        if fragment not in data:
            raise SystemExit(f"ERROR merchant persistence invariant missing: {fragment}")

    print("EverLeaf merchant persistence transaction: PASS")
    print("  merchant inventory snapshot + Fredrick marker share one connection")
    print("  auto-commit disabled during snapshot persistence")
    print("  commit only after both writes succeed")
    print("  SQL/runtime failure rolls the snapshot transaction back")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
