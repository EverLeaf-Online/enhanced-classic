package everleaf.progression;

import java.util.Set;

/** Immutable Everleaf post-200 milestone contract. */
public record EndgameMilestone(
        int level,
        String key,
        String displayName,
        String titleReward,
        Set<EndgameRewardLane> unlockedLanes,
        Set<String> unlockTags
) {
    public EndgameMilestone {
        if (level < 200 || level > 250) throw new IllegalArgumentException("milestone level must be 200-250");
        if (key == null || key.isBlank()) throw new IllegalArgumentException("key cannot be blank");
        if (displayName == null || displayName.isBlank()) throw new IllegalArgumentException("displayName cannot be blank");
        if (titleReward == null || titleReward.isBlank()) throw new IllegalArgumentException("titleReward cannot be blank");
        unlockedLanes = unlockedLanes == null ? Set.of() : Set.copyOf(unlockedLanes);
        unlockTags = unlockTags == null ? Set.of() : Set.copyOf(unlockTags);
    }

    public boolean reachedBy(int characterLevel) {
        return characterLevel >= level && characterLevel <= 250;
    }
}
