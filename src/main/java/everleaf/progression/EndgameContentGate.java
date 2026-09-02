package everleaf.progression;

import java.util.Set;

/**
 * Reusable access contract for post-200 content.
 * Concrete boss, PQ, quest, forge, and collection content can depend on this
 * instead of scattering raw level checks throughout scripts.
 */
public record EndgameContentGate(
        String id,
        String displayName,
        int minimumLevel,
        String requiredUnlockTag,
        Set<EndgameRewardLane> lanes
) {
    public EndgameContentGate {
        if (id == null || id.isBlank()) throw new IllegalArgumentException("id cannot be blank");
        if (displayName == null || displayName.isBlank()) throw new IllegalArgumentException("displayName cannot be blank");
        if (minimumLevel < 200 || minimumLevel > 250) throw new IllegalArgumentException("minimumLevel must be 200-250");
        if (requiredUnlockTag == null || requiredUnlockTag.isBlank()) throw new IllegalArgumentException("requiredUnlockTag cannot be blank");
        lanes = lanes == null ? Set.of() : Set.copyOf(lanes);
    }

    public boolean isAccessible(int level) {
        return level >= minimumLevel
                && level <= 250
                && EndgameMilestoneCatalog.hasUnlockTag(level, requiredUnlockTag);
    }
}
