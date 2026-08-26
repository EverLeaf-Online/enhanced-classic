package everleaf.progression;

import service.enhanced.EndgameTierPolicy;

import java.util.EnumSet;
import java.util.Set;

/**
 * Everleaf-facing identity and content-lane policy for the shared endgame tiers.
 */
public record EndgameTierProfile(
        EndgameTierPolicy.Tier tier,
        String name,
        String purpose,
        Set<EndgameRewardLane> activeLanes
) {
    public EndgameTierProfile {
        if (tier == null || tier == EndgameTierPolicy.Tier.PRE_ENDGAME) {
            throw new IllegalArgumentException("profile requires an endgame tier");
        }
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("name cannot be blank");
        }
        if (purpose == null || purpose.isBlank()) {
            throw new IllegalArgumentException("purpose cannot be blank");
        }
        activeLanes = Set.copyOf(activeLanes);
    }

    public static EndgameTierProfile forLevel(int level) {
        return forTier(EndgameTierPolicy.forLevel(level));
    }

    public static EndgameTierProfile forTier(EndgameTierPolicy.Tier tier) {
        if (tier == null || tier == EndgameTierPolicy.Tier.PRE_ENDGAME) {
            throw new IllegalArgumentException("level/tier has not reached Everleaf endgame");
        }

        return switch (tier) {
            case TIER_1 -> new EndgameTierProfile(
                    tier,
                    "Rooted",
                    "Transition from classic v83 endgame into Everleaf progression.",
                    EnumSet.of(EndgameRewardLane.BOSS, EndgameRewardLane.WEEKLY,
                            EndgameRewardLane.QUEST, EndgameRewardLane.PARTY,
                            EndgameRewardLane.COLLECTION));
            case TIER_2 -> new EndgameTierProfile(
                    tier,
                    "Awakened",
                    "Establish repeatable party and account progression.",
                    EnumSet.of(EndgameRewardLane.BOSS, EndgameRewardLane.WEEKLY,
                            EndgameRewardLane.QUEST, EndgameRewardLane.PARTY,
                            EndgameRewardLane.COLLECTION, EndgameRewardLane.GUILD));
            case TIER_3 -> new EndgameTierProfile(
                    tier,
                    "Ascendant",
                    "Advance into hard encounters, gear growth, and guild objectives.",
                    EnumSet.allOf(EndgameRewardLane.class));
            case TIER_4 -> new EndgameTierProfile(
                    tier,
                    "Ancient",
                    "Complete final pre-cap challenges and capstone progression.",
                    EnumSet.allOf(EndgameRewardLane.class));
            case TIER_5 -> new EndgameTierProfile(
                    tier,
                    "Evergreen",
                    "Continue mastery, prestige, and account goals at the level cap.",
                    EnumSet.allOf(EndgameRewardLane.class));
            case PRE_ENDGAME -> throw new IllegalArgumentException("pre-endgame has no Everleaf tier profile");
        };
    }

    public boolean supports(EndgameRewardLane lane) {
        if (lane == null) {
            return false;
        }
        return activeLanes.contains(lane);
    }
}
