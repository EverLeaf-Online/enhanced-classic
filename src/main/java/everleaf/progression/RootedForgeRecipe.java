package everleaf.progression;

import java.util.Map;

/** Initial forge recipes unlocked by the Rooted milestone. */
public enum RootedForgeRecipe {
    ROOTED_WEAPON_REFINEMENT(
            "Rooted Weapon Refinement",
            Map.of(RootedMaterial.EMBER_CORE, 6, RootedMaterial.ANCIENT_BARK, 3),
            60
    ),
    ROOTED_ARMOR_REFINEMENT(
            "Rooted Armor Refinement",
            Map.of(RootedMaterial.EMBER_CORE, 4, RootedMaterial.ANCIENT_BARK, 4),
            45
    );

    private final String displayName;
    private final Map<RootedMaterial, Integer> materialCosts;
    private final int verdantMarkCost;

    RootedForgeRecipe(String displayName, Map<RootedMaterial, Integer> materialCosts, int verdantMarkCost) {
        this.displayName = displayName;
        this.materialCosts = Map.copyOf(materialCosts);
        this.verdantMarkCost = verdantMarkCost;
    }

    public String displayName() { return displayName; }
    public Map<RootedMaterial, Integer> materialCosts() { return materialCosts; }
    public int verdantMarkCost() { return verdantMarkCost; }

    public boolean directlyGrantsBestInSlot() {
        return false;
    }
}
