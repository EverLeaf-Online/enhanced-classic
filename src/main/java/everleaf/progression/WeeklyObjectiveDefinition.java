package everleaf.progression;

import java.util.Set;

/** Immutable definition for a weekly objective template. */
public record WeeklyObjectiveDefinition(
        String id,
        String displayName,
        EndgameRewardLane lane,
        int minimumLevel,
        int targetCount,
        int pointReward,
        Set<String> tags
) {
    public WeeklyObjectiveDefinition {
        if (id == null || id.isBlank()) throw new IllegalArgumentException("id cannot be blank");
        if (displayName == null || displayName.isBlank()) throw new IllegalArgumentException("displayName cannot be blank");
        if (lane == null) throw new IllegalArgumentException("lane cannot be null");
        if (minimumLevel < 200 || minimumLevel > 250) throw new IllegalArgumentException("minimumLevel must be 200-250");
        if (targetCount < 1) throw new IllegalArgumentException("targetCount must be positive");
        if (pointReward < 1) throw new IllegalArgumentException("pointReward must be positive");
        tags = tags == null ? Set.of() : Set.copyOf(tags);
    }

    public boolean isEligible(int level) {
        return level >= minimumLevel && level <= 250
                && EndgameTierProfile.forLevel(level).supports(lane);
    }
}
