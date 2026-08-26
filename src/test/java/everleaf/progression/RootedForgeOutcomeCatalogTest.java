package everleaf.progression;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class RootedForgeOutcomeCatalogTest {
    @Test
    void allRootedRecipesHaveSafeDeterministicOutcomes() {
        for (RootedForgeRecipe recipe : RootedForgeRecipe.values()) {
            var outcome = RootedForgeOutcomeCatalog.byRecipe(recipe);
            assertEquals(recipe, outcome.recipe());
            assertTrue(outcome.policy().deterministic());
            assertFalse(outcome.policy().canFail());
            assertFalse(outcome.policy().canDowngrade());
            assertFalse(outcome.policy().canDestroyItem());
            assertFalse(outcome.policy().usesRandomStatRolls());
        }
    }

    @Test
    void weaponAndArmorStageOneHaveFixedKnownDeltas() {
        var weapon = RootedForgeOutcomeCatalog.byRecipe(RootedForgeRecipe.ROOTED_WEAPON_REFINEMENT).statDelta();
        assertEquals(3, weapon.weaponAttack());
        assertEquals(3, weapon.magicAttack());
        assertEquals(50, weapon.hp());

        var armor = RootedForgeOutcomeCatalog.byRecipe(RootedForgeRecipe.ROOTED_ARMOR_REFINEMENT).statDelta();
        assertEquals(12, armor.weaponDefense());
        assertEquals(12, armor.magicDefense());
        assertEquals(100, armor.hp());
    }

    @Test
    void punitiveForgePolicyCannotBeConstructed() {
        assertThrows(IllegalArgumentException.class,
                () -> new ForgeOutcomePolicy(true, true, false, false, false));
        assertThrows(IllegalArgumentException.class,
                () -> new ForgeOutcomePolicy(true, false, true, false, false));
        assertThrows(IllegalArgumentException.class,
                () -> new ForgeOutcomePolicy(true, false, false, true, false));
        assertThrows(IllegalArgumentException.class,
                () -> new ForgeOutcomePolicy(true, false, false, false, true));
    }
}
