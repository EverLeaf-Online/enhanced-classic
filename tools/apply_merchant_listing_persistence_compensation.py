#!/usr/bin/env python3
"""Compensate Hired Merchant listing persistence failures after source removal."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDLER = ROOT / "src/main/java/net/server/channel/handlers/PlayerInteractionHandler.java"


def main() -> int:
    text = HANDLER.read_text(encoding="utf-8")
    marker = "Hired Merchant listing persistence failed twice"
    if marker in text:
        print("OK already fixed: Hired Merchant listing persistence compensation")
    else:
        old = '''                    try {\n                        merchant.saveItems(false);   // thanks Masterrulax for realizing yet another dupe with merchants/Fredrick\n                    } catch (SQLException ex) {\n                        log.error("Failed to persist Hired Merchant listing for chr {} item {}", chr.getName(), sourceItem.getItemId(), ex);\n                    }\n'''
        new = '''                    boolean merchantPersisted = false;\n                    SQLException merchantPersistenceFailure = null;\n                    try {\n                        merchant.saveItems(false);   // thanks Masterrulax for realizing yet another dupe with merchants/Fredrick\n                        merchantPersisted = true;\n                    } catch (SQLException firstEx) {\n                        merchantPersistenceFailure = firstEx;\n                        log.warn("Hired Merchant listing persistence failed once for chr {} item {}; retrying", chr.getName(), sourceItem.getItemId(), firstEx);\n                        try {\n                            merchant.saveItems(false);\n                            merchantPersisted = true;\n                        } catch (SQLException retryEx) {\n                            firstEx.addSuppressed(retryEx);\n                            log.error("Hired Merchant listing persistence failed twice for chr {} item {}; compensating source removal", chr.getName(), sourceItem.getItemId(), firstEx);\n                        }\n                    }\n\n                    if (!merchantPersisted) {\n                        Item restoreItem = sourceItem.copy();\n                        restoreItem.setQuantity(removeQuantity);\n                        boolean restoreFits = InventoryManipulator.checkSpace(c, restoreItem.getItemId(), restoreItem.getQuantity(), restoreItem.getOwner(), restoreItem.getExpiration());\n                        boolean restored = restoreFits && InventoryManipulator.addFromDrop(c, restoreItem, false);\n                        if (restored) {\n                            boolean listingRolledBack = merchant.removeItem(shopItem);\n                            if (!listingRolledBack) {\n                                log.error("CRITICAL: restored source item but could not roll back volatile Hired Merchant listing for chr {} item {}", chr.getName(), sourceItem.getItemId());\n                                c.disconnect(true, false);\n                                return;\n                            }\n\n                            chr.saveCharToDB(false);\n                            try {\n                                merchant.saveItems(false);\n                            } catch (SQLException cleanupEx) {\n                                if (merchantPersistenceFailure != null) {\n                                    merchantPersistenceFailure.addSuppressed(cleanupEx);\n                                }\n                                log.error("Compensated Hired Merchant listing for chr {} item {}, but cleanup snapshot persistence still failed", chr.getName(), sourceItem.getItemId(), cleanupEx);\n                            }\n                            c.sendPacket(PacketCreator.updateHiredMerchant(merchant, chr));\n                            c.sendPacket(PacketCreator.serverNotice(1, "The merchant could not save that listing. Your item was restored; please try again."));\n                            c.sendPacket(PacketCreator.enableActions());\n                            return;\n                        }\n\n                        log.error("CRITICAL: Hired Merchant persistence failed and source-item compensation could not restore chr {} item {}; merchant remains closed with the volatile listing", chr.getName(), sourceItem.getItemId(), merchantPersistenceFailure);\n                        c.sendPacket(PacketCreator.serverNotice(1, "The merchant could not save this listing and automatic inventory restoration could not complete. Keep the merchant closed and contact staff."));\n                        c.sendPacket(PacketCreator.enableActions());\n                        return;\n                    }\n'''
        if old not in text:
            raise SystemExit("ERROR expected Hired Merchant persistence catch block not found")
        HANDLER.write_text(text.replace(old, new, 1), encoding="utf-8")
        print("FIXED: Hired Merchant listing persistence compensation")

    final = HANDLER.read_text(encoding="utf-8")
    required = (
        "boolean merchantPersisted = false;",
        "Hired Merchant listing persistence failed once",
        "Hired Merchant listing persistence failed twice",
        "InventoryManipulator.checkSpace(c, restoreItem.getItemId(), restoreItem.getQuantity(), restoreItem.getOwner(), restoreItem.getExpiration())",
        "InventoryManipulator.addFromDrop(c, restoreItem, false)",
        "boolean listingRolledBack = merchant.removeItem(shopItem);",
        "chr.saveCharToDB(false);",
        "merchant remains closed with the volatile listing",
    )
    for fragment in required:
        if fragment not in final:
            raise SystemExit(f"ERROR merchant listing compensation invariant missing: {fragment}")

    print("EverLeaf Hired Merchant listing persistence compensation: PASS")
    print("  failed merchant snapshot is retried once before compensation")
    print("  compensation restores the exact removed source quantity with owner/flag/expiration preserved")
    print("  volatile listing is removed only after inventory restoration succeeds")
    print("  restored inventory is persisted immediately")
    print("  cleanup merchant snapshot is retried after rollback")
    print("  unrecoverable compensation fails closed without opening the merchant")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
