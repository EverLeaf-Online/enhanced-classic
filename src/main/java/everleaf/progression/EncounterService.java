package everleaf.progression;

import java.time.Instant;
import java.time.LocalDate;

/** Coordinates access validation, attempt lifecycle, and weekly reward eligibility. */
public final class EncounterService {
    private final EncounterRepository repository;

    public EncounterService(EncounterRepository repository) {
        if (repository == null) throw new IllegalArgumentException("repository cannot be null");
        this.repository = repository;
    }

    public EncounterAttempt start(int accountId, int characterId, int level, String encounterId, Instant now) {
        EnhancedBossDefinition definition = EnhancedBossCatalog.byId(encounterId);
        if (!definition.isLevelEligible(level)) {
            throw new IllegalStateException("level_gate");
        }
        return repository.createAttempt(accountId, characterId, encounterId, now);
    }

    public EncounterAttempt clear(long attemptId, Instant now) {
        EncounterAttempt attempt = repository.findAttempt(attemptId)
                .orElseThrow(() -> new IllegalArgumentException("unknown attempt"));
        if (attempt.finished()) throw new IllegalStateException("attempt_already_finished");
        return repository.finishAttempt(attemptId, EncounterResult.CLEARED, now);
    }

    public EncounterAttempt fail(long attemptId, Instant now) {
        EncounterAttempt attempt = repository.findAttempt(attemptId)
                .orElseThrow(() -> new IllegalArgumentException("unknown attempt"));
        if (attempt.finished()) throw new IllegalStateException("attempt_already_finished");
        return repository.finishAttempt(attemptId, EncounterResult.FAILED, now);
    }

    public boolean isWeeklyRewardEligible(int accountId, String encounterId, Instant now) {
        LocalDate week = WeeklyWindow.forInstant(now).startDate();
        return !repository.hasWeeklyClear(accountId, encounterId, week);
    }

    public boolean claimWeeklyReward(long attemptId) {
        EncounterAttempt attempt = repository.findAttempt(attemptId)
                .orElseThrow(() -> new IllegalArgumentException("unknown attempt"));
        if (!attempt.cleared()) return false;
        if (attempt.weeklyRewardClaimed()) return false;
        return repository.markWeeklyRewardClaimed(attemptId);
    }
}
