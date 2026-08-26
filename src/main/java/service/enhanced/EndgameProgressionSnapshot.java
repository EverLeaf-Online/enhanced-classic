package service.enhanced;

import java.util.Set;

/**
 * Immutable view of a character's current Everleaf endgame progression state.
 * Intended for NPCs, commands, account UI, and future website/API surfaces.
 */
public record EndgameProgressionSnapshot(
        int level,
        EndgameTierPolicy.Tier tier,
        Set<EndgameProgressionPolicy.Unlock> unlocks,
        Integer nextMilestoneLevel,
        int levelsToNextMilestone,
        boolean atLevelCap
) {
    public static EndgameProgressionSnapshot forLevel(int level) {
        EndgameTierPolicy.Tier tier = EndgameTierPolicy.forLevel(level);
        Integer next = nextMilestoneAfter(level);
        int distance = next == null ? 0 : next - level;
        return new EndgameProgressionSnapshot(
                level,
                tier,
                EndgameProgressionPolicy.unlocksForLevel(level),
                next,
                distance,
                level == LevelCapPolicy.PLAYER_MAX_LEVEL
        );
    }

    private static Integer nextMilestoneAfter(int level) {
        for (EndgameTierPolicy.Tier candidate : EndgameTierPolicy.Tier.values()) {
            int milestone = candidate.minimumLevel();
            if (milestone > level) {
                return milestone;
            }
        }
        return null;
    }
}
