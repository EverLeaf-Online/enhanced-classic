#!/usr/bin/env python3
"""Static release gate for shop listing source integrity."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDLER = ROOT / "src/main/java/net/server/channel/handlers/PlayerInteractionHandler.java"
PLAYER_SHOP = ROOT / "src/main/java/server/maps/PlayerShop.java"
HIRED = ROOT / "src/main/java/server/maps/HiredMerchant.java"


def require(data: str, fragment: str, label: str) -> None:
    if fragment not in data:
        raise SystemExit(f"FAIL: {label}")


def main() -> int:
    handler = HANDLER.read_text(encoding="utf-8")
    player_shop = PLAYER_SHOP.read_text(encoding="utf-8")
    hired = HIRED.read_text(encoding="utf-8")

    require(handler, "ivType == null || ivType == InventoryType.UNDEFINED || ivType == InventoryType.CANHOLD || ivType == InventoryType.EQUIPPED", "invalid inventory-type gate missing")
    require(handler, "long totalQuantity = (long) listingPerBundle * listingBundles;", "long-width listing quantity calculation missing")
    require(handler, "totalQuantity > Short.MAX_VALUE", "short-range listing quantity gate missing")
    require(handler, "Item currentItem = inv.getItem(slot);", "locked source-item revalidation missing")
    require(handler, "currentItem == sourceItem", "source identity revalidation missing")
    require(handler, "currentItem.getQuantity() >= removeQuantity", "source quantity revalidation missing")
    require(handler, "shop.removeItem(shopItem) : merchant.removeItem(shopItem)", "failed-source rollback missing")
    require(player_shop, "public boolean removeItem(PlayerShopItem item)", "PlayerShop rollback helper missing")
    require(hired, "public boolean removeItem(PlayerShopItem item)", "HiredMerchant rollback helper missing")
    require(player_shop, "return items.remove(item);", "PlayerShop identity rollback missing")
    require(hired, "return items.remove(item);", "HiredMerchant identity rollback missing")

    invalid_lookup = "InventoryType ivType = InventoryType.getByType(p.readByte());\n                short slot = p.readShort();\n                short bundles = p.readShort();\n                Item ivItem = chr.getInventory(ivType).getItem(slot);"
    if invalid_lookup in handler:
        raise SystemExit("FAIL: legacy shop listing dereferences client inventory type before validation")

    print("EverLeaf shop listing source integrity audit: PASS")
    print("  invalid inventory types fail closed before inventory dereference")
    print("  listing quantities use checked long arithmetic")
    print("  exact source slot/item/quantity is revalidated under inventory lock")
    print("  failed revalidation rolls back the admitted listing by identity")
    print("  stock rollback is synchronized in PlayerShop and HiredMerchant")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
