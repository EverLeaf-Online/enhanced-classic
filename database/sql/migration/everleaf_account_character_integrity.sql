-- EverLeaf account/character relationship guard.
--
-- Purpose:
--   Prevent a direct DELETE from accounts from leaving character rows behind.
--
-- This migration intentionally uses ON DELETE RESTRICT instead of CASCADE.
-- Character deletion has application-level cleanup for inventory, quests, pets,
-- social state, merchant state, etc.; cascading only the characters row would
-- bypass that cleanup and can leave legacy dependent tables orphaned.
--
-- Fail closed if historical orphaned character rows already exist. Audit and
-- remediate those rows first, then re-run this migration.

DROP PROCEDURE IF EXISTS everleaf_install_account_character_guard;
DELIMITER //
CREATE PROCEDURE everleaf_install_account_character_guard()
BEGIN
    DECLARE orphan_count BIGINT DEFAULT 0;
    DECLARE fk_count INT DEFAULT 0;
    DECLARE restrict_fk_count INT DEFAULT 0;

    SELECT COUNT(*)
      INTO orphan_count
      FROM characters c
      LEFT JOIN accounts a ON a.id = c.accountid
     WHERE a.id IS NULL;

    IF orphan_count <> 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'EverLeaf account/character guard not installed: orphaned characters exist; run the account-integrity audit and remediate first.';
    END IF;

    SELECT COUNT(*),
           COALESCE(SUM(r.DELETE_RULE = 'RESTRICT' AND r.UPDATE_RULE = 'RESTRICT'), 0)
      INTO fk_count, restrict_fk_count
      FROM information_schema.KEY_COLUMN_USAGE k
      JOIN information_schema.REFERENTIAL_CONSTRAINTS r
        ON r.CONSTRAINT_SCHEMA = k.CONSTRAINT_SCHEMA
       AND r.CONSTRAINT_NAME = k.CONSTRAINT_NAME
       AND r.TABLE_NAME = k.TABLE_NAME
     WHERE k.CONSTRAINT_SCHEMA = DATABASE()
       AND k.TABLE_NAME = 'characters'
       AND k.COLUMN_NAME = 'accountid'
       AND k.REFERENCED_TABLE_NAME = 'accounts'
       AND k.REFERENCED_COLUMN_NAME = 'id';

    IF fk_count = 0 THEN
        ALTER TABLE characters
            ADD CONSTRAINT fk_everleaf_characters_account
            FOREIGN KEY (accountid) REFERENCES accounts(id)
            ON DELETE RESTRICT
            ON UPDATE RESTRICT;
    ELSEIF fk_count <> 1 OR restrict_fk_count <> 1 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'EverLeaf account/character guard found an unexpected existing foreign-key rule; review it manually instead of silently replacing it.';
    END IF;
END//
DELIMITER ;

CALL everleaf_install_account_character_guard();
DROP PROCEDURE everleaf_install_account_character_guard;
