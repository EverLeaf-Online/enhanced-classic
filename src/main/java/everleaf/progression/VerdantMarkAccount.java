package everleaf.progression;

/** Immutable account-bound Verdant Marks balance snapshot. */
public record VerdantMarkAccount(
        int accountId,
        int balance,
        long lifetimeEarned,
        long lifetimeSpent
) {
    public VerdantMarkAccount {
        if (accountId <= 0) throw new IllegalArgumentException("accountId must be positive");
        if (balance < 0) throw new IllegalArgumentException("balance cannot be negative");
        if (lifetimeEarned < 0 || lifetimeSpent < 0) {
            throw new IllegalArgumentException("lifetime totals cannot be negative");
        }
    }
}
