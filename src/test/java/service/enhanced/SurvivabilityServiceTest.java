package service.enhanced;

import client.Character;
import client.Job;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class SurvivabilityServiceTest {

    private final SurvivabilityService service = new SurvivabilityService();

    @Test
    void raisesCharacterOnlyToMissingFloor() {
        Character chr = mock(Character.class);
        when(chr.getJob()).thenReturn(Job.NIGHTLORD);
        when(chr.getLevel()).thenReturn(120);
        when(chr.getMaxHp()).thenReturn(4000);

        int increase = service.applyCurrentFloor(chr);

        assertEquals(1500, increase);
        verify(chr).setMaxHp(5500);
    }

    @Test
    void leavesCharacterAboveFloorUntouched() {
        Character chr = mock(Character.class);
        when(chr.getJob()).thenReturn(Job.NIGHTLORD);
        when(chr.getLevel()).thenReturn(120);
        when(chr.getMaxHp()).thenReturn(7000);

        int increase = service.applyCurrentFloor(chr);

        assertEquals(0, increase);
        verify(chr, never()).setMaxHp(org.mockito.ArgumentMatchers.anyInt());
    }

    @Test
    void rejectsNullCharacter() {
        assertThrows(IllegalArgumentException.class, () -> service.applyCurrentFloor(null));
    }
}
