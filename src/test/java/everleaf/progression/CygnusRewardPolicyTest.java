package everleaf.progression;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class CygnusRewardPolicyTest {
    @Test
    void whiteScrollIsTenTimesRarerThanChaosAndThresholdsDoNotOverlap() {
        assertEquals(CygnusRewardPolicy.RareReward.WHITE_SCROLL, CygnusRewardPolicy.roll(0));
        assertEquals(CygnusRewardPolicy.RareReward.WHITE_SCROLL,
                CygnusRewardPolicy.roll(CygnusRewardPolicy.WHITE_SCROLL_CHANCE - 1));
        assertEquals(CygnusRewardPolicy.RareReward.CHAOS_SCROLL,
                CygnusRewardPolicy.roll(CygnusRewardPolicy.WHITE_SCROLL_CHANCE));
        assertEquals(CygnusRewardPolicy.RareReward.CHAOS_SCROLL,
                CygnusRewardPolicy.roll(CygnusRewardPolicy.WHITE_SCROLL_CHANCE + CygnusRewardPolicy.CHAOS_SCROLL_CHANCE - 1));
        assertEquals(CygnusRewardPolicy.RareReward.NONE,
                CygnusRewardPolicy.roll(CygnusRewardPolicy.WHITE_SCROLL_CHANCE + CygnusRewardPolicy.CHAOS_SCROLL_CHANCE));
        assertEquals(10, CygnusRewardPolicy.CHAOS_SCROLL_CHANCE / CygnusRewardPolicy.WHITE_SCROLL_CHANCE);
    }

    @Test
    void rejectsOutOfRangeRolls() {
        assertThrows(IllegalArgumentException.class, () -> CygnusRewardPolicy.roll(-1));
        assertThrows(IllegalArgumentException.class, () -> CygnusRewardPolicy.roll(CygnusRewardPolicy.ROLL_SCALE));
    }
}
