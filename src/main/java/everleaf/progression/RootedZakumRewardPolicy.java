package everleaf.progression;

import java.util.Map;

/** Reward contract for Rooted Zakum. Practice runs intentionally return no valuable progression rewards. */
public final class RootedZakumRewardPolicy {
    private RootedZakumRewardPolicy() {}

    public record RewardBundle(int verdantMarks, Map<RootedMaterial, Integer> materials) {
        public RewardBundle {
            if (verdantMarks < 0) throw new IllegalArgumentException("verdantMarks cannot be negative");
            materials = Map.copyOf(materials);
            if (materials.values().stream().anyMatch(v -> v == null || v < 0)) {
                throw new IllegalArgumentException("material quantities cannot be negative");
            }
        }
    }

    private static final RewardBundle WEEKLY_CLEAR = new RewardBundle(
            20,
            Map.of(
                    RootedMaterial.EMBER_CORE, 2,
                    RootedMaterial.ANCIENT_BARK, 1
            )
    );

    private static final RewardBundle PRACTICE_CLEAR = new RewardBundle(0, Map.of());

    public static RewardBundle forMode(EnhancedBossRewardMode mode) {
        if (mode == null) throw new IllegalArgumentException("mode cannot be null");
        return mode.grantsValuableRewards() ? WEEKLY_CLEAR : PRACTICE_CLEAR;
    }
}
