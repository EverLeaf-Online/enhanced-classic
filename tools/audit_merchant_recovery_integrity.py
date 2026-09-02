#!/usr/bin/env python3
"""Release gate for Hired Merchant/Fredrick recovery safety."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MERCHANT = ROOT / "src/main/java/server/maps/HiredMerchant.java"
FREDRICK = ROOT / "src/main/java/client/processor/npc/FredrickProcessor.java"


def require(data: str, fragment: str, label: str) -> None:
    if fragment not in data:
        raise SystemExit(f"ERROR merchant recovery invariant missing ({label}): {fragment}")


def main() -> int:
    merchant = MERCHANT.read_text(encoding="utf-8", errors="replace")
    fredrick = FREDRICK.read_text(encoding="utf-8", errors="replace")

    require(merchant, "if (item < 0 || item >= items.size())", "buy slot bounds")
    buy_start = merchant.index("public void buy(Client c, int item, short quantity)")
    buy_end = merchant.index("private void announceItemSold", buy_start)
    buy = merchant[buy_start:buy_end]
    if buy.index("if (item < 0 || item >= items.size())") > buy.index("PlayerShopItem pItem = items.get(item);"):
        raise SystemExit("ERROR merchant slot is dereferenced before bounds validation")

    require(merchant, "long grossPrice = (long) pItem.getPrice() * quantity;", "price widening")
    require(merchant, "if (grossPrice <= 0 || grossPrice > Integer.MAX_VALUE)", "price bounds")

    take_start = merchant.index("public void takeItemBack")
    take_end = merchant.index("private static boolean canBuy", take_start)
    take = merchant[take_start:take_end]
    require(take, "if (!InventoryManipulator.addFromDrop(chr.getClient(), iitem, true))", "take-back insertion result")
    if take.index("removeFromSlot(slot);") < take.index("if (!InventoryManipulator.addFromDrop"):
        raise SystemExit("ERROR merchant item removed before successful owner inventory insertion")

    require(fredrick, "ps.addBatch();", "reminder batch add")
    require(fredrick, "ItemFactory.MERCHANT.saveItems(remaining, bundles, chr.getId(), con);", "failed recovery persistence")
    retrieve_start = fredrick.index("public void fredrickRetrieveItems")
    retrieve = fredrick[retrieve_start:]
    delete_idx = retrieve.index("if (deleteFredrickItems(chr.getId()))")
    withdraw_idx = retrieve.index("chr.withdrawMerchantMesos();")
    if withdraw_idx < delete_idx:
        raise SystemExit("ERROR Fredrick withdraws merchant mesos before stored-item deletion succeeds")
    require(retrieve, "if (!InventoryManipulator.addFromDrop(chr.getClient(), item, false))", "Fredrick insertion result")
    repersist_idx = retrieve.index("ItemFactory.MERCHANT.saveItems(remaining, bundles, chr.getId(), con);")
    if repersist_idx > withdraw_idx:
        raise SystemExit("ERROR Fredrick can charge mesos before re-persisting undelivered items")

    print("EverLeaf merchant recovery integrity audit: PASS")
    print("  Hired Merchant client slot bounds: fail closed before dereference")
    print("  purchase total: long multiplication + positive/int bounds")
    print("  owner take-back: listing removed only after successful inventory insert")
    print("  Fredrick reminder deletion: real JDBC batch")
    print("  Fredrick partial recovery: remaining items re-persisted")
    print("  Fredrick merchant mesos: withdrawn after item recovery")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
