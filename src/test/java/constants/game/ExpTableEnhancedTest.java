package constants.game;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class ExpTableEnhancedTest {

    @Test
    void post200CurveStartsAtExpectedDevelopmentTarget() {
        assertEquals(1_700_000_000, ExpTable.getExpNeededForLevel(201));
    }

    @Test
    void post200CurveIsMonotonicThrough249() {
        int previous = ExpTable.getExpNeededForLevel(200);
        for (int level = 201; level < 250; level++) {
            int current = ExpTable.getExpNeededForLevel(level);
            assertTrue(current > previous, "EXP must increase at level " + level);
            assertTrue(current <= 2_000_000_000, "EXP must stay int-safe at level " + level);
            previous = current;
        }
    }

    @Test
    void level250UsesCapSentinel() {
        assertEquals(Integer.MAX_VALUE, ExpTable.getExpNeededForLevel(250));
    }
}
