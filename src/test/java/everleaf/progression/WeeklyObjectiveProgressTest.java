package everleaf.progression;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class WeeklyObjectiveProgressTest {

    @Test
    void progressClampsToTarget() {
        WeeklyObjectiveProgress progress = WeeklyObjectiveProgress
                .fresh("2026-08-24", "rooted_boss_hunt")
                .addProgress(99);
        assertEquals(3, progress.progress());
        assertTrue(progress.complete());
    }

    @Test
    void incompleteObjectiveCannotBeClaimed() {
        WeeklyObjectiveProgress progress = WeeklyObjectiveProgress
                .fresh("2026-08-24", "rooted_boss_hunt")
                .addProgress(2);
        assertThrows(IllegalStateException.class, progress::claim);
    }

    @Test
    void completedObjectiveCanBeClaimedOnce() {
        WeeklyObjectiveProgress complete = WeeklyObjectiveProgress
                .fresh("2026-08-24", "rooted_boss_hunt")
                .addProgress(3);
        WeeklyObjectiveProgress claimed = complete.claim();
        assertTrue(claimed.claimed());
        assertSame(claimed, claimed.claim());
        assertSame(claimed, claimed.addProgress(1));
    }

    @Test
    void constructorRejectsInvalidState() {
        assertThrows(IllegalArgumentException.class,
                () -> new WeeklyObjectiveProgress("2026-08-24", "rooted_boss_hunt", 4, false));
        assertThrows(IllegalArgumentException.class,
                () -> new WeeklyObjectiveProgress("2026-08-24", "rooted_boss_hunt", 2, true));
    }
}
