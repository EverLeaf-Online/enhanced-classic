package everleaf.progression;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class WeeklyProgressionPolicyTest {

    @Test
    void preEndgameHasNoWeeklyBudget() {
        assertEquals(0, WeeklyProgressionPolicy.weeklyCorePoints(199));
        assertEquals(0, WeeklyProgressionPolicy.catchUpBankCap(199));
        assertEquals(0, WeeklyProgressionPolicy.objectivePointCap(199));
    }

    @Test
    void budgetsIncreaseByTierWithoutExploding() {
        assertEquals(100, WeeklyProgressionPolicy.weeklyCorePoints(200));
        assertEquals(120, WeeklyProgressionPolicy.weeklyCorePoints(210));
        assertEquals(140, WeeklyProgressionPolicy.weeklyCorePoints(225));
        assertEquals(160, WeeklyProgressionPolicy.weeklyCorePoints(240));
        assertEquals(180, WeeklyProgressionPolicy.weeklyCorePoints(250));
    }

    @Test
    void catchUpBankIsTwoWeeksOfCoreProgress() {
        assertEquals(200, WeeklyProgressionPolicy.catchUpBankCap(200));
        assertEquals(360, WeeklyProgressionPolicy.catchUpBankCap(250));
    }

    @Test
    void singleObjectiveCannotConsumeWholeWeeklyBudget() {
        assertEquals(50, WeeklyProgressionPolicy.objectivePointCap(200));
        assertEquals(90, WeeklyProgressionPolicy.objectivePointCap(250));
        assertEquals(50, WeeklyProgressionPolicy.clampAward(200, 500));
        assertEquals(0, WeeklyProgressionPolicy.clampAward(200, -5));
    }
}
