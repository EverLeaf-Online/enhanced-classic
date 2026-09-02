package everleaf.progression;

import java.util.List;

/** Persistence boundary for EverLeaf's account-bound PQ Points economy. */
public interface PqPointRepository {
    PqPointAccount getAccount(int accountId);

    MutationResult credit(int accountId, Integer characterId, int amount, String reasonType, String reasonKey, String metadata);

    MutationResult spend(int accountId, Integer characterId, int amount, String reasonType, String reasonKey, String metadata);

    List<PqPointLedgerEntry> recentLedger(int accountId, int limit);

    record MutationResult(boolean success, int amount, int balanceAfter, String reason) {
        public static MutationResult success(int amount, int balanceAfter) {
            return new MutationResult(true, amount, balanceAfter, "ok");
        }

        public static MutationResult rejected(String reason, int balanceAfter) {
            return new MutationResult(false, 0, balanceAfter, reason);
        }
    }
}
