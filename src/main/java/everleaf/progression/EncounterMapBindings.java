package everleaf.progression;

import java.util.Map;

/** Concrete bindings added only when the underlying classic assets are verified. */
public final class EncounterMapBindings {
    private EncounterMapBindings() {}

    private static final Map<String, EncounterMapBinding> BINDINGS = Map.of(
            "rooted_zakum", new EncounterMapBinding(
                    "rooted_zakum",
                    "ZakumBattle",
                    280030000,
                    211042400,
                    8800002
            )
    );

    public static EncounterMapBinding byEncounterId(String encounterId) {
        EncounterMapBinding binding = BINDINGS.get(encounterId);
        if (binding == null) throw new IllegalArgumentException("unbound enhanced encounter: " + encounterId);
        return binding;
    }

    public static boolean isBound(String encounterId) {
        return BINDINGS.containsKey(encounterId);
    }
}
