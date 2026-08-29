-- Required by the EverLeaf equipment persistence model.
-- Safe to run repeatedly and safe for databases that already contain the Rooted forge column.

SET @everleaf_forge_stage_exists = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'inventoryequipment'
      AND column_name = 'everleaf_forge_stage'
);
SET @everleaf_forge_stage_ddl = IF(
    @everleaf_forge_stage_exists = 0,
    'ALTER TABLE inventoryequipment ADD COLUMN everleaf_forge_stage TINYINT UNSIGNED NOT NULL DEFAULT 0 AFTER ringid',
    'SELECT 1'
);
PREPARE everleaf_forge_stage_statement FROM @everleaf_forge_stage_ddl;
EXECUTE everleaf_forge_stage_statement;
DEALLOCATE PREPARE everleaf_forge_stage_statement;
