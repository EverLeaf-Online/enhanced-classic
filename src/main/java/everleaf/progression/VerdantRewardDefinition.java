package everleaf.progression;

import java.util.Set;

/**
 * Catalog definition for a Verdant Marks reward.
 *
 * Direct best-in-slot equipment is deliberately unrepresentable: rewards may
 * supply components/materials, but not a finished BiS item.
 */
public record VerdantRewardDefinition(
        String id,
        String displayName,
        VerdantRewardCategory category,
        int minimumLevel,
        int price,
        Integer weeklyAccountLimit,
        Set<String> tags
) {
    public VerdantRewardDefinition {
        if (id == null || id.isBlank()) throw new IllegalArgumentException("id cannot be blank");
        if (displayName == null || displayName.isBlank()) throw new IllegalArgumentException("displayName cannot be blank");
        if (category == null) throw new IllegalArgumentException("category cannot be null");
        if (minimumLevel < 200 || minimumLevel > 250) throw new IllegalArgumentException("minimumLevel must be 200-250");
        if (price <= 0) throw new IllegalArgumentException("price must be positive");
        if (weeklyAccountLimit != null && weeklyAccountLimit <= 0) {
            throw new IllegalArgumentException("weeklyAccountLimit must be positive when present");
        }
        tags = tags == null ? Set.of() : Set.copyOf(tags);
        if (tags.contains("direct-bis") || tags.contains("pay-to-win")) {
            throw new IllegalArgumentException("Verdant rewards cannot be direct BiS or pay-to-win");
        }
    }

    public boolean isEligible(int level) {
        return level >= minimumLevel && level <= 250;
    }
}
