package everleaf.progression;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class EnhancedBossCatalogTest {
    @Test
    void tierBoundariesMatchEndgameMilestones() {
        assertThrows(IllegalArgumentException.class, () -> EnhancedBossTier.forLevel(199));
        assertEquals(EnhancedBossTier.ROOTED, EnhancedBossTier.forLevel(200));
        assertEquals(EnhancedBossTier.AWAKENED, EnhancedBossTier.forLevel(210));
        assertEquals(EnhancedBossTier.ASCENDANT, EnhancedBossTier.forLevel(225));
        assertEquals(EnhancedBossTier.ANCIENT, EnhancedBossTier.forLevel(240));
        assertEquals(EnhancedBossTier.EVERGREEN, EnhancedBossTier.forLevel(250));
    }

    @Test
    void laterLevelsRetainEarlierEncounterAccess() {
        assertEquals(1, EnhancedBossCatalog.eligibleForLevel(200).size());
        assertEquals(2, EnhancedBossCatalog.eligibleForLevel(210).size());
        assertEquals(3, EnhancedBossCatalog.eligibleForLevel(225).size());
        assertEquals(4, EnhancedBossCatalog.eligibleForLevel(240).size());
        assertEquals(4, EnhancedBossCatalog.eligibleForLevel(250).size());
    }

    @Test
    void catalogDoesNotSellBestInSlotPower() {
        for (EnhancedBossDefinition encounter : EnhancedBossCatalog.all()) {
            assertFalse(encounter.rewardTags().contains("donation"));
            assertFalse(encounter.rewardTags().contains("cash-shop"));
        }
    }
}
