package everleaf.progression;

import java.time.Instant;
import java.time.LocalDate;

/**
 * Durable attempt and account-weekly reward ownership for the level-180 Fallen Cygnus bridge encounter.
 * This intentionally does not use EnhancedBossCatalog because that ladder begins at level 200.
 */
public final class CygnusEncounterLifecycleService {
    public static final String ENCOUNTER_ID = "fallen_cygnus";
    public static final int MIN_LEVEL = 180;
    public static final int MAX_LEVEL = 255;

    private final EncounterRepository repository;

    public CygnusEncounterLifecycleService(EncounterRepository repository) {
        if (repository == null) throw new IllegalArgumentException("repository cannot be null");
        this.repository = repository;
    }

    public StartedAttempt begin(int accountId, int characterId, int level, Instant now) {
        if (level < MIN_LEVEL || level > MAX_LEVEL) throw new IllegalStateException("level_gate");
        LocalDate week = WeeklyWindow.forInstant(now).startDate();
        boolean weekly = !repository.hasWeeklyRewardClaim(accountId, ENCOUNTER_ID, week);
        EncounterAttempt attempt = repository.createAttempt(accountId, characterId, ENCOUNTER_ID, now);
        return new StartedAttempt(attempt.id(), weekly ? EnhancedBossRewardMode.WEEKLY_REWARD : EnhancedBossRewardMode.PRACTICE);
    }

    public Completion complete(long attemptId, EnhancedBossRewardMode mode, Instant now) {
        if (mode == null) throw new IllegalArgumentException("mode cannot be null");
        EncounterAttempt attempt = repository.findAttempt(attemptId)
                .orElseThrow(() -> new IllegalArgumentException("unknown attempt"));
        if (attempt.result() == EncounterResult.IN_PROGRESS) {
            attempt = repository.finishAttempt(attemptId, EncounterResult.CLEARED, now);
        }
        if (!attempt.cleared()) return new Completion(false, false, "attempt_not_cleared");
        if (!mode.grantsValuableRewards()) return new Completion(true, false, "practice");

        LocalDate week = WeeklyWindow.forInstant(now).startDate();
        boolean claimed = attempt.weeklyRewardClaimed()
                || repository.markWeeklyRewardClaimed(attemptId, week, now);
        return claimed
                ? new Completion(true, true, "weekly_reward")
                : new Completion(true, false, "weekly_already_claimed");
    }

    public void fail(long attemptId, Instant now) {
        EncounterAttempt attempt = repository.findAttempt(attemptId)
                .orElseThrow(() -> new IllegalArgumentException("unknown attempt"));
        if (!attempt.finished()) repository.finishAttempt(attemptId, EncounterResult.FAILED, now);
    }

    public record StartedAttempt(long attemptId, EnhancedBossRewardMode mode) {}
    public record Completion(boolean completed, boolean weeklyRewardClaimed, String reason) {}
}
