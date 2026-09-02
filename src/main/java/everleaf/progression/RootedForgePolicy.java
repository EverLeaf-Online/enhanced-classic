package everleaf.progression;

import java.util.Map;

/** Pure forge validation; actual transactional spending is handled by persistence adapters. */
public final class RootedForgePolicy {
    private RootedForgePolicy() {}

    public record Check(boolean allowed, String reason) {
        public static Check allow() { return new Check(true, "ok"); }
        public static Check deny(String reason) { return new Check(false, reason); }
    }

    public static Check canCraft(RootedForgeRecipe recipe, int verdantMarks, Map<RootedMaterial, Integer> balances) {
        if (recipe == null) return Check.deny("Unknown forge recipe.");
        if (balances == null) return Check.deny("Material balances are unavailable.");
        if (verdantMarks < recipe.verdantMarkCost()) return Check.deny("Not enough Verdant Marks.");

        for (var cost : recipe.materialCosts().entrySet()) {
            if (balances.getOrDefault(cost.getKey(), 0) < cost.getValue()) {
                return Check.deny("Not enough " + cost.getKey().displayName() + ".");
            }
        }
        return Check.allow();
    }
}
