package everleaf.progression;

import java.util.Map;

/**
 * Server-side forge recipe contract. Inputs are symbolic progression resource
 * ids, keeping economy policy separate from concrete Maple item bindings.
 */
public record ForgeRecipeDefinition(
        String id,
        String displayName,
        int requiredLevel,
        String requiredUnlock,
        Map<String, Integer> inputs,
        String outputTag,
        boolean bestInSlotOutput
) {
    public ForgeRecipeDefinition {
        if (id == null || id.isBlank()) throw new IllegalArgumentException("id cannot be blank");
        if (displayName == null || displayName.isBlank()) throw new IllegalArgumentException("displayName cannot be blank");
        if (requiredLevel < 200 || requiredLevel > 250) throw new IllegalArgumentException("invalid endgame level");
        if (requiredUnlock == null || requiredUnlock.isBlank()) throw new IllegalArgumentException("requiredUnlock cannot be blank");
        if (inputs == null || inputs.isEmpty()) throw new IllegalArgumentException("inputs cannot be empty");
        inputs = Map.copyOf(inputs);
        if (inputs.values().stream().anyMatch(value -> value == null || value <= 0)) {
            throw new IllegalArgumentException("input quantities must be positive");
        }
        if (outputTag == null || outputTag.isBlank()) throw new IllegalArgumentException("outputTag cannot be blank");
    }
}
