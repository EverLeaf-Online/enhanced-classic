package everleaf.progression;

import java.time.Instant;
import java.time.LocalDate;
import java.util.Optional;

/** Persistence boundary for Everleaf's hybrid weekly progression model. */
public interface WeeklyProgressRepository {

    Optional<AccountWeeklyState> findAccountState(int accountId, LocalDate weekStartUtc);

    AccountWeeklyState saveAccountState(AccountWeeklyState state);

    Optional<CharacterObjectiveState> findCharacterObjective(
            int characterId,
            LocalDate weekStartUtc,
            String objectiveId
    );

    CharacterObjectiveState saveCharacterObjective(CharacterObjectiveState state);

    /**
     * Atomically consume account reward budget and mark the character objective
     * claimed. Implementations backed by a database must perform both writes in
     * one transaction and reject stale/already-claimed state.
     */
    ClaimCommitResult commitClaim(
            int accountId,
            int characterId,
            LocalDate weekStartUtc,
            String objectiveId,
            int pointsToAward,
            int maximumAccountPoints,
            Instant claimedAt
    );

    record ClaimCommitResult(boolean committed, int pointsAwarded, String reason) {
        public static ClaimCommitResult committed(int points) {
            return new ClaimCommitResult(true, points, "committed");
        }

        public static ClaimCommitResult rejected(String reason) {
            return new ClaimCommitResult(false, 0, reason);
        }
    }
}
