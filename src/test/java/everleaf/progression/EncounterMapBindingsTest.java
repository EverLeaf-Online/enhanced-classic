package everleaf.progression;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class EncounterMapBindingsTest {
    @Test
    void rootedZakumUsesVerifiedClassicAssets() {
        EncounterMapBinding binding = EncounterMapBindings.byEncounterId("rooted_zakum");
        assertEquals("ZakumBattle", binding.classicEventScript());
        assertEquals(280030000, binding.entryMapId());
        assertEquals(211042400, binding.exitMapId());
        assertEquals(8800002, binding.completionMonsterId());
    }

    @Test
    void unimplementedHigherTierBindingsStayExplicitlyUnbound() {
        assertFalse(EncounterMapBindings.isBound("awakened_horntail"));
        assertThrows(IllegalArgumentException.class,
                () -> EncounterMapBindings.byEncounterId("awakened_horntail"));
    }
}
