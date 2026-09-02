package everleaf.progression;

import client.inventory.InventoryType;

/** Inventory location captured before atomic forge payment. */
public record RootedForgeTarget(int itemId, InventoryType inventoryType, short slot) {
    public RootedForgeTarget {
        if (itemId <= 0) throw new IllegalArgumentException("itemId must be positive");
        if (inventoryType != InventoryType.EQUIP && inventoryType != InventoryType.EQUIPPED) {
            throw new IllegalArgumentException("forge target must be equipment");
        }
        if (inventoryType == InventoryType.EQUIP && slot <= 0) throw new IllegalArgumentException("invalid equip slot");
        if (inventoryType == InventoryType.EQUIPPED && slot >= 0) throw new IllegalArgumentException("invalid equipped slot");
    }
}
