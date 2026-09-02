package server;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;

import client.Character;
import client.inventory.Inventory;
import client.inventory.InventoryType;
import client.inventory.Item;
import constants.inventory.ItemConstants;
import java.lang.reflect.Field;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

class WzDonorStagingItemSmokeTest {
    private static final int CARBONATED_DRINK = 2022711;
    private static final int ACORN = 2022712;

    @BeforeAll
    static void requireExplicitStagingOptIn() {
        Assumptions.assumeTrue(
                Boolean.getBoolean("wz-donor-staging-smoke"),
                "staging donor smoke is opt-in and must never run against canonical production implicitly");
        String wzPath = System.getProperty("wz-path");
        assertNotNull(wzPath, "wz-path must point at the disposable staged WZ tree");
        assertTrue(!wzPath.isBlank(), "wz-path must not be blank");
    }

    @Test
    void firstV95ConsumeBatchLoadsThroughRealServerProvider() {
        ItemInformationProvider ii = ItemInformationProvider.getInstance();

        assertEquals("Carbonated Drink", ii.getName(CARBONATED_DRINK));
        assertEquals("Acorn", ii.getName(ACORN));

        StatEffect drink = ii.getItemEffect(CARBONATED_DRINK);
        assertNotNull(drink, "Carbonated Drink effect must load from Item.wz spec");
        assertEquals(1000, drink.getHp());
        assertEquals(1000, drink.getMp());
        assertEquals(0.0, drink.getHpRate());
        assertEquals(0.0, drink.getMpRate());

        StatEffect acorn = ii.getItemEffect(ACORN);
        assertNotNull(acorn, "Acorn effect must load from Item.wz spec");
        assertEquals(70, acorn.getHp());
        assertEquals(70, acorn.getMp());
        assertEquals(0.0, acorn.getHpRate());
        assertEquals(0.0, acorn.getMpRate());

        assertEquals(-1, ii.getWholePrice(CARBONATED_DRINK));
        assertEquals(10, ii.getWholePrice(ACORN));
        assertEquals(100, ii.getSlotMax(null, CARBONATED_DRINK));
        assertEquals(20, ii.getSlotMax(null, ACORN));

        for (int itemId : new int[] {CARBONATED_DRINK, ACORN}) {
            assertEquals(InventoryType.USE, ItemConstants.getInventoryType(itemId));
            assertTrue(ItemConstants.isConsumable(itemId), "candidate must route through ordinary consumable handling");
            assertFalse(ItemConstants.isRechargeable(itemId), "candidate must not use throwing-star/bullet stack rules");
            assertFalse(ii.isQuestItem(itemId), "candidate must not become a quest item");
            assertFalse(ii.isPickupRestricted(itemId), "candidate must not become one-of-a-kind/pickup restricted");
            assertFalse(ii.isAccountRestricted(itemId), "candidate must not become account restricted");
            assertFalse(ii.isDropRestricted(itemId), "candidate must not become drop/trade restricted");
        }
    }

