package everleaf.progression;

/**
 * Concrete server/WZ identifiers used by an enhanced encounter adapter.
 * Kept separate from progression definitions so map/monster choices can change
 * without changing access and reward policy.
 */
public record EncounterMapBinding(
        String encounterId,
        String classicEventScript,
        int entryMapId,
        int exitMapId,
        int completionMonsterId
) {
    public EncounterMapBinding {
        if (encounterId == null || encounterId.isBlank()) throw new IllegalArgumentException("encounterId cannot be blank");
        if (classicEventScript == null || classicEventScript.isBlank()) throw new IllegalArgumentException("classicEventScript cannot be blank");
        if (entryMapId <= 0 || exitMapId <= 0 || completionMonsterId <= 0) throw new IllegalArgumentException("ids must be positive");
    }
}
