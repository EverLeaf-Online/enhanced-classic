package everleaf.progression;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class RootedZakumRewardPolicyTest {
    @Test
    void practiceRunsGrantNoValuableProgression() {
        var reward = RootedZakumRewardPolicy.forMode(EnhancedBossRewardMode.PRACTICE);
        assertEquals(0, reward.verdantMarks());
        assertTrue(reward.materials().isEmpty());
    }

    @Test
    void weeklyClearGrantsControlledBoundMaterials() {
        var reward = RootedZakumRewardPolicy.forMode(EnhancedBossRewardMode.WEEKLY_REWARD);
        assertTrue(reward.verdantMarks() > 0);
        assertTrue(reward.materials().get(RootedMaterial.EMBER_CORE) > 0);
        assertTrue(reward.materials().keySet().stream().allMatch(RootedMaterial::accountBound));
    }

    @Test
    void forgeRecipesDoNotDirectlyGrantBestInSlot() {
        for (RootedForgeRecipe recipe : RootedForgeRecipe.values()) {
            assertFalse(recipe.directlyGrantsBestInSlot());
            assertTrue(recipe.verdantMarkCost() > 0);
            assertFalse(recipe.materialCosts().isEmpty());
        }
    }
}
