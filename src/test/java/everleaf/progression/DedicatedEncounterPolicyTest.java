package everleaf.progression;

import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class DedicatedEncounterPolicyTest {
    private final EnhancedBossDefinition rooted = EnhancedBossCatalog.byId("rooted_zakum");

    @Test
    void acceptsRootedPartyWithinThreeToSixPlayers() {
        Set<Integer> result = DedicatedEncounterPolicy.validateParty(rooted, 10, List.of(10, 11, 12));
        assertEquals(Set.of(10, 11, 12), result);
        assertEquals(6, DedicatedEncounterPolicy.validateParty(rooted, 10, List.of(10, 11, 12, 13, 14, 15)).size());
    }

    @Test
    void rejectsPartyOutsideEncounterBounds() {
        assertEquals("party_too_small", assertThrows(IllegalStateException.class,
                () -> DedicatedEncounterPolicy.validateParty(rooted, 10, List.of(10, 11))).getMessage());
        assertEquals("party_too_large", assertThrows(IllegalStateException.class,
                () -> DedicatedEncounterPolicy.validateParty(rooted, 10, List.of(10, 11, 12, 13, 14, 15, 16))).getMessage());
    }

    @Test
    void requiresLeaderAndUniqueParticipants() {
        assertEquals("leader_not_in_party", assertThrows(IllegalArgumentException.class,
                () -> DedicatedEncounterPolicy.validateParty(rooted, 99, List.of(10, 11, 12))).getMessage());
        assertEquals("duplicate_participant", assertThrows(IllegalArgumentException.class,
                () -> DedicatedEncounterPolicy.validateParty(rooted, 10, List.of(10, 10, 12))).getMessage());
    }

    @Test
    void practiceClearsNeverBecomeRewardEligible() {
        DedicatedEncounterInstance practice = new DedicatedEncounterInstance(
                "test", 1L, "rooted_zakum", 10, Set.of(10, 11, 12), true,
                EncounterInstanceState.CLEARED, java.time.Instant.EPOCH,
                java.time.Instant.EPOCH, java.time.Instant.EPOCH.plusSeconds(10), java.time.Instant.EPOCH.plusSeconds(5));
        assertFalse(practice.rewardEligible());
    }
}
