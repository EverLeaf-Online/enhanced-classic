package everleaf.progression;

import java.util.Map;

/**
 * Deterministic Rooted-tier equipment outcomes. Item-id binding is deliberately
 * deferred to the inventory adapter so these balance contracts stay independent
 * of WZ/client data and can be tested safely.
 */
public final class RootedForgeOutcomeCatalog {
    private RootedForgeOutcomeCatalog() {}

    public record Outcome(
            RootedForgeRecipe recipe,
            int stage,
            ForgeStatDelta statDelta,
            ForgeOutcomePolicy policy
    ) {
        public Outcome {
            if (recipe == null) throw new IllegalArgumentException("recipe cannot be null");
            if (stage < 1) throw new IllegalArgumentException("stage must be positive");
            if (statDelta == null) throw new IllegalArgumentException("statDelta cannot be null");
            if (policy == null) throw new IllegalArgumentException("policy cannot be null");
        }
    }

    private static final Map<RootedForgeRecipe, Outcome> OUTCOMES = Map.of(
            RootedForgeRecipe.ROOTED_WEAPON_REFINEMENT,
            new Outcome(
                    RootedForgeRecipe.ROOTED_WEAPON_REFINEMENT,
                    1,
                    ForgeStatDelta.weaponStageOne(),
                    ForgeOutcomePolicy.everleafDefault()
            ),
            RootedForgeRecipe.ROOTED_ARMOR_REFINEMENT,
            new Outcome(
                    RootedForgeRecipe.ROOTED_ARMOR_REFINEMENT,
                    1,
                    ForgeStatDelta.armorStageOne(),
                    ForgeOutcomePolicy.everleafDefault()
            )
    );

    public static Outcome byRecipe(RootedForgeRecipe recipe) {
        Outcome outcome = OUTCOMES.get(recipe);
        if (outcome == null) throw new IllegalArgumentException("No deterministic outcome for recipe: " + recipe);
        return outcome;
    }
}
