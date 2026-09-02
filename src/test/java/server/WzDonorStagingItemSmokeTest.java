package server;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockStatic;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import client.inventory.Inventory;
import client.inventory.InventoryType;
import client.inventory.Item;
import client.inventory.ItemFactory;
import constants.inventory.ItemConstants;
import java.lang.reflect.Field;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;
import tools.DatabaseConnection;
import tools.Pair;

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
    void firstV95ConsumeBatchReconstructsThroughRealItemFactoryLoadPath() throws Exception {
        verifyLoadedItems(ItemFactory.INVENTORY, 31001);
        verifyLoadedItems(ItemFactory.STORAGE, 41001);
    }

    private static void verifyLoadedItems(ItemFactory factory, int ownerId) throws Exception {
        Connection connection = mock(Connection.class);
        PreparedStatement statement = mock(PreparedStatement.class);
        ResultSet resultSet = mock(ResultSet.class);

        when(connection.prepareStatement(anyString())).thenReturn(statement);
        when(statement.executeQuery()).thenReturn(resultSet);
        when(resultSet.next()).thenReturn(true, true, false);
        when(resultSet.getByte("inventorytype")).thenReturn(InventoryType.USE.getType(), InventoryType.USE.getType());
        when(resultSet.getInt("petid")).thenReturn(0, 0);
        when(resultSet.wasNull()).thenReturn(true, true);
        when(resultSet.getInt("itemid")).thenReturn(CARBONATED_DRINK, ACORN);
        when(resultSet.getInt("position")).thenReturn(3, 8);
        when(resultSet.getInt("quantity")).thenReturn(7, 19);
        when(resultSet.getString("owner")).thenReturn("", "EverLeaf");
        when(resultSet.getLong("expiration")).thenReturn(-1L, 1_900_000_000_000L);
        when(resultSet.getString("giftFrom")).thenReturn("", "staging");
        when(resultSet.getInt("flag")).thenReturn(0, 0);

        try (MockedStatic<DatabaseConnection> database = mockStatic(DatabaseConnection.class)) {
            database.when(DatabaseConnection::getConnection).thenReturn(connection);
            List<Pair<Item, InventoryType>> loaded = factory.loadItems(ownerId, false);

            assertEquals(2, loaded.size());
            assertLoadedItem(loaded.get(0), CARBONATED_DRINK, 3, 7, "", -1L, "");
            assertLoadedItem(loaded.get(1), ACORN, 8, 19, "EverLeaf", 1_900_000_000_000L, "staging");
        }

        verify(statement).setInt(1, factory.getValue());
        verify(statement).setInt(2, ownerId);
        verify(statement).executeQuery();
    }

    private static void assertLoadedItem(
            Pair<Item, InventoryType> pair,
            int itemId,
            int position,
            int quantity,
            String owner,
            long expiration,
            String giftFrom) {
        Item item = pair.getLeft();
        assertEquals(InventoryType.USE, pair.getRight());
        assertEquals(itemId, item.getItemId());
        assertEquals(position, item.getPosition());
        assertEquals(quantity, item.getQuantity());
        assertEquals(owner, item.getOwner());
        assertEquals(expiration, item.getExpiration());
        assertEquals(giftFrom, item.getGiftFrom());
        assertEquals(0, item.getFlag());
        assertEquals(-1, item.getPetId());
        assertFalse(item.isUntradeable());
    }

    @SuppressWarnings("unchecked")
    private static Map<Short, Item> storageItems(StorageInventory storage) throws Exception {
        Field field = StorageInventory.class.getDeclaredField("inventory");
        field.setAccessible(true);
        return (Map<Short, Item>) field.get(storage);
    }
}
