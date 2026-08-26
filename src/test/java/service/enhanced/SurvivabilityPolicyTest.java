package service.enhanced;

import client.Job;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class SurvivabilityPolicyTest {

    @Test
    void classifiesCoreAndExtendedJobs() {
        assertEquals(SurvivabilityPolicy.Archetype.WARRIOR, SurvivabilityPolicy.classify(Job.HERO));
        assertEquals(SurvivabilityPolicy.Archetype.WARRIOR, SurvivabilityPolicy.classify(Job.ARAN4));
        assertEquals(SurvivabilityPolicy.Archetype.BRAWLER, SurvivabilityPolicy.classify(Job.BUCCANEER));
        assertEquals(SurvivabilityPolicy.Archetype.BRAWLER, SurvivabilityPolicy.classify(Job.THUNDERBREAKER4));
        assertEquals(SurvivabilityPolicy.Archetype.MAGICIAN, SurvivabilityPolicy.classify(Job.BISHOP));
        assertEquals(SurvivabilityPolicy.Archetype.MAGICIAN, SurvivabilityPolicy.classify(Job.EVAN10));
        assertEquals(SurvivabilityPolicy.Archetype.RANGED, SurvivabilityPolicy.classify(Job.NIGHTLORD));
        assertEquals(SurvivabilityPolicy.Archetype.RANGED, SurvivabilityPolicy.classify(Job.CORSAIR));
        assertEquals(SurvivabilityPolicy.Archetype.RANGED, SurvivabilityPolicy.classify(Job.WINDARCHER4));
        assertEquals(SurvivabilityPolicy.Archetype.BEGINNER, SurvivabilityPolicy.classify(Job.BEGINNER));
    }

    @Test
    void floorsIncreaseAtProgressionTiers() {
        assertEquals(0, SurvivabilityPolicy.minimumMaxHp(Job.NIGHTLORD, 49));
        assertEquals(2200, SurvivabilityPolicy.minimumMaxHp(Job.NIGHTLORD, 50));
        assertEquals(3000, SurvivabilityPolicy.minimumMaxHp(Job.NIGHTLORD, 70));
        assertEquals(4200, SurvivabilityPolicy.minimumMaxHp(Job.NIGHTLORD, 90));
        assertEquals(5500, SurvivabilityPolicy.minimumMaxHp(Job.NIGHTLORD, 120));
        assertEquals(6800, SurvivabilityPolicy.minimumMaxHp(Job.NIGHTLORD, 150));
        assertEquals(8000, SurvivabilityPolicy.minimumMaxHp(Job.NIGHTLORD, 180));
        assertEquals(9000, SurvivabilityPolicy.minimumMaxHp(Job.NIGHTLORD, 200));
    }

    @Test
    void warriorFloorsRemainHigherThanRangedFloors() {
        assertEquals(10000, SurvivabilityPolicy.minimumMaxHp(Job.HERO, 120));
        assertEquals(5500, SurvivabilityPolicy.minimumMaxHp(Job.BOWMASTER, 120));
    }

    @Test
    void requiredIncreaseIsIdempotent() {
        assertEquals(1500, SurvivabilityPolicy.requiredIncrease(Job.NIGHTLORD, 120, 4000));
        assertEquals(0, SurvivabilityPolicy.requiredIncrease(Job.NIGHTLORD, 120, 5500));
        assertEquals(0, SurvivabilityPolicy.requiredIncrease(Job.NIGHTLORD, 120, 7000));
    }

    @Test
    void rejectsInvalidInputs() {
        assertThrows(IllegalArgumentException.class,
                () -> SurvivabilityPolicy.minimumMaxHp(Job.HERO, 0));
        assertThrows(IllegalArgumentException.class,
                () -> SurvivabilityPolicy.requiredIncrease(Job.HERO, 120, -1));
    }
}
