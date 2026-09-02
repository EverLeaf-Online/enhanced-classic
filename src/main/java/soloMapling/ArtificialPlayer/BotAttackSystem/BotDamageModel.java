package soloMapling.ArtificialPlayer.BotAttackSystem;

import java.util.concurrent.ThreadLocalRandom;

public final class BotDamageModel {
    private BotDamageModel() {}

    private static final int[][] TIER_BAND = {
            {20, 40},
            {70, 160},
            {240, 620},
            {900, 2300},
            {2800, 6500},
    };

    private static final double LEVEL_RAMP_DIVISOR = 250.0;
    private static final int SINGLE_LINE_MAX_LINES = 2;
    private static final double SINGLE_LINE_MULT_MIN = 2.0;
    private static final double SINGLE_LINE_MULT_MAX = 2.5;

    public static int rollLine(int jobTier, int level, int numDamageLines) {
        int tier = Math.max(0, Math.min(TIER_BAND.length - 1, jobTier));
        int[] band = TIER_BAND[tier];
        ThreadLocalRandom rng = ThreadLocalRandom.current();
        int base = (band[0] >= band[1]) ? band[0] : rng.nextInt(band[0], band[1] + 1);
        if (level > 0) {
            base = (int) Math.round(base * (1.0 + level / LEVEL_RAMP_DIVISOR));
        }
        if (numDamageLines <= SINGLE_LINE_MAX_LINES) {
            double mult = SINGLE_LINE_MULT_MIN + rng.nextDouble() * (SINGLE_LINE_MULT_MAX - SINGLE_LINE_MULT_MIN);
            base = (int) Math.round(base * mult);
        }
        return Math.max(1, base);
    }
}
