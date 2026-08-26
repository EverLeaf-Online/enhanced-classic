package everleaf.progression;

import java.util.List;
import java.util.Set;

/**
 * Initial server-side Verdant Marks shop catalog.
 *
 * These entries intentionally describe reward contracts rather than concrete
 * Maple item IDs. Item/script bindings can be added behind fulfillment adapters
 * without changing pricing, eligibility, or anti-P2W policy.
 */
public final class VerdantRewardCatalog {
    private VerdantRewardCatalog() {
    }

    private static final List<VerdantRewardDefinition> REWARDS = List.of(
            new VerdantRewardDefinition(
                    "rooted_upgrade_bundle", "Rooted Upgrade Material Bundle",
                    VerdantRewardCategory.PROGRESSION_MATERIAL, 200, 80, 2,
                    Set.of("bound", "materials", "non-bis")
            ),
            new VerdantRewardDefinition(
                    "returning_adventurer_cache", "Returning Adventurer Catch-up Cache",
                    VerdantRewardCategory.CATCH_UP, 200, 60, 1,
                    Set.of("bound", "catch-up")
            ),
            new VerdantRewardDefinition(
                    "everleaf_style_token", "Everleaf Style Token",
                    VerdantRewardCategory.COSMETIC, 200, 45, null,
                    Set.of("cosmetic", "account-safe")
            ),
            new VerdantRewardDefinition(
                    "travel_utility_pack", "Travel Utility Pack",
                    VerdantRewardCategory.UTILITY, 200, 30, 3,
                    Set.of("utility", "non-power")
            ),
            new VerdantRewardDefinition(
                    "awakened_forge_component", "Awakened Forge Component",
                    VerdantRewardCategory.GEAR_COMPONENT, 210, 100, 1,
                    Set.of("bound", "component", "non-bis")
            ),
            new VerdantRewardDefinition(
                    "ascendant_forge_component", "Ascendant Forge Component",
                    VerdantRewardCategory.GEAR_COMPONENT, 225, 130, 1,
                    Set.of("bound", "component", "non-bis")
            ),
            new VerdantRewardDefinition(
                    "ancient_forge_component", "Ancient Forge Component",
                    VerdantRewardCategory.GEAR_COMPONENT, 240, 160, 1,
                    Set.of("bound", "component", "non-bis")
            ),
            new VerdantRewardDefinition(
                    "evergreen_prestige_token", "Evergreen Prestige Token",
                    VerdantRewardCategory.COSMETIC, 250, 150, null,
                    Set.of("cosmetic", "prestige")
            )
    );

    public static List<VerdantRewardDefinition> all() {
        return REWARDS;
    }

    public static List<VerdantRewardDefinition> eligibleForLevel(int level) {
        return REWARDS.stream().filter(reward -> reward.isEligible(level)).toList();
    }

    public static VerdantRewardDefinition byId(String id) {
        if (id == null || id.isBlank()) throw new IllegalArgumentException("id cannot be blank");
        return REWARDS.stream()
                .filter(reward -> reward.id().equals(id))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("unknown Verdant reward: " + id));
    }
}
