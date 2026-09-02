package everleaf.progression;

/** Immutable snapshot of an account's PQ Point balance. */
public record PqPointAccount(
        int accountId,
        int balance,
        long lifetimeEarned,
        long lifetimeSpent
) {
    public PqPointAccount {
        if (accountId <= 0) throw new IllegalArgumentException("accountId must be positive");
        if (balance < 0) throw new IllegalArgumentException("balance cannot be negative");
        if (lifetimeEarned < 0 || lifetimeSpent < 0) {
            throw new IllegalArgumentException("lifetime totals cannot be negative");
        }
    }
}
