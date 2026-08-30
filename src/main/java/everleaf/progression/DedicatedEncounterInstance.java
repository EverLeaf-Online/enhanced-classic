package everleaf.progression;

import java.time.Instant;
import java.util.Set;

/**
 * Immutable public snapshot for one dedicated enhanced-boss instance.
 * Runtime adapters may hold mutable engine objects separately.
 */
public record DedicatedEncounterInstance(
        String instanceId,
        long attemptId,
        String encounterId,
        int leaderCharacterId,
        Set<Integer> participantCharacterIds,
        boolean practice,
        EncounterInstanceState state,
        Instant createdAt,
        Instant startedAt,
        Instant deadline,
        Instant finishedAt
) {
    public DedicatedEncounterInstance {
        if (instanceId == null || instanceId.isBlank()) throw new IllegalArgumentException("instanceId cannot be blank");
        if (encounterId == null || encounterId.isBlank()) throw new IllegalArgumentException("encounterId cannot be blank");
        participantCharacterIds = Set.copyOf(participantCharacterIds);
        if (participantCharacterIds.isEmpty()) throw new IllegalArgumentException("participants cannot be empty");
        if (!participantCharacterIds.contains(leaderCharacterId)) throw new IllegalArgumentException("leader must be a participant");
        if (state == null) throw new IllegalArgumentException("state cannot be null");
        if (createdAt == null) throw new IllegalArgumentException("createdAt cannot be null");
    }

    public boolean terminal() {
        return state.terminal();
    }

    public boolean rewardEligible() {
        return !practice && state == EncounterInstanceState.CLEARED;
    }
}
