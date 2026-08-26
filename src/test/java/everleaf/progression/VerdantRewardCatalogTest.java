package everleaf.progression;

import org.junit.jupiter.api.Test;

import java.util.HashSet;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class VerdantRewardCatalogTest {

    @Test
    void catalogIdsAreUniqueAndRewardsStayInsideApprovedCategories() {
        Set<String> ids = new HashSet<>();
        for (VerdantRewardDefinition reward : VerdantRewardCatalog.all()) {
            assertTrue(ids.add(reward.id()), "duplicate reward id: " + reward.id());
            assertNotNull(reward.category());
            assertTrue(reward.price() > 0);
            assertFalse(reward.tags().contains("direct-bis"));
            assertFalse(reward.tags().contains("pay-to-win"));
        }
    }

    @Test
    void directBisAndPayToWinDefinitionsAreRejected() {
        assertThrows(IllegalArgumentException.class, () -> new VerdantRewardDefinition(
                "bad_bis", "Bad BiS", VerdantRewardCategory.GEAR_COMPONENT,
                200, 100, 1, Set.of("direct-bis")
        ));
        assertThrows(IllegalArgumentException.class, () -> new VerdantRewardDefinition(
                "bad_p2w", "Bad P2W", VerdantRewardCategory.UTILITY,
                200, 100, 1, Set.of("pay-to-win")
        ));
    }

    @Test
    void levelGatesExposeRewardsGradually() {
        assertTrue(VerdantRewardCatalog.eligibleForLevel(199).isEmpty());
        assertTrue(VerdantRewardCatalog.eligibleForLevel(200).stream()
                .noneMatch(reward -> reward.minimumLevel() > 200));
        assertTrue(VerdantRewardCatalog.eligibleForLevel(225).stream()
                .anyMatch(reward -> reward.id().equals("ascendant_forge_component")));
        assertTrue(VerdantRewardCatalog.eligibleForLevel(250).stream()
                .anyMatch(reward -> reward.id().equals("evergreen_prestige_token")));
    }
}
