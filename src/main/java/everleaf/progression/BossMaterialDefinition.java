package everleaf.progression;

/**
 * Symbolic boss material contract. Concrete Maple item IDs are intentionally
 * bound later so progression/economy rules can be tested without WZ changes.
 */
public record BossMaterialDefinition(
        String id,
        String displayName,
        String encounterId,
        EnhancedBossTier tier,
        boolean accountBound,
        boolean weeklyLimited
) {
    public BossMaterialDefinition {
        if (id == null || id.isBlank()) throw new IllegalArgumentException("id cannot be blank");
        if (displayName == null || displayName.isBlank()) throw new IllegalArgumentException("displayName cannot be blank");
        if (encounterId == null || encounterId.isBlank()) throw new IllegalArgumentException("encounterId cannot be blank");
        if (tier == null) throw new IllegalArgumentException("tier cannot be null");
    }
}
