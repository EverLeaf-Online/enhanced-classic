package everleaf.progression;

import java.time.Instant;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

public interface EncounterRepository {
    EncounterAttempt createAttempt(int accountId, int characterId, String encounterId, Instant startedAt);

    Optional<EncounterAttempt> findAttempt(long attemptId);

    EncounterAttempt finishAttempt(long attemptId, EncounterResult result, Instant finishedAt);

    boolean hasWeeklyRewardClaim(int accountId, String encounterId, LocalDate weekStartUtc);

    boolean markWeeklyRewardClaimed(long attemptId, LocalDate weekStartUtc, Instant claimedAt);

    List<EncounterAttempt> recentAttempts(int characterId, int limit);
}
