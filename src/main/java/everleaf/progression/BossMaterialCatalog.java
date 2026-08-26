package everleaf.progression;

import java.util.List;

/** Canonical symbolic materials earned from enhanced encounters. */
public final class BossMaterialCatalog {
    private BossMaterialCatalog() {}

    private static final List<BossMaterialDefinition> MATERIALS = List.of(
            new BossMaterialDefinition(
                    "rooted_ember", "Rooted Ember", "rooted_zakum",
                    EnhancedBossTier.ROOTED, true, true
            ),
            new BossMaterialDefinition(
                    "awakened_scale", "Awakened Scale", "awakened_horntail",
                    EnhancedBossTier.AWAKENED, true, true
            ),
            new BossMaterialDefinition(
                    "ascendant_fragment", "Ascendant Fragment", "ascendant_pink_bean",
                    EnhancedBossTier.ASCENDANT, true, true
            ),
            new BossMaterialDefinition(
                    "ancient_core", "Ancient Core", "ancient_pink_bean",
                    EnhancedBossTier.ANCIENT, true, true
            )
    );

    public static List<BossMaterialDefinition> all() { return MATERIALS; }

    public static BossMaterialDefinition forEncounter(String encounterId) {
        return MATERIALS.stream()
                .filter(material -> material.encounterId().equals(encounterId))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("no material for encounter: " + encounterId));
    }
}
