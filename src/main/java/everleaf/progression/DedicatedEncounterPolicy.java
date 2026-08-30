package everleaf.progression;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

/** Stateless validation used before allocating a server event instance. */
public final class DedicatedEncounterPolicy {
    private DedicatedEncounterPolicy() {}

    public static Set<Integer> validateParty(
            EnhancedBossDefinition definition,
            int leaderCharacterId,
            Collection<Integer> participantCharacterIds
    ) {
        if (definition == null) throw new IllegalArgumentException("definition cannot be null");
        if (participantCharacterIds == null) throw new IllegalArgumentException("participants cannot be null");

        Set<Integer> unique = new HashSet<>(participantCharacterIds);
        if (unique.size() != participantCharacterIds.size()) {
            throw new IllegalArgumentException("duplicate_participant");
        }
        if (!unique.contains(leaderCharacterId)) {
            throw new IllegalArgumentException("leader_not_in_party");
        }
        if (unique.size() < definition.partyMin()) {
            throw new IllegalStateException("party_too_small");
        }
        if (unique.size() > definition.partyMax()) {
            throw new IllegalStateException("party_too_large");
        }
        return Set.copyOf(unique);
    }
}
