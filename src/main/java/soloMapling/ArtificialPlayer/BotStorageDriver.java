package soloMapling.ArtificialPlayer;

import client.Character;
import client.inventory.Inventory;
import client.inventory.InventoryType;
import client.inventory.Item;
import client.inventory.manipulator.InventoryManipulator;
import client.inventory.manipulator.KarmaManipulator;
import constants.id.ItemId;
import constants.inventory.ItemConstants;
import server.ItemInformationProvider;
import server.Storage;
import server.life.NPC;

/** Exercises EverLeaf's real account-storage container with the same inventory/meso invariants as clients. */
public final class BotStorageDriver {
    private static final double INTERACT_RANGE_SQ = 250.0 * 250.0;

    private BotStorageDriver() {}

    public static StorageResult open(Character bot, int npcId) {
        if (!eligible(bot)) return StorageResult.fail("not-eligible");
        NPC npc = BotNpcDriver.findNpc(bot, npcId);
        if (npc == null || npc.getPosition() == null) return StorageResult.fail("npc-not-on-map");
        if (bot.getPosition().distanceSq(npc.getPosition()) > INTERACT_RANGE_SQ) return StorageResult.fail("npc-too-far");
        Storage storage = bot.getStorage();
        if (storage == null) return StorageResult.fail("storage-unavailable");
        storage.sendStorage(bot.getClient(), npcId);
        return snapshot(bot, "opened", 0, 0);
    }

    public static StorageResult close(Character bot) {
        if (!eligible(bot) || bot.getStorage() == null) return StorageResult.fail("not-eligible");
        bot.getStorage().close();
        return snapshot(bot, "closed", 0, 0);
    }

    public static StorageResult deposit(Character bot, InventoryType type, short slot, short quantity) {
        if (!sessionValid(bot)) return StorageResult.fail("storage-not-open");
        if (type == null || type == InventoryType.UNDEFINED || type == InventoryType.EQUIPPED || quantity <= 0) {
            return StorageResult.fail("invalid-item-request");
        }

        Storage storage = bot.getStorage();
        if (storage.isFull()) return StorageResult.fail("storage-full");
        int fee = storage.getStoreFee();
        if (bot.getMeso() < fee) return StorageResult.fail("insufficient-mesos-for-fee");

        Inventory inv = bot.getInventory(type);
        inv.lockInventory();
        try {
            Item source = inv.getItem(slot);
            if (source == null || source.getQuantity() < quantity) return StorageResult.fail("item-not-present");
            int itemId = source.getItemId();
            if (ItemId.isWeddingRing(itemId) || ItemId.isWeddingToken(itemId)) return StorageResult.fail("item-storage-blocked");
            if (ItemConstants.isRechargeable(itemId)) quantity = source.getQuantity();

            Item stored = source.copy();
            stored.setQuantity(quantity);
            KarmaManipulator.toggleKarmaFlagToUntradeable(stored);
            if (!storage.store(stored)) return StorageResult.fail("storage-full");

            try {
                InventoryManipulator.removeFromSlot(bot.getClient(), type, slot, quantity, false);
            } catch (RuntimeException failure) {
                storage.takeOut(stored);
                return StorageResult.fail("inventory-remove-failed");
            }

            if (fee > 0) bot.gainMeso(-fee, false, true, false);
            bot.setUsedStorage();
            storage.sendStored(bot.getClient(), type);
            return snapshot(bot, "item-deposited", itemId, quantity);
        } finally {
            inv.unlockInventory();
        }
    }

