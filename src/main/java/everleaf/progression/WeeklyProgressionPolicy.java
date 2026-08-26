package everleaf.progression;

import service.enhanced.EndgameTierPolicy;

/**
 * Predictable weekly progression budget for Everleaf endgame.
 *
 * Values are intentionally abstract points rather than a final player-facing
 * currency. Content can divide the budget across objectives without allowing
 * raw reward inflation to spread through scripts.
 */
public final class WeeklyProgressionPolicy {
    private WeeklyProgressionPolicy() {
    }

    public static int weeklyCorePoints(int level) {
        EndgameTierPolicy.Tier tier = EndgameTierPolicy.forLevel(level);
        return switch (tier) {
            case PRE_ENDGAME -> 0;
            case TIER_1 -> 100;
            case TIER_2 -> 120;
            case TIER_3 -> 140;
            case TIER_4 -> 160;
            case TIER_5 -> 180;
        };
    }

    public static int catchUpBankCap(int level) {
        int weekly = weeklyCorePoints(level);
        return weekly == 0 ? 0 : weekly * 2;
    }

    public static int maximumClaimablePoints(int level, int catchupPointsBank) {
        if (catchupPointsBank < 0) throw new IllegalArgumentException("catchupPointsBank cannot be negative");
        return weeklyCorePoints(level) + Math.min(catchupPointsBank, catchUpBankCap(level));
    }

    public static int remainingAccountBudget(int level, int catchupPointsBank, int alreadyClaimed) {
        if (alreadyClaimed < 0) throw new IllegalArgumentException("alreadyClaimed cannot be negative");
        return Math.max(0, maximumClaimablePoints(level, catchupPointsBank) - alreadyClaimed);
    }

    public static int objectivePointCap(int level) {
        int weekly = weeklyCorePoints(level);
        return weekly == 0 ? 0 : Math.max(25, weekly / 2);
    }

    public static int clampAward(int level, int requestedPoints) {
        if (requestedPoints <= 0) {
            return 0;
        }
        return Math.min(requestedPoints, objectivePointCap(level));
    }
}
