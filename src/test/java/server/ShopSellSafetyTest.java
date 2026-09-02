package server;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ShopSellSafetyTest {
    @Test
    void missingItemPriceIsNotAValidSaleValue() {
        assertFalse(Shop.isValidSellPrice(-1));
    }

    @Test
    void explicitZeroAndPositivePricesRemainValidSaleValues() {
        assertTrue(Shop.isValidSellPrice(0));
        assertTrue(Shop.isValidSellPrice(1));
        assertTrue(Shop.isValidSellPrice(10));
    }
}
