package everleaf.progression;

/** Reward behavior for an enhanced encounter attempt. */
public enum EnhancedBossRewardMode {
    WEEKLY_REWARD,
    PRACTICE;

    public boolean grantsValuableRewards() {
        return this == WEEKLY_REWARD;
    }
}
