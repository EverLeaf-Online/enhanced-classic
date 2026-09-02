package server;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;

import client.Character;
import client.inventory.InventoryType;
import client.inventory.Item;
import java.util.List;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

class WzDonorStagingTradeSmokeTest {
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
}