    public static StorageResult withdraw(Character bot, int storageIndex) {
        if (!sessionValid(bot)) return StorageResult.fail("storage-not-open");
        Storage storage = bot.getStorage();
        if (storageIndex < 0 || storageIndex >= storage.getItems().size()) return StorageResult.fail("invalid-storage-index");

        Item item = storage.getItems().get(storageIndex);
        if (item == null) return StorageResult.fail("item-not-present");
        ItemInformationProvider ii = ItemInformationProvider.getInstance();
        if (ii.isPickupRestricted(item.getItemId()) && bot.haveItemWithId(item.getItemId(), true)) {
            return StorageResult.fail("pickup-restricted");
        }
        int fee = storage.getTakeOutFee();
        if (bot.getMeso() < fee) return StorageResult.fail("insufficient-mesos-for-fee");
        if (!InventoryManipulator.checkSpace(bot.getClient(), item.getItemId(), item.getQuantity(), item.getOwner())) {
            return StorageResult.fail("inventory-full");
        }

        if (!storage.takeOut(item)) return StorageResult.fail("storage-remove-failed");
        try {
            KarmaManipulator.toggleKarmaFlagToUntradeable(item);
            InventoryManipulator.addFromDrop(bot.getClient(), item, false);
        } catch (RuntimeException failure) {
            storage.store(item);
            return StorageResult.fail("inventory-add-failed");
        }

        if (fee > 0) bot.gainMeso(-fee, false, true, false);
        bot.setUsedStorage();
        storage.sendTakenOut(bot.getClient(), item.getInventoryType());
        return snapshot(bot, "item-withdrawn", item.getItemId(), item.getQuantity());
    }

    public static StorageResult depositMesos(Character bot, int amount) {
        if (!sessionValid(bot)) return StorageResult.fail("storage-not-open");
        if (amount <= 0 || bot.getMeso() < amount) return StorageResult.fail("insufficient-mesos");
        Storage storage = bot.getStorage();
        long next = (long) storage.getMeso() + amount;
        if (next > Integer.MAX_VALUE) return StorageResult.fail("storage-meso-overflow");
        storage.setMeso((int) next);
        bot.gainMeso(-amount, false, true, false);
        bot.setUsedStorage();
        storage.sendMeso(bot.getClient());
        return snapshot(bot, "mesos-deposited", 0, amount);
    }

    public static StorageResult withdrawMesos(Character bot, int amount) {
        if (!sessionValid(bot)) return StorageResult.fail("storage-not-open");
        if (amount <= 0) return StorageResult.fail("invalid-mesos");
        Storage storage = bot.getStorage();
        if (storage.getMeso() < amount) return StorageResult.fail("insufficient-storage-mesos");
        long nextPlayer = (long) bot.getMeso() + amount;
        if (nextPlayer > Integer.MAX_VALUE) return StorageResult.fail("player-meso-overflow");
        storage.setMeso(storage.getMeso() - amount);
        bot.gainMeso(amount, false, true, false);
        bot.setUsedStorage();
        storage.sendMeso(bot.getClient());
        return snapshot(bot, "mesos-withdrawn", 0, amount);
    }

    public static StorageResult status(Character bot) {
        if (!eligible(bot) || bot.getStorage() == null) return StorageResult.fail("not-eligible");
        return snapshot(bot, bot.getStorage().isStorageOpen() ? "open" : "closed", 0, 0);
    }

    private static StorageResult snapshot(Character bot, String reason, int itemId, int amount) {
        Storage storage = bot.getStorage();
        return new StorageResult(true, storage.isStorageOpen(), storage.getItems().size(), storage.getSlots(),
                storage.getMeso(), bot.getMeso(), itemId, amount, reason);
    }

    private static boolean sessionValid(Character bot) {
        return eligible(bot) && bot.getStorage() != null && bot.getStorage().isStorageOpen()
                && bot.getStorage().getCurrentMapId() == bot.getMapId()
                && BotNpcDriver.findNpc(bot, bot.getStorage().getCurrentNpcid()) != null;
    }

    private static boolean eligible(Character bot) {
        return bot != null && BotHelpers.isBot(bot) && bot.getClient() != null && bot.isLoggedinWorld()
                && bot.getMap() != null && bot.getPosition() != null && bot.isAlive();
    }

    public record StorageResult(boolean success, boolean open, int itemCount, int slots, int storageMesos,
                                int playerMesos, int itemId, int amount, String reason) {
        static StorageResult fail(String reason) {
            return new StorageResult(false, false, 0, 0, 0, 0, 0, 0, reason);
        }
    }
}
