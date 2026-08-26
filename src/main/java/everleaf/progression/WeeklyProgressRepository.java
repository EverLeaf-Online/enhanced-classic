package everleaf.progression;

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
}
