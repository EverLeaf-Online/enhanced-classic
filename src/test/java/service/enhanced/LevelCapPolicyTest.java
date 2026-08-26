package service.enhanced;

import client.Job;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class LevelCapPolicyTest {

    @Test
    void allPlayableJobFamiliesUseLevel250Cap() {
        assertEquals(250, LevelCapPolicy.maxLevel(Job.HERO));
        assertEquals(250, LevelCapPolicy.maxLevel(Job.BISHOP));
        assertEquals(250, LevelCapPolicy.maxLevel(Job.NIGHTLORD));
        assertEquals(250, LevelCapPolicy.maxLevel(Job.BUCCANEER));
        assertEquals(250, LevelCapPolicy.maxLevel(Job.DAWNWARRIOR4));
        assertEquals(250, LevelCapPolicy.maxLevel(Job.ARAN4));
        assertEquals(250, LevelCapPolicy.maxLevel(Job.EVAN10));
    }
}
