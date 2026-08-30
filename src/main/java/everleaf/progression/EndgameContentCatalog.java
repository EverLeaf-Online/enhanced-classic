package everleaf.progression;

import java.util.List;
import java.util.Set;

/** Initial content-agnostic post-200 access catalog. */
public final class EndgameContentCatalog {
    private EndgameContentCatalog() {
    }

    private static final List<EndgameContentGate> CONTENT = List.of(
            new EndgameContentGate("rooted_boss_tier", "Rooted Boss Tier", 200, "rooted_bosses",
                    Set.of(EndgameRewardLane.BOSS)),
            new EndgameContentGate("rooted_forge", "Rooted Forge", 200, "rooted_forge",
                    Set.of(EndgameRewardLane.QUEST, EndgameRewardLane.WEEKLY)),
            new EndgameContentGate("awakened_boss_tier", "Awakened Boss Tier", 210, "awakened_bosses",
                    Set.of(EndgameRewardLane.BOSS, EndgameRewardLane.PARTY)),
            new EndgameContentGate("awakened_forge", "Awakened Forge", 210, "awakened_forge",
                    Set.of(EndgameRewardLane.WEEKLY)),
            new EndgameContentGate("hard_mode_boss_tier", "Ascendant Hard-Mode Boss Tier", 225, "hard_mode_bosses",
                    Set.of(EndgameRewardLane.BOSS, EndgameRewardLane.PARTY)),
            new EndgameContentGate("ascendant_forge", "Ascendant Forge", 225, "ascendant_forge",
                    Set.of(EndgameRewardLane.WEEKLY)),
            new EndgameContentGate("ancient_boss_tier", "Ancient Boss Tier", 240, "ancient_bosses",
                    Set.of(EndgameRewardLane.BOSS, EndgameRewardLane.PARTY, EndgameRewardLane.GUILD)),
            new EndgameContentGate("ancient_forge", "Ancient Forge", 240, "ancient_forge",
                    Set.of(EndgameRewardLane.WEEKLY)),
            new EndgameContentGate("evergreen_mastery", "Evergreen Mastery", 250, "evergreen_mastery",
                    Set.of(EndgameRewardLane.BOSS, EndgameRewardLane.WEEKLY, EndgameRewardLane.COLLECTION,
                            EndgameRewardLane.GUILD)),
            new EndgameContentGate("capstone_quest", "Evergreen Capstone", 250, "capstone_quest",
                    Set.of(EndgameRewardLane.QUEST))
    );

    public static List<EndgameContentGate> all() {
        return CONTENT;
    }

    public static List<EndgameContentGate> accessibleAt(int level) {
        if (level < 200) return List.of();
        return CONTENT.stream().filter(gate -> gate.isAccessible(level)).toList();
    }

    public static EndgameContentGate byId(String id) {
        if (id == null || id.isBlank()) throw new IllegalArgumentException("id cannot be blank");
        return CONTENT.stream().filter(g -> g.id().equals(id)).findFirst()
                .orElseThrow(() -> new IllegalArgumentException("unknown endgame content gate: " + id));
    }
}
