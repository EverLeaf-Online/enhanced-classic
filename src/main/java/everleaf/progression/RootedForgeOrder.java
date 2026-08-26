package everleaf.progression;

import java.time.Instant;

/** Durable handoff between atomic forge payment and inventory fulfillment. */
public record RootedForgeOrder(
        long id,
        int accountId,
        int characterId,
        RootedForgeRecipe recipe,
        RootedForgeTarget target,
        String requestKey,
        Status status,
        Instant createdAt
) {
    public RootedForgeOrder {
        if (id <= 0) throw new IllegalArgumentException("id must be positive");
        if (accountId <= 0) throw new IllegalArgumentException("accountId must be positive");
        if (characterId <= 0) throw new IllegalArgumentException("characterId must be positive");
        if (recipe == null) throw new IllegalArgumentException("recipe cannot be null");
        if (target == null) throw new IllegalArgumentException("target cannot be null");
        if (requestKey == null || requestKey.isBlank()) throw new IllegalArgumentException("requestKey cannot be blank");
        if (status == null) throw new IllegalArgumentException("status cannot be null");
        if (createdAt == null) throw new IllegalArgumentException("createdAt cannot be null");
    }

    public enum Status { PENDING, FULFILLED }
}
