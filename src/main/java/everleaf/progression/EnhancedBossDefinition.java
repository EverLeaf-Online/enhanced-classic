package everleaf.progression;

import java.util.Set;

/**
 * Server-side contract for an enhanced encounter. Concrete monster/map IDs
 * live in adapters so progression policy stays testable without WZ assets.
 */
public record EnhancedBossDefinition(
        String id,
        String displayName,
        EnhancedBossTier tier,
        String classicEncounter,
        int partyMin,
        int partyMax,
        int timeLimitMinutes,
        Set<String> mechanics,
        Set<String> rewardTags
) {
    public EnhancedBossDefinition {
        if (id == null || id.isBlank()) throw new IllegalArgumentException("id cannot be blank");
        if (displayName == null || displayName.isBlank()) throw new IllegalArgumentException("displayName cannot be blank");
        if (tier == null) throw new IllegalArgumentException("tier cannot be null");
        if (partyMin < 1 || partyMax < partyMin) throw new IllegalArgumentException("invalid party size");
        if (timeLimitMinutes < 1) throw new IllegalArgumentException("time limit must be positive");
        mechanics = Set.copyOf(mechanics);
        rewardTags = Set.copyOf(rewardTags);
    }

    public boolean isLevelEligible(int level) {
        return level >= tier.requiredLevel();
    }
}
