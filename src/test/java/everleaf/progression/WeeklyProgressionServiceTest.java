package everleaf.progression;

import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.time.LocalDate;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

class WeeklyProgressionServiceTest {

    @Test
    void objectivesAreCharacterScopedButBudgetIsAccountScoped() {
        MemoryRepository repository = new MemoryRepository();
        WeeklyProgressionService service = new WeeklyProgressionService(repository);
        Instant now = Instant.parse("2026-08-26T06:00:00Z");

        service.addProgress(101, 200, "rooted_boss_hunt", 3, now);
        var first = service.claim(1, 101, 200, "rooted_boss_hunt", now);
        assertTrue(first.success());
        assertEquals(40, first.pointsAwarded());

        service.addProgress(102, 200, "rooted_party_clear", 3, now);
        var second = service.claim(1, 102, 200, "rooted_party_clear", now);
        assertTrue(second.success());
        assertEquals(35, second.pointsAwarded());

        service.addProgress(102, 200, "rooted_collection", 5, now);
        var third = service.claim(1, 102, 200, "rooted_collection", now);
        assertTrue(third.success());
        assertEquals(25, third.pointsAwarded());

        assertEquals(100, repository.accountStates.values().iterator().next().rewardPointsClaimed());
    }

    @Test
    void claimCannotExceedSharedAccountBudget() {
        MemoryRepository repository = new MemoryRepository();
        WeeklyProgressionService service = new WeeklyProgressionService(repository);
        Instant now = Instant.parse("2026-08-26T06:00:00Z");
        LocalDate week = WeeklyWindow.forInstant(now).startDate();
        repository.saveAccountState(new AccountWeeklyState(1, week, 90, 0));

        service.addProgress(201, 200, "rooted_boss_hunt", 3, now);
        var result = service.claim(1, 201, 200, "rooted_boss_hunt", now);

        assertTrue(result.success());
        assertEquals(10, result.pointsAwarded());
        assertEquals(100, repository.findAccountState(1, week).orElseThrow().rewardPointsClaimed());
    }

    @Test
    void completedObjectiveCannotBeClaimedTwice() {
        MemoryRepository repository = new MemoryRepository();
        WeeklyProgressionService service = new WeeklyProgressionService(repository);
        Instant now = Instant.parse("2026-08-26T06:00:00Z");

        service.addProgress(301, 200, "rooted_collection", 5, now);
        assertTrue(service.claim(3, 301, 200, "rooted_collection", now).success());
        assertEquals("already_claimed", service.claim(3, 301, 200, "rooted_collection", now).reason());
    }

    private static final class MemoryRepository implements WeeklyProgressRepository {
        private final Map<String, AccountWeeklyState> accountStates = new HashMap<>();
        private final Map<String, CharacterObjectiveState> characterStates = new HashMap<>();

        @Override
        public Optional<AccountWeeklyState> findAccountState(int accountId, LocalDate weekStartUtc) {
            return Optional.ofNullable(accountStates.get(accountId + ":" + weekStartUtc));
        }

        @Override
        public AccountWeeklyState saveAccountState(AccountWeeklyState state) {
            accountStates.put(state.accountId() + ":" + state.weekStartUtc(), state);
            return state;
        }

        @Override
        public Optional<CharacterObjectiveState> findCharacterObjective(int characterId, LocalDate weekStartUtc, String objectiveId) {
            return Optional.ofNullable(characterStates.get(characterId + ":" + weekStartUtc + ":" + objectiveId));
        }

        @Override
        public CharacterObjectiveState saveCharacterObjective(CharacterObjectiveState state) {
            characterStates.put(state.characterId() + ":" + state.weekStartUtc() + ":" + state.objectiveId(), state);
            return state;
        }

        @Override
        public ClaimCommitResult commitClaim(int accountId, int characterId, LocalDate weekStartUtc, String objectiveId,
                                             int pointsToAward, int maximumAccountPoints, Instant claimedAt) {
            CharacterObjectiveState objective = findCharacterObjective(characterId, weekStartUtc, objectiveId).orElse(null);
            if (objective == null || !objective.completed()) return ClaimCommitResult.rejected("not_complete");
            if (objective.claimed()) return ClaimCommitResult.rejected("already_claimed");

            AccountWeeklyState account = findAccountState(accountId, weekStartUtc)
                    .orElse(new AccountWeeklyState(accountId, weekStartUtc, 0, 0));
            int remaining = Math.max(0, maximumAccountPoints - account.rewardPointsClaimed());
            int awarded = Math.min(pointsToAward, remaining);
            if (awarded <= 0) return ClaimCommitResult.rejected("account_budget_exhausted");

            saveAccountState(account.withClaimedPoints(awarded));
            saveCharacterObjective(new CharacterObjectiveState(
                    objective.characterId(), objective.weekStartUtc(), objective.objectiveId(),
                    objective.progressCount(), objective.completedAt(), claimedAt
            ));
            return ClaimCommitResult.committed(awarded);
        }
    }
}
