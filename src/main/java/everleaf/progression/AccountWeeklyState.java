package everleaf.progression;

import java.time.LocalDate;

/** Account-scoped valuable weekly reward budget state. */
public record AccountWeeklyState(
        int accountId,
        LocalDate weekStartUtc,
        int rewardPointsClaimed,
        int catchupPointsBank
) {
    public AccountWeeklyState {
        if (accountId < 1) throw new IllegalArgumentException("accountId must be positive");
        if (weekStartUtc == null) throw new IllegalArgumentException("weekStartUtc cannot be null");
        if (rewardPointsClaimed < 0) throw new IllegalArgumentException("rewardPointsClaimed cannot be negative");
        if (catchupPointsBank < 0) throw new IllegalArgumentException("catchupPointsBank cannot be negative");
    }

    public AccountWeeklyState withClaimedPoints(int points) {
        if (points < 0) throw new IllegalArgumentException("points cannot be negative");
        return new AccountWeeklyState(accountId, weekStartUtc, rewardPointsClaimed + points, catchupPointsBank);
    }
}
