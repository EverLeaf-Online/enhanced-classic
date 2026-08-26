package everleaf.progression;

import java.util.Optional;

/** Atomic payment and durable fulfillment storage for Rooted forging. */
public interface RootedForgeRepository {
    PurchaseResult purchase(int accountId, int characterId, RootedForgeRecipe recipe, RootedForgeTarget target, String requestKey);

    Optional<RootedForgeOrder> findByRequestKey(int accountId, String requestKey);

    Optional<RootedForgeOrder> findById(long orderId);

    boolean markFulfilled(long orderId);

    record PurchaseResult(boolean applied, String reason, RootedForgeOrder order) {
        public static PurchaseResult success(RootedForgeOrder order) {
            return new PurchaseResult(true, "ok", order);
        }

        public static PurchaseResult rejected(String reason) {
            return new PurchaseResult(false, reason, null);
        }

        public static PurchaseResult duplicate(RootedForgeOrder order) {
            return new PurchaseResult(false, "duplicate_request", order);
        }
    }
}
