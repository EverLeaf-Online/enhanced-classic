package everleaf.progression;

import java.util.List;

/** Application service for the account-bound Verdant Marks economy. */
public final class VerdantMarkService {
    public static final String CURRENCY_NAME = "Verdant Marks";

    private final VerdantMarkRepository repository;

    public VerdantMarkService(VerdantMarkRepository repository) {
        if (repository == null) throw new IllegalArgumentException("repository cannot be null");
        this.repository = repository;
    }

    public VerdantMarkAccount account(int accountId) {
        return repository.getAccount(accountId);
    }

    public VerdantMarkRepository.MutationResult awardWeekly(
            int accountId,
            int characterId,
            int amount,
            String weekKey,
            String objectiveId
    ) {
        if (amount <= 0) throw new IllegalArgumentException("amount must be positive");
        return repository.credit(
                accountId,
                characterId,
                amount,
                "WEEKLY_OBJECTIVE",
                weekKey + ":" + objectiveId,
                "objective=" + objectiveId
        );
    }

    public VerdantMarkRepository.MutationResult spend(
            int accountId,
            int characterId,
            int amount,
            String purchaseKey,
            String metadata
    ) {
        if (amount <= 0) throw new IllegalArgumentException("amount must be positive");
        if (purchaseKey == null || purchaseKey.isBlank()) throw new IllegalArgumentException("purchaseKey cannot be blank");
        return repository.spend(accountId, characterId, amount, "REWARD_SHOP", purchaseKey, metadata);
    }

    public List<VerdantMarkLedgerEntry> recentLedger(int accountId, int limit) {
        if (limit < 1 || limit > 100) throw new IllegalArgumentException("limit must be 1-100");
        return repository.recentLedger(accountId, limit);
    }
}
