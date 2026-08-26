package everleaf.progression;

import java.util.Map;

/** Account-bound material storage for the Rooted forge lane. */
public interface RootedMaterialRepository {
    Map<RootedMaterial, Integer> balances(int accountId);

    MutationResult credit(int accountId, int characterId, RootedMaterial material, int amount, String reasonKey);

    MutationResult spend(int accountId, int characterId, RootedMaterial material, int amount, String reasonKey);

    record MutationResult(boolean applied, String reason, int balanceAfter) {
        public static MutationResult success(int balanceAfter) {
            return new MutationResult(true, "ok", balanceAfter);
        }

        public static MutationResult rejected(String reason, int balanceAfter) {
            return new MutationResult(false, reason, balanceAfter);
        }
    }
}
