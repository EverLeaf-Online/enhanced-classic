package everleaf.progression;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class WeeklyObjectiveCatalogTest {

    @Test
    void preEndgameHasNoWeeklyObjectives() {
        assertTrue(WeeklyObjectiveCatalog.eligibleForLevel(199).isEmpty());
    }

    @Test
    void rootedObjectivesExcludeGuildLane() {
        List<WeeklyObjectiveDefinition> objectives = WeeklyObjectiveCatalog.eligibleForLevel(200);
        assertFalse(objectives.isEmpty());
        assertTrue(objectives.stream().noneMatch(o -> o.lane() == EndgameRewardLane.GUILD));
    }

    @Test
    void awakenedUnlocksGuildObjective() {
        assertTrue(WeeklyObjectiveCatalog.eligibleForLevel(210).stream()
                .anyMatch(o -> o.id().equals("awakened_guild")));
    }

    @Test
    void higherTiersAccumulateEligibleTemplates() {
        int rooted = WeeklyObjectiveCatalog.eligibleForLevel(200).size();
        int ascendant = WeeklyObjectiveCatalog.eligibleForLevel(225).size();
        int evergreen = WeeklyObjectiveCatalog.eligibleForLevel(250).size();
        assertTrue(ascendant > rooted);
        assertTrue(evergreen > ascendant);
    }

    @Test
    void idsResolveDeterministically() {
        WeeklyObjectiveDefinition objective = WeeklyObjectiveCatalog.byId("rooted_boss_hunt");
        assertEquals(EndgameRewardLane.BOSS, objective.lane());
        assertThrows(IllegalArgumentException.class, () -> WeeklyObjectiveCatalog.byId("missing"));
    }

    @Test
    void definitionsAreImmutable() {
        assertThrows(UnsupportedOperationException.class,
                () -> WeeklyObjectiveCatalog.all().add(WeeklyObjectiveCatalog.byId("rooted_boss_hunt")));
    }
}
