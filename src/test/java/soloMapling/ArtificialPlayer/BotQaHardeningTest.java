package soloMapling.ArtificialPlayer;

import org.junit.jupiter.api.Test;
import server.Storage;

import java.util.LinkedHashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class BotQaHardeningTest {

    @Test
    void deterministicFleetJobsReceiveClassAppropriateWeaponsAndStats() {
        assertEquals(1302000, BotQaLoadout.weaponForJob(112));   // Hero sword
        assertEquals(1372000, BotQaLoadout.weaponForJob(212));   // Arch Mage wand
        assertEquals(1452002, BotQaLoadout.weaponForJob(312));   // Bowmaster bow
        assertEquals(1472000, BotQaLoadout.weaponForJob(412));   // Night Lord claw
        assertEquals(1482000, BotQaLoadout.weaponForJob(512));   // Buccaneer knuckle
        assertEquals(1492000, BotQaLoadout.weaponForJob(522));   // Corsair gun
        assertEquals(1442000, BotQaLoadout.weaponForJob(2112));  // Aran polearm

        BotQaLoadout.StatProfile warrior = BotQaLoadout.statsForJob(112);
        BotQaLoadout.StatProfile mage = BotQaLoadout.statsForJob(212);
        BotQaLoadout.StatProfile thief = BotQaLoadout.statsForJob(412);
        BotQaLoadout.StatProfile bowman = BotQaLoadout.statsForJob(312);
        assertTrue(warrior.str() > warrior.dex());
        assertTrue(mage.intel() > mage.luk());
        assertTrue(thief.luk() > thief.dex());
        assertTrue(bowman.dex() > bowman.str());
    }

    @Test
    void conservationLedgerDetectsCreationAndExactConservation() {
        BotQaLedger.Snapshot before = new BotQaLedger.Snapshot(10_000L, Map.of(2000000, 100L, 4000000, 5L));
        BotQaLedger.Snapshot same = new BotQaLedger.Snapshot(10_000L, Map.of(2000000, 100L, 4000000, 5L));
        BotQaLedger.Snapshot duped = new BotQaLedger.Snapshot(11_000L, Map.of(2000000, 101L, 4000000, 5L));

        assertTrue(BotQaLedger.compare(before, same).fullyConserved());
        assertFalse(BotQaLedger.noItemCreation(before, duped));
        assertFalse(BotQaLedger.noMesoCreation(before, duped));
        assertEquals(100L, BotQaLedger.quantity(before, 2000000));
    }

    @Test
    void transientQaStorageCannotBeMistakenForPersistedStorage() {
        Storage storage = Storage.createTransientQaStorage(16, 0);
        assertTrue(storage.isTransientQaStorage());
        assertEquals(16, storage.getSlots());
        assertEquals(0, storage.getMeso());
        assertThrows(IllegalStateException.class, () -> storage.saveToDB(null));
    }

    @Test
    void suiteAndSoakFailClosedWithoutExplicitArmToken() {
        assertFalse(BotQaSuiteRunner.start(1, 1, 100000000, 3).success());
        assertEquals("explicit-arm-token-required",
                BotQaSuiteRunner.start(1, 1, 100000000, 3).reason());
        assertFalse(BotQaSoakRunner.start(1, 1).success());
        assertEquals("explicit-arm-token-required", BotQaSoakRunner.start(1, 1).reason());
    }

    @Test
    void machineReadableReportJsonEscapesUnsafeText() {
        Map<String, Object> fields = new LinkedHashMap<>();
        fields.put("success", true);
        fields.put("count", 3);
        fields.put("reason", "quote\" newline\n");
        String json = BotQaReport.toJson(fields);
        assertTrue(json.startsWith("{"));
        assertTrue(json.endsWith("}"));
        assertTrue(json.contains("\"success\":true"));
        assertTrue(json.contains("\"count\":3"));
        assertTrue(json.contains("quote\\\" newline\\n"));
    }
}
