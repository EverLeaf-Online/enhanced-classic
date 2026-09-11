package everleaf.progression;

/** Immutable account-wide milestone state used by the player command and tests. */
public record AccountMilestoneSnapshot(
        int accountId,
        int uniqueMonsterCards,
        int uniqueCompletedQuests,
        int linkedLevelScore,
        int linkedCharacters
) {
    public AccountMilestoneSnapshot {
        if (accountId < 0 || uniqueMonsterCards < 0 || uniqueCompletedQuests < 0
                || linkedLevelScore < 0 || linkedCharacters < 0) {
            throw new IllegalArgumentException("Milestone snapshot values cannot be negative");
        }
    }

    public int value(AccountMilestoneTrack track) {
        return switch (track) {
            case MONSTER_BOOK -> uniqueMonsterCards;
            case QUESTS -> uniqueCompletedQuests;
            case LEGACY -> linkedLevelScore;
        };
    }

    public int tier(AccountMilestoneTrack track) {
        return track.tierFor(value(track));
    }
}
