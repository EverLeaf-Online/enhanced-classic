package everleaf.progression;

import java.time.Instant;

/** Immutable PQ Point audit record. */
public record PqPointLedgerEntry(
        long id,
        int accountId,
        Integer characterId,
        int amount,
        int balanceAfter,
        String reasonType,
        String reasonKey,
        String metadata,
        Instant createdAt
) {
    public PqPointLedgerEntry {
        if (id < 0) throw new IllegalArgumentException("id cannot be negative");
        if (accountId <= 0) throw new IllegalArgumentException("accountId must be positive");
        if (amount == 0) throw new IllegalArgumentException("amount cannot be zero");
        if (balanceAfter < 0) throw new IllegalArgumentException("balanceAfter cannot be negative");
        if (reasonType == null || reasonType.isBlank()) throw new IllegalArgumentException("reasonType cannot be blank");
        if (reasonKey == null || reasonKey.isBlank()) throw new IllegalArgumentException("reasonKey cannot be blank");
        if (createdAt == null) throw new IllegalArgumentException("createdAt cannot be null");
    }
}
