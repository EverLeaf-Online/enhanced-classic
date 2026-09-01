#!/usr/bin/env python3
"""Harden offline Hired Merchant seller-credit updates against lost increments."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/main/java/server/maps/HiredMerchant.java"


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")

    if "import org.slf4j.Logger;" not in text:
        anchor = "import net.server.Server;\n"
        if anchor not in text:
            raise SystemExit("ERROR HiredMerchant logger import anchor not found")
        text = text.replace(anchor, anchor + "import org.slf4j.Logger;\nimport org.slf4j.LoggerFactory;\n", 1)
        print("FIXED: HiredMerchant logger imports")
    else:
        print("OK already fixed: HiredMerchant logger imports")

    logger = "    private static final Logger log = LoggerFactory.getLogger(HiredMerchant.class);\n"
    if logger not in text:
        anchor = "public class HiredMerchant extends AbstractMapObject {\n"
        if anchor not in text:
            raise SystemExit("ERROR HiredMerchant logger field anchor not found")
        text = text.replace(anchor, anchor + logger, 1)
        print("FIXED: HiredMerchant logger field")
    else:
        print("OK already fixed: HiredMerchant logger field")

    old = '''                    } else {
                        try (Connection con = DatabaseConnection.getConnection()) {
                            long merchantMesos = 0;
                            try (PreparedStatement ps = con.prepareStatement("SELECT MerchantMesos FROM characters WHERE id = ?")) {
                                ps.setInt(1, ownerId);
                                try (ResultSet rs = ps.executeQuery()) {
                                    if (rs.next()) {
                                        merchantMesos = rs.getInt(1);
                                    }
                                }
                            }
                            merchantMesos += price;

                            try (PreparedStatement ps = con.prepareStatement("UPDATE characters SET MerchantMesos = ? WHERE id = ?", PreparedStatement.RETURN_GENERATED_KEYS)) {
                                ps.setInt(1, (int) Math.min(merchantMesos, Integer.MAX_VALUE));
                                ps.setInt(2, ownerId);
                                ps.executeUpdate();
                            }
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
'''
    new = '''                    } else {
                        try (Connection con = DatabaseConnection.getConnection();
                             PreparedStatement ps = con.prepareStatement(
                                     "UPDATE characters SET MerchantMesos = LEAST(CAST(COALESCE(MerchantMesos, 0) AS SIGNED) + ?, ?) WHERE id = ?")) {
                            ps.setInt(1, price);
                            ps.setInt(2, Integer.MAX_VALUE);
                            ps.setInt(3, ownerId);
                            if (ps.executeUpdate() != 1) {
                                log.error("Failed to credit offline Hired Merchant owner {} with {} mesos: character row not found", ownerId, price);
                            }
                        } catch (SQLException e) {
                            log.error("Failed to credit offline Hired Merchant owner {} with {} mesos", ownerId, price, e);
                        }
                    }
'''
    if new in text:
        print("OK already fixed: atomic offline merchant credit increment")
    elif old in text:
        text = text.replace(old, new, 1)
        print("FIXED: atomic offline merchant credit increment")
    else:
        raise SystemExit("ERROR expected offline merchant credit read/modify/write block not found")

    TARGET.write_text(text, encoding="utf-8")
    final = TARGET.read_text(encoding="utf-8")
    required = (
        "import org.slf4j.Logger;",
        "import org.slf4j.LoggerFactory;",
        "private static final Logger log = LoggerFactory.getLogger(HiredMerchant.class);",
        "UPDATE characters SET MerchantMesos = LEAST(CAST(COALESCE(MerchantMesos, 0) AS SIGNED) + ?, ?) WHERE id = ?",
        "if (ps.executeUpdate() != 1)",
        "log.error(\"Failed to credit offline Hired Merchant owner {} with {} mesos",
    )
    for fragment in required:
        if fragment not in final:
            raise SystemExit(f"ERROR merchant credit invariant missing: {fragment}")
    if "SELECT MerchantMesos FROM characters WHERE id = ?" in final:
        raise SystemExit("ERROR stale offline merchant credit read/modify/write remains")

    print("EverLeaf merchant credit concurrency hardening: PASS")
    print("  offline seller credit uses one atomic SQL UPDATE")
    print("  concurrent sales cannot overwrite each other's prior MerchantMesos read")
    print("  credit clamps at signed-int maximum")
    print("  missing owner row / SQL failure is explicitly logged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
