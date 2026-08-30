package everleaf.progression;

import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class RootedForgePolicyTest {
    @Test
    void acceptsExactWeaponRefinementCost() {
        var recipe = RootedForgeRecipe.ROOTED_WEAPON_REFINEMENT;
        var check = RootedForgePolicy.canCraft(
                recipe,
                recipe.verdantMarkCost(),
                Map.of(RootedMaterial.EMBER_CORE, 6, RootedMaterial.ANCIENT_BARK, 3)
        );
        assertTrue(check.allowed());
    }

    @Test
    void rejectsMissingCurrencyOrMaterials() {
        var recipe = RootedForgeRecipe.ROOTED_ARMOR_REFINEMENT;
        assertFalse(RootedForgePolicy.canCraft(
                recipe,
                recipe.verdantMarkCost() - 1,
                Map.of(RootedMaterial.EMBER_CORE, 99, RootedMaterial.ANCIENT_BARK, 99)
        ).allowed());

        assertFalse(RootedForgePolicy.canCraft(
                recipe,
                999,
                Map.of(RootedMaterial.EMBER_CORE, 99, RootedMaterial.ANCIENT_BARK, 0)
        ).allowed());
    }
}
