package everleaf.progression;

import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.time.LocalDate;

import static org.junit.jupiter.api.Assertions.*;

class WeeklyWindowTest {

    @Test
    void weekStartsMondayUtc() {
        WeeklyWindow window = WeeklyWindow.forInstant(Instant.parse("2026-08-26T06:00:00Z"));
        assertEquals(LocalDate.of(2026, 8, 24), window.startDate());
        assertEquals(LocalDate.of(2026, 8, 31), window.endDateExclusive());
        assertEquals("2026-08-24", window.key());
    }

    @Test
    void boundaryMovesAtMondayMidnightUtc() {
        WeeklyWindow before = WeeklyWindow.forInstant(Instant.parse("2026-08-30T23:59:59Z"));
        WeeklyWindow after = WeeklyWindow.forInstant(Instant.parse("2026-08-31T00:00:00Z"));
        assertNotEquals(before.key(), after.key());
        assertFalse(before.contains(Instant.parse("2026-08-31T00:00:00Z")));
        assertTrue(after.contains(Instant.parse("2026-08-31T00:00:00Z")));
    }
}
