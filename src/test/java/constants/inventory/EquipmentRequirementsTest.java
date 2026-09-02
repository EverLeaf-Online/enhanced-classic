package constants.inventory;

import client.Job;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class EquipmentRequirementsTest {

    @Test
    void unrestrictedEquipmentAllowsAnyJob() {
        assertTrue(EquipmentRequirements.canEquipForJob(Job.BEGINNER, 0));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.HERO, 0));
    }

    @Test
    void explorerFamiliesRespectRequirementMask() {
        assertTrue(EquipmentRequirements.canEquipForJob(Job.HERO, 1));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.BISHOP, 2));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.BOWMASTER, 4));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.NIGHTLORD, 8));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.CORSAIR, 16));
        assertFalse(EquipmentRequirements.canEquipForJob(Job.BISHOP, 1));
    }

    @Test
    void legacyAllFamilySentinelAllowsCombatFamiliesOnly() {
        int allFamilies = EquipmentRequirements.ALL_COMBAT_FAMILIES;
        assertTrue(EquipmentRequirements.canEquipForJob(Job.HERO, allFamilies));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.BISHOP, allFamilies));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.BOWMASTER, allFamilies));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.NIGHTLORD, allFamilies));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.CORSAIR, allFamilies));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.EVAN10, allFamilies));
        assertFalse(EquipmentRequirements.canEquipForJob(Job.BEGINNER, allFamilies));
        assertFalse(EquipmentRequirements.canEquipForJob(Job.NOBLESSE, allFamilies));
        assertFalse(EquipmentRequirements.canEquipForJob(Job.LEGEND, allFamilies));
    }

    @Test
    void extendedClassesMapToTheirCombatFamily() {
        assertTrue(EquipmentRequirements.canEquipForJob(Job.DAWNWARRIOR4, 1));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.ARAN4, 1));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.BLAZEWIZARD4, 2));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.EVAN10, 2));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.WINDARCHER4, 4));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.NIGHTWALKER4, 8));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.THUNDERBREAKER4, 16));
    }

    @Test
    void beginnerCannotBypassRestrictedGear() {
        assertFalse(EquipmentRequirements.canEquipForJob(Job.BEGINNER, 1));
        assertFalse(EquipmentRequirements.canEquipForJob(Job.NOBLESSE, 2));
        assertFalse(EquipmentRequirements.canEquipForJob(Job.LEGEND, 1));
    }

    @Test
    void gmJobsBypassRequirements() {
        assertTrue(EquipmentRequirements.canEquipForJob(Job.GM, 1));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.SUPERGM, 16));
        assertTrue(EquipmentRequirements.canEquipForJob(Job.GM, EquipmentRequirements.ALL_COMBAT_FAMILIES));
    }
}
