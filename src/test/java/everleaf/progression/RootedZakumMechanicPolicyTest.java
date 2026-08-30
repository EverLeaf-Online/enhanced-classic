package everleaf.progression;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class RootedZakumMechanicPolicyTest {
    @Test
    void wavesEscalateBeforeHardEnrage() {
        var waves = RootedZakumMechanicPolicy.waves();
        assertEquals(3, waves.size());
        for (int i = 1; i < waves.size(); i++) {
            assertTrue(waves.get(i).delayMinutes() > waves.get(i - 1).delayMinutes());
            assertTrue(waves.get(i).count() > waves.get(i - 1).count());
            assertTrue(waves.get(i).hitPoints() > waves.get(i - 1).hitPoints());
        }
        assertTrue(waves.get(waves.size() - 1).delayMinutes()
                < RootedZakumMechanicPolicy.enrageWarningMinute());
        assertTrue(RootedZakumMechanicPolicy.enrageWarningMinute()
                < RootedZakumMechanicPolicy.hardEnrageMinute());
    }

    @Test
    void policyCannotBeMutatedAtRuntime() {
        assertThrows(UnsupportedOperationException.class,
                () -> RootedZakumMechanicPolicy.waves().clear());
    }
}
