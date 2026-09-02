package server;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

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

        // The donor data intentionally omits a price for Carbonated Drink and explicitly sets Acorn to 10.
        assertEquals(-1, ii.getWholePrice(CARBONATED_DRINK));
        assertEquals(10, ii.getWholePrice(ACORN));

        // Acorn explicitly declares slotMax=20. Null Client is safe for non-rechargeable consumables.
        assertEquals(20, ii.getSlotMax(null, ACORN));

        // Both candidates survived the profiler specifically because they carry no special transfer/system flags.
        for (int itemId : new int[] {CARBONATED_DRINK, ACORN}) {
            assertFalse(ii.isQuestItem(itemId), "candidate must not become a quest item");
            assertFalse(ii.isPickupRestricted(itemId), "candidate must not become one-of-a-kind/pickup restricted");
            assertFalse(ii.isAccountRestricted(itemId), "candidate must not become account restricted");
            assertFalse(ii.isDropRestricted(itemId), "candidate must not become drop/trade restricted");
        }
    }
}
