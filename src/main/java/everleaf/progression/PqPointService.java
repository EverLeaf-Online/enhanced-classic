package everleaf.progression;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.OptionalInt;

/** Application service for EverLeaf's account-bound PQ Points economy. */
public final class PqPointService {
    public static final String CURRENCY_NAME = "PQ Points";

    private static final Map<String, Integer> CLEAR_AWARDS;

    static {
        Map<String, Integer> awards = new LinkedHashMap<>();
        awards.put("HenesysPQ", 1);
        awards.put("KerningPQ", 1);
        awards.put("LudiPQ", 2);
        awards.put("LudiMazePQ", 2);
        awards.put("EllinPQ", 3);
        awards.put("OrbisPQ", 3);
        awards.put("PiratePQ", 3);
        awards.put("MagatiaPQ_A", 4);
        awards.put("MagatiaPQ_Z", 4);
        awards.put("AmoriaPQ", 4);
        awards.put("CWKPQ", 6);
        CLEAR_AWARDS = Map.copyOf(awards);
    }

    private final PqPointRepository repository;

    public PqPointService(PqPointRepository repository) {
        if (repository == null) throw new IllegalArgumentException("repository cannot be null");
        this.repository = repository;
    }

    public PqPointAccount account(int accountId) {
        return repository.getAccount(accountId);
    }

    public OptionalInt clearAward(String eventName) {
        Integer award = CLEAR_AWARDS.get(eventName);
        return award == null ? OptionalInt.empty() : OptionalInt.of(award);
    }

    public boolean isEligiblePq(String eventName) {
        return CLEAR_AWARDS.containsKey(eventName);
    }

    public Map<String, Integer> clearAwards() {
        return CLEAR_AWARDS;
    }

    /**
     * Award an eligible PQ clear exactly once per account and event instance.
     * The unique ledger key prevents duplicate payout if a script accidentally
     * signals clear twice or reconnect cleanup re-enters the completion path.
     */
    public PqPointRepository.MutationResult awardClear(
            int accountId,
            int characterId,
            String eventName,
            String instanceName
    ) {
        if (eventName == null || eventName.isBlank()) {
            return PqPointRepository.MutationResult.rejected("unknown_event", account(accountId).balance());
        }
        Integer amount = CLEAR_AWARDS.get(eventName);
        if (amount == null) {
            return PqPointRepository.MutationResult.rejected("not_pq_whitelist", account(accountId).balance());
        }
        if (instanceName == null || instanceName.isBlank()) {
            throw new IllegalArgumentException("instanceName cannot be blank");
        }

        return repository.credit(
                accountId,
                characterId,
                amount,
                "PQ_CLEAR",
                eventName + ":" + instanceName,
                "event=" + eventName
        );
    }

    public PqPointRepository.MutationResult spend(
            int accountId,
            int characterId,
            int amount,
            String purchaseKey,
            String metadata
    ) {
        if (amount <= 0) throw new IllegalArgumentException("amount must be positive");
        if (purchaseKey == null || purchaseKey.isBlank()) throw new IllegalArgumentException("purchaseKey cannot be blank");
        return repository.spend(accountId, characterId, amount, "PQ_SHOP", purchaseKey, metadata);
    }

    public List<PqPointLedgerEntry> recentLedger(int accountId, int limit) {
        if (limit < 1 || limit > 100) throw new IllegalArgumentException("limit must be 1-100");
        return repository.recentLedger(accountId, limit);
    }
}
