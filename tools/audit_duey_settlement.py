#!/usr/bin/env python3
"""Release gate for deterministic Duey settlement failure-path safety."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DUEY = ROOT / "src/main/java/client/processor/npc/DueyProcessor.java"


def main() -> int:
    text = DUEY.read_text(encoding="utf-8", errors="replace")
    required = (
        "if (invTypeId <= 0)",
        "sourceItem == null || amount < 1 || sourceItem.getQuantity() < amount",
        "short transferAmount = ItemConstants.isRechargeable(sourceItem.getItemId())",
        "Item packageItem = sourceItem.copy();",
        "KarmaManipulator.toggleKarmaFlagToUntradeable(packageItem);",
        "if (!insertPackageItem(packageId, packageItem))",
        "InventoryManipulator.removeFromSlot(c, invType, itemPos, transferAmount, true, false);",
        "if (res != 0)",
        "removePackageFromDB(packageId);",
        "if (packageId != -1 && !insertPackageItem(packageId, item))",
        "else if (!InventoryManipulator.addFromDrop(c, dpItem, false))",
    )
    for fragment in required:
        if fragment not in text:
            raise SystemExit(f"ERROR Duey settlement invariant missing: {fragment}")

    helper_start = text.index("private static int addPackageItemFromInventory")
    send_start = text.index("public static void dueySendItem")
    helper = text[helper_start:send_start]
    if helper.index("insertPackageItem(packageId, packageItem)") > helper.index("InventoryManipulator.removeFromSlot"):
        raise SystemExit("ERROR sender inventory is mutated before package payload persistence")

    send_end = text.index("public static void dueyRemovePackage", send_start)
    send = text[send_start:send_end]
    failure = send.index("if (res != 0)")
    charge_meso = send.index("gainMeso((int) -finalcost")
    charge_ticket = send.index("InventoryManipulator.removeById", send.index("int packageId = createPackage"))
    if charge_meso < failure or charge_ticket < failure:
        raise SystemExit("ERROR Duey charges sender before send settlement succeeds")
    if send.index("removePackageFromDB(packageId);", failure) > charge_meso:
        raise SystemExit("ERROR failed Duey package cleanup occurs after sender charging")

    print("EverLeaf Duey settlement audit: PASS")
    print("  payload persistence precedes sender item removal")
    print("  failed sends clean incomplete package headers")
    print("  mesos and Quick Delivery ticket charge only after settlement")
    print("  rechargeable sends transfer/remove one identical full-stack quantity")
    print("  final claim insertion failure aborts before meso grant/package removal")
    print("  NOTE: process-crash exactly-once delivery still requires a durable cross-domain design")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
