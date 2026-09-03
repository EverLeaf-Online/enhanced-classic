package everleaf.progression;

import client.Character;
import client.inventory.manipulator.InventoryManipulator;

/** Small Java boundary so event scripts do not need to depend on overloaded primitive inventory APIs. */
public final class CygnusRewardDelivery {
    private CygnusRewardDelivery() {}

    public static boolean canReceive(Character player, int itemId) {
        return player != null && itemId > 0 && player.canHold(itemId);
    }

    public static boolean deliver(Character player, int itemId) {
        if (!canReceive(player, itemId)) return false;
        return InventoryManipulator.addById(player.getClient(), itemId, (short) 1,
                "Fallen Cygnus weekly clear", -1);
    }
}
