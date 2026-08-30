package everleaf.progression;

import java.util.List;
import java.util.Set;

/**
 * Initial hybrid encounter plan. Names intentionally reference classic
 * encounters while concrete monster/map bindings remain adapter-driven.
 */
public final class EnhancedBossCatalog {
    private EnhancedBossCatalog() {}

    private static final List<EnhancedBossDefinition> ENCOUNTERS = List.of(
            new EnhancedBossDefinition(
                    "rooted_zakum", "Rooted Zakum", EnhancedBossTier.ROOTED, "Zakum",
                    3, 6, 30,
                    Set.of("arm-pressure", "add-waves", "anti-burst-window"),
                    Set.of("boss-material", "rooted", "weekly")
            ),
            new EnhancedBossDefinition(
                    "awakened_horntail", "Awakened Horntail", EnhancedBossTier.AWAKENED, "Horntail",
                    4, 6, 40,
                    Set.of("body-order", "dispel-pressure", "add-waves", "phase-enrage"),
                    Set.of("boss-material", "awakened", "forge-component")
            ),
            new EnhancedBossDefinition(
                    "ascendant_pink_bean", "Ascendant Pink Bean", EnhancedBossTier.ASCENDANT, "Pink Bean",
                    4, 6, 45,
                    Set.of("statue-sequence", "damage-check", "add-waves", "hard-enrage"),
                    Set.of("boss-material", "ascendant", "forge-component", "mastery")
            ),
            new EnhancedBossDefinition(
                    "ancient_pink_bean", "Ancient Pink Bean", EnhancedBossTier.ANCIENT, "Pink Bean",
                    5, 6, 40,
                    Set.of("accelerated-phases", "punishing-dispel", "hard-enrage", "limited-recovery"),
                    Set.of("boss-material", "ancient", "capstone-component", "prestige")
            )
    );

    public static List<EnhancedBossDefinition> all() { return ENCOUNTERS; }

    public static List<EnhancedBossDefinition> eligibleForLevel(int level) {
        return ENCOUNTERS.stream().filter(encounter -> encounter.isLevelEligible(level)).toList();
    }

    public static EnhancedBossDefinition byId(String id) {
        return ENCOUNTERS.stream()
                .filter(encounter -> encounter.id().equals(id))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("unknown enhanced boss: " + id));
    }
}
