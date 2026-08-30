package everleaf.progression;

import java.time.Instant;

/** Immutable persisted state for one Everleaf enhanced-boss attempt. */
public record EncounterAttempt(
        long id,
        int accountId,
        int characterId,
        String encounterId,
        Instant startedAt,
        Instant finishedAt,
        EncounterResult result,
        boolean weeklyRewardClaimed
) {
    public EncounterAttempt {
        if (accountId <= 0) throw new IllegalArgumentException("accountId must be positive");
        if (characterId <= 0) throw new IllegalArgumentException("characterId must be positive");
        if (encounterId == null || encounterId.isBlank()) throw new IllegalArgumentException("encounterId cannot be blank");
        if (startedAt == null) throw new IllegalArgumentException("startedAt cannot be null");
        if (result == null) throw new IllegalArgumentException("result cannot be null");
        if (result == EncounterResult.IN_PROGRESS && finishedAt != null) {
            throw new IllegalArgumentException("in-progress encounter cannot have finishedAt");
        }
        if (result != EncounterResult.IN_PROGRESS && finishedAt == null) {
            throw new IllegalArgumentException("finished encounter requires finishedAt");
        }
    }

    public boolean finished() {
        return result != EncounterResult.IN_PROGRESS;
    }

    public boolean cleared() {
        return result == EncounterResult.CLEARED;
    }
}
