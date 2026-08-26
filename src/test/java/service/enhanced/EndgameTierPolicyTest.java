package service.enhanced;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class EndgameTierPolicyTest {

    @Test
    void resolvesMilestones() {
        assertEquals(EndgameTierPolicy.Tier.PRE_ENDGAME, EndgameTierPolicy.forLevel(199));
        assertEquals(EndgameTierPolicy.Tier.TIER_1, EndgameTierPolicy.forLevel(200));
        assertEquals(EndgameTierPolicy.Tier.TIER_2, EndgameTierPolicy.forLevel(210));
        assertEquals(EndgameTierPolicy.Tier.TIER_3, EndgameTierPolicy.forLevel(225));
        assertEquals(EndgameTierPolicy.Tier.TIER_4, EndgameTierPolicy.forLevel(240));
        assertEquals(EndgameTierPolicy.Tier.TIER_5, EndgameTierPolicy.forLevel(250));
    }

    @Test
    void tierChecksAreMonotonic() {
        assertFalse(EndgameTierPolicy.hasReached(199, EndgameTierPolicy.Tier.TIER_1));
        assertTrue(EndgameTierPolicy.hasReached(225, EndgameTierPolicy.Tier.TIER_1));
        assertTrue(EndgameTierPolicy.hasReached(225, EndgameTierPolicy.Tier.TIER_3));
        assertFalse(EndgameTierPolicy.hasReached(225, EndgameTierPolicy.Tier.TIER_4));
    }

    @Test
    void rejectsLevelsOutsideEnhancedClassicRange() {
        assertThrows(IllegalArgumentException.class, () -> EndgameTierPolicy.forLevel(0));
        assertThrows(IllegalArgumentException.class, () -> EndgameTierPolicy.forLevel(251));
    }
}
