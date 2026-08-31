package client.inventory;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ItemFactoryPersistenceTest {
    @Test
    void equipmentInsertNamesTheForgeStageAndAllValues() {
        String sql = ItemFactory.INVENTORY_EQUIPMENT_INSERT_SQL;

        assertTrue(sql.contains("`everleaf_forge_stage`"));
        assertEquals(24, sql.chars().filter(character -> character == '?').count());
    }
}
