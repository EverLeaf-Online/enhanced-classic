package service.enhanced;

/**
 * Shared Enhanced Classic endgame progression tiers.
 *
 * <p>Boss access, high-level quests, gear progression, achievements and weekly
 * objectives should depend on these tiers rather than scattering raw level
 * checks throughout scripts.</p>
 */
public final class EndgameTierPolicy {

    private EndgameTierPolicy() {
    }

    public enum Tier {
        PRE_ENDGAME(0, 1),
        TIER_1(200, 1),
        TIER_2(210, 2),
        TIER_3(225, 3),
        TIER_4(240, 4),
        TIER_5(250, 5);

        private final int minimumLevel;
        private final int rank;

        Tier(int minimumLevel, int rank) {
            this.minimumLevel = minimumLevel;
            this.rank = rank;
        }

        public int minimumLevel() {
            return minimumLevel;
        }

        public int rank() {
            return rank;
        }
    }

    public static Tier forLevel(int level) {
        if (level < 1 || level > LevelCapPolicy.PLAYER_MAX_LEVEL) {
            throw new IllegalArgumentException("level must be between 1 and " + LevelCapPolicy.PLAYER_MAX_LEVEL);
        }
        if (level >= 250) return Tier.TIER_5;
        if (level >= 240) return Tier.TIER_4;
        if (level >= 225) return Tier.TIER_3;
        if (level >= 210) return Tier.TIER_2;
        if (level >= 200) return Tier.TIER_1;
        return Tier.PRE_ENDGAME;
    }

    public static boolean hasReached(int level, Tier tier) {
        if (tier == null) {
            throw new IllegalArgumentException("tier cannot be null");
        }
        return forLevel(level).rank() >= tier.rank();
    }
}
