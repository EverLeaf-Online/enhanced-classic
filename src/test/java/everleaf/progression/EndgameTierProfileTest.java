package everleaf.progression;

import org.junit.jupiter.api.Test;
import service.enhanced.EndgameTierPolicy;

import static org.junit.jupiter.api.Assertions.*;

class EndgameTierProfileTest {

    @Test
    void mapsMilestonesToNamedProfiles() {
        assertEquals("Rooted", EndgameTierProfile.forLevel(200).name());
        assertEquals("Awakened", EndgameTierProfile.forLevel(210).name());
        assertEquals("Ascendant", EndgameTierProfile.forLevel(225).name());
        assertEquals("Ancient", EndgameTierProfile.forLevel(240).name());
        assertEquals("Evergreen", EndgameTierProfile.forLevel(250).name());
    }

    @Test
    void rootedDoesNotUnlockGuildLaneYet() {
        EndgameTierProfile rooted = EndgameTierProfile.forLevel(200);
        assertTrue(rooted.supports(EndgameRewardLane.BOSS));
        assertTrue(rooted.supports(EndgameRewardLane.COLLECTION));
        assertFalse(rooted.supports(EndgameRewardLane.GUILD));
    }

    @Test
    void tierTwoAndAboveSupportGuildProgression() {
        assertTrue(EndgameTierProfile.forLevel(210).supports(EndgameRewardLane.GUILD));
        assertTrue(EndgameTierProfile.forLevel(250).supports(EndgameRewardLane.GUILD));
    }

    @Test
    void preEndgameHasNoProfile() {
        assertThrows(IllegalArgumentException.class, () -> EndgameTierProfile.forLevel(199));
        assertThrows(IllegalArgumentException.class,
                () -> EndgameTierProfile.forTier(EndgameTierPolicy.Tier.PRE_ENDGAME));
    }

    @Test
    void activeLaneSetIsImmutable() {
        EndgameTierProfile profile = EndgameTierProfile.forLevel(225);
        assertThrows(UnsupportedOperationException.class,
                () -> profile.activeLanes().add(EndgameRewardLane.BOSS));
    }
}
