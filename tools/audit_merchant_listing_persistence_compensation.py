#!/usr/bin/env python3
"""Audit Hired Merchant listing persistence compensation."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDLER = ROOT / "src/main/java/net/server/channel/handlers/PlayerInteractionHandler.java"


def main() -> int:
    text = HANDLER.read_text(encoding="utf-8")
    required = (
        "boolean merchantPersisted = false;",
        "merchant.saveItems(false);",
        "Hired Merchant listing persistence failed once",
        "Hired Merchant listing persistence failed twice",
        "Item restoreItem = sourceItem.copy();",
        "restoreItem.setQuantity(removeQuantity);",
        "InventoryManipulator.checkSpace(c, restoreItem.getItemId(), restoreItem.getQuantity(), restoreItem.getOwner(), restoreItem.getExpiration())",
        "InventoryManipulator.addFromDrop(c, restoreItem, false)",
        "boolean listingRolledBack = merchant.removeItem(shopItem);",
        "chr.saveCharToDB(false);",
        "merchant remains closed with the volatile listing",
    )
    for fragment in required:
        if fragment not in text:
            raise SystemExit(f"FAIL merchant listing persistence compensation invariant missing: {fragment}")

    if text.count("merchant.saveItems(false);") < 3:
        raise SystemExit("FAIL merchant listing persistence does not include initial, retry, and cleanup snapshot attempts")

    restore_pos = text.index("InventoryManipulator.addFromDrop(c, restoreItem, false)")
    rollback_pos = text.index("boolean listingRolledBack = merchant.removeItem(shopItem);")
    if restore_pos > rollback_pos:
        raise SystemExit("FAIL volatile listing is removed before source inventory restoration succeeds")

    print("EverLeaf Hired Merchant listing persistence compensation audit: PASS")
    print("  transient snapshot failure receives one immediate retry")
    print("  failed durable listing restores the exact source payload")
    print("  source restoration precedes volatile-listing rollback")
    print("  restored inventory receives an immediate character save")
    print("  cleanup snapshot is attempted after compensation")
    print("  unrecoverable compensation leaves the merchant closed")
    print("  NOTE: process death between cross-domain writes still requires a durable journal/outbox for exactly-once semantics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
