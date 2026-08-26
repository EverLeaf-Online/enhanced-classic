package everleaf.progression;

import java.time.Instant;
import java.time.LocalDate;

/**
 * Coordinates character objective progress with an account-wide valuable
 * reward budget. The repository boundary keeps persistence interchangeable.
 */
public final class WeeklyProgressionService {
    private final WeeklyProgressRepository repository;

    public WeeklyProgressionService(WeeklyProgressRepository repository) {
        if (repository == null) throw new IllegalArgumentException("repository cannot be null");
        this.repository = repository;
    }

    public CharacterObjectiveState addProgress(
            int characterId,
            int characterLevel,
            String objectiveId,
            int amount,
            Instant now
    ) {
        if (amount <= 0) throw new IllegalArgumentException("amount must be positive");
        WeeklyObjectiveDefinition definition = WeeklyObjectiveCatalog.byId(objectiveId);
        if (!definition.isEligible(characterLevel)) {
            throw new IllegalStateException("character is not eligible for objective " + objectiveId);
        }

        LocalDate week = WeeklyWindow.forInstant(now).startDate();
        CharacterObjectiveState current = repository.findCharacterObjective(characterId, week, objectiveId)
                .orElse(new CharacterObjectiveState(characterId, week, objectiveId, 0, null, null));

        if (current.claimed()) return current;

        int progress = Math.min(definition.targetCount(), current.progressCount() + amount);
        Instant completedAt = current.completedAt();
        if (completedAt == null && progress >= definition.targetCount()) {
            completedAt = now;
        }

        return repository.saveCharacterObjective(new CharacterObjectiveState(
                characterId,
                week,
                objectiveId,
                progress,
                completedAt,
                current.claimedAt()
        ));
    }

    public ClaimResult claim(
            int accountId,
            int characterId,
            int characterLevel,
            String objectiveId,
            Instant now
    ) {
        WeeklyObjectiveDefinition definition = WeeklyObjectiveCatalog.byId(objectiveId);
        if (!definition.isEligible(characterLevel)) {
            return ClaimResult.rejected("not_eligible");
        }

        LocalDate week = WeeklyWindow.forInstant(now).startDate();
        CharacterObjectiveState objective = repository.findCharacterObjective(characterId, week, objectiveId)
                .orElse(null);
        if (objective == null || !objective.completed()) return ClaimResult.rejected("not_complete");
        if (objective.claimed()) return ClaimResult.rejected("already_claimed");

        AccountWeeklyState account = repository.findAccountState(accountId, week)
                .orElse(new AccountWeeklyState(accountId, week, 0, 0));

        int weeklyBudget = WeeklyProgressionPolicy.weeklyCorePoints(characterLevel);
        int totalAvailable = weeklyBudget + account.catchupPointsBank();
        int remaining = Math.max(0, totalAvailable - account.rewardPointsClaimed());
        int requested = WeeklyProgressionPolicy.clampAward(characterLevel, definition.pointReward());
        int awarded = Math.min(requested, remaining);
        if (awarded <= 0) return ClaimResult.rejected("account_budget_exhausted");

        repository.saveAccountState(account.withClaimedPoints(awarded));
        repository.saveCharacterObjective(new CharacterObjectiveState(
                objective.characterId(), objective.weekStartUtc(), objective.objectiveId(),
                objective.progressCount(), objective.completedAt(), now
        ));
        return ClaimResult.awarded(awarded);
    }

    public record ClaimResult(boolean success, int pointsAwarded, String reason) {
        public static ClaimResult awarded(int points) {
            return new ClaimResult(true, points, "awarded");
        }

        public static ClaimResult rejected(String reason) {
            return new ClaimResult(false, 0, reason);
        }
    }
}
