package service.enhanced;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class EndgameProgressionPolicyTest {

    @Test
    void preEndgameHasNoEndgameUnlocks() {
        assertTrue(EndgameProgressionPolicy.unlocksForLevel(199).isEmpty());
    }

    @Test
    void level200StartsEndgameAndWeeklies() {
        assertTrue(EndgameProgressionPolicy.isUnlocked(200,
                EndgameProgressionPolicy.Unlock.ENDGAME_QUESTLINE));
        assertTrue(EndgameProgressionPolicy.isUnlocked(200,
                EndgameProgressionPolicy.Unlock.WEEKLY_OBJECTIVES));
        assertFalse(EndgameProgressionPolicy.isUnlocked(200,
                EndgameProgressionPolicy.Unlock.ADVANCED_BOSS_TRACK));
    }

    @Test
    void level225IncludesEarlierUnlocksAndGearTrack() {
        assertTrue(EndgameProgressionPolicy.isUnlocked(225,
                EndgameProgressionPolicy.Unlock.ADVANCED_BOSS_TRACK));
        assertTrue(EndgameProgressionPolicy.isUnlocked(225,
                EndgameProgressionPolicy.Unlock.HIGH_END_BOSS_TRACK));
        assertTrue(EndgameProgressionPolicy.isUnlocked(225,
                EndgameProgressionPolicy.Unlock.ADVANCED_GEAR_TRACK));
        assertFalse(EndgameProgressionPolicy.isUnlocked(225,
                EndgameProgressionPolicy.Unlock.CAPSTONE_REWARDS));
    }

    @Test
    void level250IncludesCapstoneUnlocks() {
        assertTrue(EndgameProgressionPolicy.isUnlocked(250,
                EndgameProgressionPolicy.Unlock.CAPSTONE_QUESTLINE));
        assertTrue(EndgameProgressionPolicy.isUnlocked(250,
                EndgameProgressionPolicy.Unlock.CAPSTONE_REWARDS));
        assertTrue(EndgameProgressionPolicy.isUnlocked(250,
                EndgameProgressionPolicy.Unlock.ENDGAME_QUESTLINE));
    }
}
