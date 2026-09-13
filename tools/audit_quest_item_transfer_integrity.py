#!/usr/bin/env python3
"""Static release gate for quest/untradeable item transfer semantics.

Quest items are allowed to remain in same-account storage, but must not become
player-to-player transfer vectors through direct trade, PlayerShop/Hired
Merchant, Duey, or ground drops. The runtime restriction is deliberately
centralized through ItemInformationProvider.isDropRestricted() and
Item.isUntradeable().
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IIP = ROOT / "src/main/java/server/ItemInformationProvider.java"
ITEM = ROOT / "src/main/java/client/inventory/Item.java"
INTERACTION = ROOT / "src/main/java/net/server/channel/handlers/PlayerInteractionHandler.java"
DUEY = ROOT / "src/main/java/client/processor/npc/DueyProcessor.java"
INVENTORY = ROOT / "src/main/java/client/inventory/manipulator/InventoryManipulator.java"
CONFIG = ROOT / "config.yaml"


def require(data: str, fragment: str, label: str) -> None:
    if fragment not in data:
        raise SystemExit(f"FAIL: {label}")


def main() -> int:
    iip = IIP.read_text(encoding="utf-8")
    item = ITEM.read_text(encoding="utf-8")
    interaction = INTERACTION.read_text(encoding="utf-8")
    duey = DUEY.read_text(encoding="utf-8")
    inventory = INVENTORY.read_text(encoding="utf-8")
    config = CONFIG.read_text(encoding="utf-8")

    require(iip, "return isLootRestricted(itemId) || isQuestItem(itemId);",
            "quest items are not included in drop restrictions")
    require(item, "ItemInformationProvider.getInstance().isDropRestricted(this.getItemId())",
            "Item.isUntradeable does not inherit WZ quest/trade restrictions")
    require(interaction, "ii.isDropRestricted(item.getItemId())",
            "direct trade does not reject drop/quest-restricted items")
    # The shop listing path now locks the source inventory and names the exact
    # captured object sourceItem. Keep this assertion aligned with that hardened
    # source-revalidation path instead of the retired ivItem local variable.
    require(interaction, "sourceItem == null || sourceItem.isUntradeable()",
            "PlayerShop/Hired Merchant listing does not reject untradeable items")
    require(duey, "item.isUntradeable() || ii.isUnmerchable(item.getItemId())",
            "Duey does not reject untradeable/quest items")
    require(inventory, "USE_ERASE_UNTRADEABLE_DROP && it.isUntradeable()",
            "ground-drop path does not recognize untradeable/quest items")
    require(config, "USE_ERASE_UNTRADEABLE_DROP: true",
            "untradeable ground drops are not configured to disappear")

    print("EverLeaf quest-item transfer integrity audit: PASS")
    print("  WZ quest/trade restrictions feed Item.isUntradeable")
    print("  direct trade rejects drop/quest-restricted items")
    print("  PlayerShop/Hired Merchant and Duey reject untradeable items")
    print("  dropped untradeable quest items disappear instead of becoming transferable loot")
    print("  same-account Storage is intentionally outside this player-to-player restriction gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
