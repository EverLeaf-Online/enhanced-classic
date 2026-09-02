package server;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockStatic;
import static org.mockito.Mockito.when;

import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Arrays;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;
import provider.Data;
import provider.DataProvider;
import provider.DataProviderFactory;
import provider.DataTool;
import provider.wz.WZFiles;
import scripting.event.EventInstanceManager;
import server.life.LifeFactory;
import server.life.Monster;
import server.life.NPC;
import server.maps.MapFactory;
import server.maps.MapleMap;
import tools.DatabaseConnection;

class WzDonorNinjaCastleRuntimeSmokeTest {
    private static final int SCRIPTED_PORTAL_TARGET_SENTINEL = 999999999;
    private static final int[] MAPS = {
        800040000, 800040100,
        800040200, 800040201, 800040202, 800040203, 800040204, 800040205, 800040206, 800040207,
        800040208, 800040209, 800040210, 800040211,
        800040300, 800040301, 800040302, 800040303, 800040304, 800040305, 800040306, 800040307,
        800040308, 800040309, 800040310, 800040311, 800040312, 800040313, 800040314, 800040315,
        800040400, 800040401, 800040410
    };
    private static final int[] MOBS = {
        9400400, 9400401, 9400402, 9400403, 9400404, 9400405, 9400406, 9400407, 9400408, 9400409, 9400410
    };
    private static final int[] NPCS = {
        9110100, 9110101, 9110102, 9110103, 9110104, 9110105, 9110106, 9110107,
        9110108, 9110109, 9110110, 9110111, 9110112, 9110113, 9110114
    };
    private static final int[] QUESTS = {8163, 8164, 8165, 8166, 8167, 8168, 8169, 8170, 8171};

    @BeforeAll
    static void requireExplicitStagingOptIn() {
        Assumptions.assumeTrue(
                Boolean.getBoolean("wz-donor-ninja-staging-smoke"),
                "Ninja Castle staging smoke is opt-in and must never run against canonical WZ implicitly");
        String wzPath = System.getProperty("wz-path");
        assertNotNull(wzPath, "wz-path must point at the disposable staged Ninja Castle WZ tree");
        assertFalse(wzPath.isBlank(), "wz-path must not be blank");
    }

    @Test
    void allFrozenMapsLoadThroughRealMapFactory() throws Exception {
        Connection connection = mock(Connection.class);
        PreparedStatement statement = mock(PreparedStatement.class);
        ResultSet resultSet = mock(ResultSet.class);
        when(connection.prepareStatement(anyString())).thenReturn(statement);
        when(statement.executeQuery()).thenReturn(resultSet);
        when(resultSet.next()).thenReturn(false);
        EventInstanceManager event = mock(EventInstanceManager.class);

        try (MockedStatic<DatabaseConnection> database = mockStatic(DatabaseConnection.class)) {
            database.when(DatabaseConnection::getConnection).thenReturn(connection);
            for (int mapId : MAPS) {
                MapleMap map = MapFactory.loadMapFromWz(mapId, 0, 1, event);
                assertNotNull(map, "map must load through real MapFactory: " + mapId);
                assertEquals(mapId, map.getId());
            }
        }
    }

    @Test
    void allFrozenMobsLoadAndReviveChainIsPreserved() {
        for (int mobId : MOBS) {
            Monster monster = LifeFactory.getMonster(mobId);
            assertNotNull(monster, "mob must load through real LifeFactory: " + mobId);
            assertEquals(mobId, monster.getId());
            assertNotEquals("MISSINGNO", monster.getName(), "mob String.wz name must resolve: " + mobId);
        }

        Monster firstBossForm = LifeFactory.getMonster(9400408);
        assertNotNull(firstBossForm);
        assertEquals(Arrays.asList(9400409), firstBossForm.getStats().getRevives());
        assertNotNull(LifeFactory.getMonster(9400409), "revived final form must load");
    }

    @Test
    void allFrozenNpcAssetsAndNamesResolve() {
        DataProvider npcProvider = DataProviderFactory.getDataProvider(WZFiles.NPC);
        for (int npcId : NPCS) {
            Data npcAsset = npcProvider.getData(npcId + ".img");
            assertNotNull(npcAsset, "Npc.wz asset must resolve: " + npcId);
            NPC npc = LifeFactory.getNPC(npcId);
            assertNotNull(npc);
            assertEquals(npcId, npc.getId());
            assertNotEquals("MISSINGNO", npc.getName(), "Npc String.wz name must resolve: " + npcId);
        }
    }

    @Test
    void bossPortalUsesScriptSentinelAndReviewedDestinationLoads() throws Exception {
        DataProvider mapProvider = DataProviderFactory.getDataProvider(WZFiles.MAP);
        Data source = mapProvider.getData("Map/Map8/800040401.img");
        assertNotNull(source);

        Data bossPortal = null;
        for (Data portal : source.getChildByPath("portal")) {
            if ("ninja_Boss".equals(DataTool.getString(portal.getChildByPath("script"), ""))) {
                bossPortal = portal;
                break;
            }
        }
        assertNotNull(bossPortal, "map 800040401 must contain scripted ninja_Boss portal");
        assertEquals(
                SCRIPTED_PORTAL_TARGET_SENTINEL,
                DataTool.getInt(bossPortal.getChildByPath("tm")),
                "scripted portals keep the WZ target sentinel; the reviewed JS owns the real warp destination");

        String portalScript = Files.readString(Path.of("scripts/portal/ninja_Boss.js"));
        assertTrue(portalScript.contains("pi.warp(800040410, \"out00\")"));

        Connection connection = mock(Connection.class);
        PreparedStatement statement = mock(PreparedStatement.class);
        ResultSet resultSet = mock(ResultSet.class);
        when(connection.prepareStatement(anyString())).thenReturn(statement);
        when(statement.executeQuery()).thenReturn(resultSet);
        when(resultSet.next()).thenReturn(false);
        EventInstanceManager event = mock(EventInstanceManager.class);
        try (MockedStatic<DatabaseConnection> database = mockStatic(DatabaseConnection.class)) {
            database.when(DatabaseConnection::getConnection).thenReturn(connection);
            MapleMap target = MapFactory.loadMapFromWz(800040410, 0, 1, event);
            assertNotNull(target);
            assertNotNull(target.getPortal("out00"), "ninja_Boss reviewed target map must expose out00 portal");
        }
    }

    @Test
    void frozenQuestNodesExistAcrossRealQuestProvider() {
        DataProvider questProvider = DataProviderFactory.getDataProvider(WZFiles.QUEST);
        Data check = questProvider.getData("Check.img");
        Data act = questProvider.getData("Act.img");
        Data info = questProvider.getData("QuestInfo.img");
        assertNotNull(check);
        assertNotNull(act);
        assertNotNull(info);

        for (int questId : QUESTS) {
            String id = Integer.toString(questId);
            assertTrue(hasQuestNode(check, id), "Check.img must contain quest " + id);
            assertTrue(hasQuestNode(act, id), "Act.img must contain quest " + id);
            assertTrue(hasQuestNode(info, id), "QuestInfo.img must contain quest " + id);
        }
    }

    private static boolean hasQuestNode(Data root, String questId) {
        if (root.getChildByPath(questId) != null) {
            return true;
        }
        for (Data child : root) {
            if (child.getChildByPath(questId) != null) {
                return true;
            }
        }
        return false;
    }
}
