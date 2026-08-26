package everleaf.progression;

import java.time.Instant;
import java.time.LocalDate;

/** Character-scoped progress for one weekly objective. */
public record CharacterObjectiveState(
        int characterId,
        LocalDate weekStartUtc,
        String objectiveId,
        int progressCount,
        Instant completedAt,
        Instant claimedAt
) {
    public CharacterObjectiveState {
        if (characterId < 1) throw new IllegalArgumentException("characterId must be positive");
        if (weekStartUtc == null) throw new IllegalArgumentException("weekStartUtc cannot be null");
        if (objectiveId == null || objectiveId.isBlank()) throw new IllegalArgumentException("objectiveId cannot be blank");
        if (progressCount < 0) throw new IllegalArgumentException("progressCount cannot be negative");
        if (claimedAt != null && completedAt == null) throw new IllegalArgumentException("claimed objective must be completed");
    }

    public boolean completed() {
        return completedAt != null;
    }

    public boolean claimed() {
        return claimedAt != null;
    }
}