    @Test
    void firstV95ConsumeBatchUsesGenericUseInventoryStackAndTransferSemantics() {
        ItemInformationProvider ii = ItemInformationProvider.getInstance();
        Inventory use = new Inventory(null, InventoryType.USE, (byte) 24);

        Item acornA = new Item(ACORN, (short) 0, (short) 12);
        Item acornB = new Item(ACORN, (short) 0, (short) 15);
        assertEquals(InventoryType.USE, acornA.getInventoryType());
        assertFalse(acornA.isUntradeable());
        assertFalse(acornB.isUntradeable());
        short acornSlotA = use.addItem(acornA);
        short acornSlotB = use.addItem(acornB);
        assertTrue(acornSlotA > 0);
        assertTrue(acornSlotB > 0);

        use.move(acornSlotB, acornSlotA, ii.getSlotMax(null, ACORN));
        assertEquals(20, use.getItem(acornSlotA).getQuantity());
        assertEquals(7, use.getItem(acornSlotB).getQuantity());
        assertEquals(27, use.countById(ACORN));

        use.removeItem(acornSlotA, (short) 3, false);
        assertEquals(17, use.getItem(acornSlotA).getQuantity());
        assertEquals(24, use.countById(ACORN));

        Item persistedShape = use.getItem(acornSlotA).copy();
        assertEquals(ACORN, persistedShape.getItemId());
        assertEquals(17, persistedShape.getQuantity());
        assertEquals(InventoryType.USE, persistedShape.getInventoryType());
        assertFalse(persistedShape.isUntradeable());

        Item drinkA = new Item(CARBONATED_DRINK, (short) 0, (short) 60);
        Item drinkB = new Item(CARBONATED_DRINK, (short) 0, (short) 40);
        short drinkSlotA = use.addItem(drinkA);
        short drinkSlotB = use.addItem(drinkB);
        use.move(drinkSlotB, drinkSlotA, ii.getSlotMax(null, CARBONATED_DRINK));
        assertEquals(100, use.getItem(drinkSlotA).getQuantity());
        assertNull(use.getItem(drinkSlotB), "fully merged ordinary stack must release the source slot");
        assertEquals(100, use.countById(CARBONATED_DRINK));
    }

    @Test
    void firstV95ConsumeBatchUsesGenericStorageMergeSemantics() throws Exception {
        StorageInventory acornStorage = new StorageInventory(null, List.of(
                new Item(ACORN, (short) 0, (short) 12),
                new Item(ACORN, (short) 0, (short) 15)));
        acornStorage.mergeItems();
        Map<Short, Item> acornItems = storageItems(acornStorage);
        assertEquals(2, acornItems.size());
        assertEquals(20, acornItems.get((short) 1).getQuantity());
        assertEquals(7, acornItems.get((short) 2).getQuantity());

        StorageInventory drinkStorage = new StorageInventory(null, List.of(
                new Item(CARBONATED_DRINK, (short) 0, (short) 60),
                new Item(CARBONATED_DRINK, (short) 0, (short) 40)));
        drinkStorage.mergeItems();
        Map<Short, Item> drinkItems = storageItems(drinkStorage);
        assertEquals(1, drinkItems.size(), "full storage merge must release the second slot");
        assertEquals(100, drinkItems.get((short) 1).getQuantity());
        assertFalse(drinkItems.get((short) 1).isUntradeable());
    }

    @Test
    void firstV95ConsumeBatchPassesDirectTradeAndPlayerShopEligibilityGates() {
        ItemInformationProvider ii = ItemInformationProvider.getInstance();
        Character character = mock(Character.class);
        Trade trade = new Trade((byte) 0, character);

        Item drink = new Item(CARBONATED_DRINK, (short) 1, (short) 6);
        Item acorn = new Item(ACORN, (short) 2, (short) 9);
        for (Item item : new Item[] {drink, acorn}) {
            assertFalse(ii.isUnmerchable(item.getItemId()), "ordinary v95 consume must not be blocked from trade/shops");
            assertFalse(ii.isDropRestricted(item.getItemId()), "ordinary v95 consume must not require karma for trade");
            assertFalse(item.isUntradeable(), "ordinary v95 consume must remain directly tradeable");
            assertTrue(trade.addItem(item.copy()), "real Trade container must accept the staged item copy");
        }

        List<Item> queued = trade.getItems();
        assertEquals(2, queued.size());
        assertEquals(CARBONATED_DRINK, queued.get(0).getItemId());
        assertEquals(6, queued.get(0).getQuantity());
        assertEquals(InventoryType.USE, queued.get(0).getInventoryType());
        assertEquals(ACORN, queued.get(1).getItemId());
        assertEquals(9, queued.get(1).getQuantity());
        assertEquals(InventoryType.USE, queued.get(1).getInventoryType());
    }

    @SuppressWarnings("unchecked")
    private static Map<Short, Item> storageItems(StorageInventory storage) throws Exception {
        Field field = StorageInventory.class.getDeclaredField("inventory");
        field.setAccessible(true);
        return (Map<Short, Item>) field.get(storage);
    }
}
