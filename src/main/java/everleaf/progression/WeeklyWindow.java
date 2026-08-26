package everleaf.progression;

import java.time.DayOfWeek;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.time.temporal.TemporalAdjusters;

/**
 * Stable Monday 00:00 UTC weekly window used by progression persistence.
 */
public record WeeklyWindow(LocalDate startDate, LocalDate endDateExclusive) {
    public WeeklyWindow {
        if (startDate == null || endDateExclusive == null || !endDateExclusive.equals(startDate.plusDays(7))) {
            throw new IllegalArgumentException("weekly window must span exactly seven days");
        }
    }

    public static WeeklyWindow forInstant(Instant instant) {
        if (instant == null) throw new IllegalArgumentException("instant cannot be null");
        LocalDate date = instant.atZone(ZoneOffset.UTC).toLocalDate();
        LocalDate monday = date.with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY));
        return new WeeklyWindow(monday, monday.plusDays(7));
    }

    public String key() {
        return startDate.toString();
    }

    public boolean contains(Instant instant) {
        if (instant == null) return false;
        LocalDate date = instant.atZone(ZoneOffset.UTC).toLocalDate();
        return !date.isBefore(startDate) && date.isBefore(endDateExclusive);
    }
}
