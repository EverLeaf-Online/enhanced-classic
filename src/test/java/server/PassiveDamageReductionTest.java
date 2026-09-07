package server;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class PassiveDamageReductionTest {
    @Test void liveHighDefenseAndAchillesWzLevelsReduceDamage() {
        assertEquals(9950, PassiveDamageReduction.apply(10000, 995));
        assertEquals(9500, PassiveDamageReduction.apply(10000, 950));
        assertEquals(9000, PassiveDamageReduction.apply(10000, 900));
        assertEquals(8500, PassiveDamageReduction.apply(10000, 850));
    }
    @Test void roundsDamageAfterMultiplicationRatherThanRoundingTheMultiplier() {
        assertEquals(85, PassiveDamageReduction.apply(101, 850));
        assertEquals(0, PassiveDamageReduction.apply(1, 995));
    }
    @Test void capsDoNotOverflowOrAmplifyDamage() {
        assertEquals(1825361099, PassiveDamageReduction.apply(Integer.MAX_VALUE, 850));
        assertEquals(100, PassiveDamageReduction.apply(100, 1200));
        assertEquals(0, PassiveDamageReduction.apply(100, -1));
        assertEquals(0, PassiveDamageReduction.apply(0, 850));
        assertEquals(-1, PassiveDamageReduction.apply(-1, 850));
    }
}
