package everleaf.progression;

import java.util.List;
import java.util.Set;

/** Canonical post-200 milestone unlock catalog. */
public final class EndgameMilestoneCatalog {
    private EndgameMilestoneCatalog() {
    }

    private static final List<EndgameMilestone> MILESTONES = List.of(
            new EndgameMilestone(200, "rooted", "Rooted", "Rooted Adventurer",
                    Set.of(EndgameRewardLane.BOSS, EndgameRewardLane.WEEKLY, EndgameRewardLane.QUEST,
                            EndgameRewardLane.PARTY, EndgameRewardLane.COLLECTION),
                    Set.of("everleaf_endgame", "rooted_bosses", "rooted_weeklies", "rooted_forge")),
            new EndgameMilestone(210, "awakened", "Awakened", "Awakened Adventurer",
                    Set.of(EndgameRewardLane.GUILD),
                    Set.of("awakened_bosses", "awakened_forge", "awakened_weeklies")),
            new EndgameMilestone(225, "ascendant", "Ascendant", "Ascendant Adventurer",
                    Set.of(), Set.of("hard_mode_bosses", "ascendant_forge", "ascendant_weeklies")),
            new EndgameMilestone(240, "ancient", "Ancient", "Ancient Adventurer",
                    Set.of(), Set.of("ancient_bosses", "ancient_forge", "ancient_weeklies")),
            new EndgameMilestone(250, "evergreen", "Evergreen", "Evergreen",
                    Set.of(), Set.of("evergreen_mastery", "evergreen_prestige", "capstone_quest"))
    );

    public static List<EndgameMilestone> all() {
        return MILESTONES;
    }

    public static List<EndgameMilestone> reachedBy(int level) {
        if (level < 200) return List.of();
        return MILESTONES.stream().filter(m -> m.reachedBy(level)).toList();
    }

    public static EndgameMilestone currentForLevel(int level) {
        if (level < 200 || level > 250) throw new IllegalArgumentException("level must be 200-250");
        return MILESTONES.stream()
                .filter(m -> m.level() <= level)
                .reduce((first, second) -> second)
                .orElseThrow();
    }

    public static boolean hasUnlockTag(int level, String tag) {
        if (tag == null || tag.isBlank() || level < 200) return false;
        return reachedBy(level).stream().anyMatch(m -> m.unlockTags().contains(tag));
    }
}
