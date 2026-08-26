package everleaf.progression;

import java.util.List;
import java.util.Set;

/**
 * Initial content-agnostic weekly catalog.
 *
 * Objective IDs are stable server-side identifiers. Concrete boss/map/quest
 * bindings can be attached later without changing the progression contract.
 */
public final class WeeklyObjectiveCatalog {
    private WeeklyObjectiveCatalog() {
    }

    private static final List<WeeklyObjectiveDefinition> OBJECTIVES = List.of(
            new WeeklyObjectiveDefinition("rooted_boss_hunt", "Defeat endgame bosses", EndgameRewardLane.BOSS,
                    200, 3, 40, Set.of("combat", "party")),
            new WeeklyObjectiveDefinition("rooted_party_clear", "Complete endgame party content", EndgameRewardLane.PARTY,
                    200, 3, 35, Set.of("party", "pq")),
            new WeeklyObjectiveDefinition("rooted_collection", "Advance an endgame collection", EndgameRewardLane.COLLECTION,
                    200, 5, 25, Set.of("account", "collection")),
            new WeeklyObjectiveDefinition("awakened_guild", "Complete guild endgame objectives", EndgameRewardLane.GUILD,
                    210, 2, 40, Set.of("guild", "social")),
            new WeeklyObjectiveDefinition("ascendant_hard_boss", "Clear advanced boss encounters", EndgameRewardLane.BOSS,
                    225, 2, 60, Set.of("combat", "hard-mode")),
            new WeeklyObjectiveDefinition("ancient_capstone", "Complete late-endgame challenges", EndgameRewardLane.WEEKLY,
                    240, 4, 70, Set.of("late-endgame")),
            new WeeklyObjectiveDefinition("evergreen_mastery", "Complete Evergreen mastery objectives", EndgameRewardLane.WEEKLY,
                    250, 5, 80, Set.of("cap", "mastery"))
    );

    public static List<WeeklyObjectiveDefinition> all() {
        return OBJECTIVES;
    }

    public static List<WeeklyObjectiveDefinition> eligibleForLevel(int level) {
        if (level < 200) return List.of();
        return OBJECTIVES.stream().filter(objective -> objective.isEligible(level)).toList();
    }

    public static WeeklyObjectiveDefinition byId(String id) {
        if (id == null || id.isBlank()) throw new IllegalArgumentException("id cannot be blank");
        return OBJECTIVES.stream()
                .filter(objective -> objective.id().equals(id))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("unknown objective: " + id));
    }
}
