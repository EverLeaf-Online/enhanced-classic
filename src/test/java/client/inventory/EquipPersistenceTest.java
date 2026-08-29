package client.inventory;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.CALLS_REAL_METHODS;
import static org.mockito.Mockito.mock;

class EquipPersistenceTest {
    @Test
    void forgeStageRoundTripsInMemory() {
        Equip equip = mock(Equip.class, CALLS_REAL_METHODS);
        equip.setEverleafForgeStage((byte) 2);

        assertEquals(2, equip.getEverleafForgeStage());
    }

    @Test
    void forgeStageCannotBeNegative() {
        Equip equip = mock(Equip.class, CALLS_REAL_METHODS);

        assertThrows(IllegalArgumentException.class, () -> equip.setEverleafForgeStage((byte) -1));
    }

    @Test
    void equipmentInsertNamesEveryPersistedColumn() {
        String sql = ItemFactory.INVENTORY_EQUIPMENT_INSERT_SQL;

        assertTrue(sql.contains("`everleaf_forge_stage`"));
        assertEquals(24, sql.chars().filter(character -> character == '?').count());
    }
}
