package constants.inventory;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ItemConstantsTest {

    @Test
    void townScrollClassificationStaysInside203Family() {
        assertTrue(ItemConstants.isTownScroll(2030000));
        assertTrue(ItemConstants.isTownScroll(2039999));
        assertFalse(ItemConstants.isTownScroll(2029999));
        assertFalse(ItemConstants.isTownScroll(2040000));
        assertFalse(ItemConstants.isTownScroll(2049100));
    }

    @Test
    void rechargeableFamiliesRemainDistinct() {
        assertTrue(ItemConstants.isThrowingStar(2070000));
        assertTrue(ItemConstants.isBullet(2330000));
        assertTrue(ItemConstants.isRechargeable(2070000));
        assertTrue(ItemConstants.isRechargeable(2330000));
        assertFalse(ItemConstants.isRechargeable(2060000));
    }

    @Test
    void upgradeScrollFamiliesAreRecognized() {
        assertTrue(ItemConstants.isCleanSlate(2049000));
        assertTrue(ItemConstants.isChaosScroll(2049100));
        assertFalse(ItemConstants.isCleanSlate(2049100));
        assertFalse(ItemConstants.isChaosScroll(2049000));
    }
}
