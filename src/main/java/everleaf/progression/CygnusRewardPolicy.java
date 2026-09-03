package everleaf.progression;

/** Controlled weekly rare-scroll policy for the final Fallen Cygnus body. */
public final class CygnusRewardPolicy {
    public static final int ROLL_SCALE = 1_000_000;
    public static final int WHITE_SCROLL_CHANCE = 5_000;   // 0.5%
    public static final int CHAOS_SCROLL_CHANCE = 50_000;  // 5.0%
    public static final int CHAOS_SCROLL = 2_049_100;
    public static final int WHITE_SCROLL = 2_340_000;

    private CygnusRewardPolicy() {}

    public enum RareReward {
        NONE(0), CHAOS_SCROLL(CygnusRewardPolicy.CHAOS_SCROLL), WHITE_SCROLL(CygnusRewardPolicy.WHITE_SCROLL);

        private final int itemId;
        RareReward(int itemId) { this.itemId = itemId; }
        public int itemId() { return itemId; }
    }

    /** roll must be in [0, ROLL_SCALE). White is deliberately ten times rarer than Chaos. */
    public static RareReward roll(int roll) {
        if (roll < 0 || roll >= ROLL_SCALE) throw new IllegalArgumentException("roll out of range");
        if (roll < WHITE_SCROLL_CHANCE) return RareReward.WHITE_SCROLL;
        if (roll < WHITE_SCROLL_CHANCE + CHAOS_SCROLL_CHANCE) return RareReward.CHAOS_SCROLL;
        return RareReward.NONE;
    }
}
