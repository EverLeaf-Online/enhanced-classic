package everleaf.progression;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;

class AccountMilestoneServiceTest {

    @Test
    void collectionTracksUseThreeBoundedTiers() {
        assertEquals(0, AccountMilestoneTrack.MONSTER_BOOK.tierFor(49));
        assertEquals(1, AccountMilestoneTrack.MONSTER_BOOK.tierFor(50));
        assertEquals(2, AccountMilestoneTrack.MONSTER_BOOK.tierFor(150));
        assertEquals(3, AccountMilestoneTrack.MONSTER_BOOK.tierFor(300));
        assertEquals(3, AccountMilestoneTrack.MONSTER_BOOK.tierFor(9999));

        assertEquals(0, AccountMilestoneTrack.QUESTS.tierFor(49));
        assertEquals(1, AccountMilestoneTrack.QUESTS.tierFor(50));
        assertEquals(2, AccountMilestoneTrack.QUESTS.tierFor(150));
        assertEquals(3, AccountMilestoneTrack.QUESTS.tierFor(300));
    }

    @Test
    void legacyScoreCapsRosterSizeAndPerCharacterLevel() {
        assertEquals(800, AccountMilestoneService.linkedLevelScore(List.of(250, 240, 230, 220, 210, 200)));
        assertEquals(525, AccountMilestoneService.linkedLevelScore(List.of(250, 150, 100, 75, 70)));
        assertEquals(0, AccountMilestoneService.linkedLevelScore(List.of()));
    }

    @Test
    void legacyTrackRewardsMeaningfulAltsButCapsPower() {
        assertEquals(0, AccountMilestoneTrack.LEGACY.tierFor(199));
        assertEquals(1, AccountMilestoneTrack.LEGACY.tierFor(200));
        assertEquals(2, AccountMilestoneTrack.LEGACY.tierFor(400));
        assertEquals(3, AccountMilestoneTrack.LEGACY.tierFor(600));
        assertEquals(3, AccountMilestoneTrack.LEGACY.tierFor(800));
    }

    @Test
    void tracksMapToExistingThreeStepRingFamilies() {
        assertArrayEquals(new int[]{1112300, 1112301, 1112302}, AccountMilestoneTrack.MONSTER_BOOK.ringIds());
        assertArrayEquals(new int[]{1112303, 1112304, 1112305}, AccountMilestoneTrack.QUESTS.ringIds());
        assertArrayEquals(new int[]{1112306, 1112307, 1112308}, AccountMilestoneTrack.LEGACY.ringIds());
    }
}
