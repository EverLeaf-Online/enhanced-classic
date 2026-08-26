package everleaf.progression;

import client.inventory.Equip;
import constants.inventory.ItemConstants;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class RootedForgeStatApplierTest {
    @Test
    void appliesWeaponOutcomeOnceAndMakesTargetUntradeable() {
        Equip weapon = new Equip(1302000, (short) 1);
        weapon.setWatk((short) 50);
        var outcome = RootedForgeOutcomeCatalog.byRecipe(RootedForgeRecipe.ROOTED_WEAPON_REFINEMENT);

        var first = RootedForgeStatApplier.apply(weapon, outcome);
        var second = RootedForgeStatApplier.apply(weapon, outcome);

        assertTrue(first.applied());
        assertFalse(second.applied());
        assertEquals("stage_already_applied", second.reason());
        assertEquals(53, weapon.getWatk());
        assertEquals(1, weapon.getEverleafForgeStage());
        assertEquals(ItemConstants.UNTRADEABLE, weapon.getFlag() & ItemConstants.UNTRADEABLE);
    }

    @Test
    void enforcesWeaponAndArmorRecipeCategories() {
        Equip weapon = new Equip(1302000, (short) 1);
        Equip armor = new Equip(1002001, (short) 2);

        assertFalse(RootedForgeStatApplier.apply(
                armor, RootedForgeOutcomeCatalog.byRecipe(RootedForgeRecipe.ROOTED_WEAPON_REFINEMENT)).applied());
        assertFalse(RootedForgeStatApplier.apply(
                weapon, RootedForgeOutcomeCatalog.byRecipe(RootedForgeRecipe.ROOTED_ARMOR_REFINEMENT)).applied());
    }

    @Test
    void validatesAllNewStatsBeforeMutatingEquipment() {
        Equip weapon = new Equip(1302000, (short) 1);
        weapon.setStr((short) 10);
        weapon.setWatk(Short.MAX_VALUE);

        assertThrows(IllegalStateException.class, () -> RootedForgeStatApplier.apply(
                weapon, RootedForgeOutcomeCatalog.byRecipe(RootedForgeRecipe.ROOTED_WEAPON_REFINEMENT)));
        assertEquals(10, weapon.getStr());
        assertEquals(0, weapon.getEverleafForgeStage());
    }
}
