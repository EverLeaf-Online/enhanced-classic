package everleaf.progression;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class EndgameMilestoneCatalogTest {

    @Test
    void currentMilestoneTracksPost200Tiers() {
        assertEquals("rooted", EndgameMilestoneCatalog.currentForLevel(200).key());
        assertEquals("rooted", EndgameMilestoneCatalog.currentForLevel(209).key());
        assertEquals("awakened", EndgameMilestoneCatalog.currentForLevel(210).key());
        assertEquals("ascendant", EndgameMilestoneCatalog.currentForLevel(225).key());
        assertEquals("ancient", EndgameMilestoneCatalog.currentForLevel(240).key());
        assertEquals("evergreen", EndgameMilestoneCatalog.currentForLevel(250).key());
    }

    @Test
    void unlockTagsAccumulateInsteadOfReplacingPriorAccess() {
        assertTrue(EndgameMilestoneCatalog.hasUnlockTag(250, "rooted_bosses"));
        assertTrue(EndgameMilestoneCatalog.hasUnlockTag(250, "hard_mode_bosses"));
        assertTrue(EndgameMilestoneCatalog.hasUnlockTag(250, "evergreen_mastery"));
        assertFalse(EndgameMilestoneCatalog.hasUnlockTag(224, "hard_mode_bosses"));
    }

    @Test
    void contentGatesHonorMilestoneBoundaries() {
        var hard = EndgameContentCatalog.byId("hard_mode_boss_tier");
        assertFalse(hard.isAccessible(224));
        assertTrue(hard.isAccessible(225));

        var evergreen = EndgameContentCatalog.byId("evergreen_mastery");
        assertFalse(evergreen.isAccessible(249));
        assertTrue(evergreen.isAccessible(250));
    }

    @Test
    void preEndgameHasNoAccessiblePost200Content() {
        assertTrue(EndgameContentCatalog.accessibleAt(199).isEmpty());
        assertThrows(IllegalArgumentException.class, () -> EndgameMilestoneCatalog.currentForLevel(199));
    }
}
