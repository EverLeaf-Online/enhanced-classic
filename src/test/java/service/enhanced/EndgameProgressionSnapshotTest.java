package service.enhanced;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class EndgameProgressionSnapshotTest {

    @Test
    void preEndgamePointsTowardLevel200() {
        EndgameProgressionSnapshot snapshot = EndgameProgressionSnapshot.forLevel(199);

        assertEquals(EndgameTierPolicy.Tier.PRE_ENDGAME, snapshot.tier());
        assertEquals(200, snapshot.nextMilestoneLevel());
        assertEquals(1, snapshot.levelsToNextMilestone());
        assertTrue(snapshot.unlocks().isEmpty());
        assertFalse(snapshot.atLevelCap());
    }

    @Test
    void tierOnePointsToward210AndIncludesEntryUnlocks() {
        EndgameProgressionSnapshot snapshot = EndgameProgressionSnapshot.forLevel(200);

        assertEquals(EndgameTierPolicy.Tier.TIER_1, snapshot.tier());
        assertEquals(210, snapshot.nextMilestoneLevel());
        assertEquals(10, snapshot.levelsToNextMilestone());
        assertTrue(snapshot.unlocks().contains(EndgameProgressionPolicy.Unlock.ENDGAME_QUESTLINE));
        assertTrue(snapshot.unlocks().contains(EndgameProgressionPolicy.Unlock.WEEKLY_OBJECTIVES));
    }

    @Test
    void levelCapHasNoNextMilestone() {
        EndgameProgressionSnapshot snapshot = EndgameProgressionSnapshot.forLevel(250);

        assertEquals(EndgameTierPolicy.Tier.TIER_5, snapshot.tier());
        assertNull(snapshot.nextMilestoneLevel());
        assertEquals(0, snapshot.levelsToNextMilestone());
        assertTrue(snapshot.atLevelCap());
        assertTrue(snapshot.unlocks().contains(EndgameProgressionPolicy.Unlock.CAPSTONE_REWARDS));
    }
}
