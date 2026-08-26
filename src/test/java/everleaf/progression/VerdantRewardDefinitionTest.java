package everleaf.progression;

import org.junit.jupiter.api.Test;

import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class VerdantRewardDefinitionTest {

    @Test
    void validRewardCanRepresentBoundProgressionMaterials() {
        VerdantRewardDefinition reward = new VerdantRewardDefinition(
                "rooted_upgrade_bundle",
                "Rooted Upgrade Bundle",
                VerdantRewardCategory.PROGRESSION_MATERIAL,
                200,
                25,
                3,
                Set.of("bound", "upgrade-material")
        );

        assertTrue(reward.isEligible(200));
        assertTrue(reward.isEligible(250));
        assertFalse(reward.isEligible(199));
    }

    @Test
    void directBisAndPayToWinTagsAreRejected() {
        assertThrows(IllegalArgumentException.class, () -> new VerdantRewardDefinition(
                "bad_bis", "Finished Best Item", VerdantRewardCategory.GEAR_COMPONENT,
                225, 100, 1, Set.of("direct-bis")
        ));
        assertThrows(IllegalArgumentException.class, () -> new VerdantRewardDefinition(
                "bad_p2w", "Paid Advantage", VerdantRewardCategory.UTILITY,
                200, 10, null, Set.of("pay-to-win")
        ));
    }

    @Test
    void invalidPricingAndLimitsAreRejected() {
        assertThrows(IllegalArgumentException.class, () -> new VerdantRewardDefinition(
                "free", "Free", VerdantRewardCategory.COSMETIC, 200, 0, null, Set.of()
        ));
        assertThrows(IllegalArgumentException.class, () -> new VerdantRewardDefinition(
                "bad_limit", "Bad Limit", VerdantRewardCategory.CATCH_UP, 200, 10, 0, Set.of()
        ));
    }
}
