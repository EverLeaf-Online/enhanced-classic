-- EverLeaf modern 13x2 status-bar quickslots (26 entries).
-- Existing v83 quickslots stay in the BIGINT; the expanded mapping is stored
-- alongside it so rollback remains safe and no account data is rewritten.
SET @everleaf_qs_ext_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'quickslotkeymapped'
    AND COLUMN_NAME = 'keymap_ext'
);
SET @everleaf_qs_ext_sql := IF(
  @everleaf_qs_ext_exists = 0,
  'ALTER TABLE quickslotkeymapped ADD COLUMN keymap_ext VARBINARY(26) NULL AFTER keymap',
  'SELECT 1'
);
PREPARE everleaf_qs_ext_stmt FROM @everleaf_qs_ext_sql;
EXECUTE everleaf_qs_ext_stmt;
DEALLOCATE PREPARE everleaf_qs_ext_stmt;
