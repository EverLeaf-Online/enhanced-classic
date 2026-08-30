package everleaf.progression;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class RootedZakumEntryValidatorTest {
    private static RootedZakumEntryValidator.Member member(int id, int level) {
        return new RootedZakumEntryValidator.Member(id, id, level, true);
    }

    @Test
    void acceptsThreeToSixEligiblePlayers() {
        assertTrue(RootedZakumEntryValidator.validate(List.of(member(1, 200), member(2, 210), member(3, 250))).allowed());
        assertTrue(RootedZakumEntryValidator.validate(List.of(member(1, 200), member(2, 200), member(3, 200), member(4, 200), member(5, 200), member(6, 200))).allowed());
    }

    @Test
    void rejectsUndersizedAndOversizedParties() {
        assertFalse(RootedZakumEntryValidator.validate(List.of(member(1, 200), member(2, 200))).allowed());
        assertFalse(RootedZakumEntryValidator.validate(List.of(member(1, 200), member(2, 200), member(3, 200), member(4, 200), member(5, 200), member(6, 200), member(7, 200))).allowed());
    }

    @Test
    void rejectsUnderleveledOrOfflineMembers() {
        assertFalse(RootedZakumEntryValidator.validate(List.of(member(1, 199), member(2, 200), member(3, 200))).allowed());
        var offline = new RootedZakumEntryValidator.Member(3, 3, 200, false);
        assertFalse(RootedZakumEntryValidator.validate(List.of(member(1, 200), member(2, 200), offline)).allowed());
    }

    @Test
    void weeklyAndPracticeModesRemainDistinct() {
        assertTrue(EnhancedBossRewardMode.WEEKLY_REWARD.grantsValuableRewards());
        assertFalse(EnhancedBossRewardMode.PRACTICE.grantsValuableRewards());
    }
}
