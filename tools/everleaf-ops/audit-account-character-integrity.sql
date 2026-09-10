-- EverLeaf account/character integrity audit.
-- Read-only. Safe to run before the account-character guard migration.

SELECT COUNT(*) AS orphan_character_count
FROM characters c
LEFT JOIN accounts a ON a.id = c.accountid
WHERE a.id IS NULL;

SELECT c.id AS character_id,
       c.accountid AS missing_account_id,
       c.name,
       c.level,
       c.job,
       c.world
FROM characters c
LEFT JOIN accounts a ON a.id = c.accountid
WHERE a.id IS NULL
ORDER BY c.accountid, c.id;

SELECT COUNT(*) AS orphan_character_inventory_count
FROM inventoryitems i
LEFT JOIN characters c ON c.id = i.characterid
WHERE i.characterid IS NOT NULL
  AND c.id IS NULL;

SELECT COUNT(*) AS orphan_account_inventory_count
FROM inventoryitems i
LEFT JOIN accounts a ON a.id = i.accountid
WHERE i.accountid IS NOT NULL
  AND a.id IS NULL;

SELECT COUNT(*) AS orphan_inventoryequipment_count
FROM inventoryequipment e
LEFT JOIN inventoryitems i USING (inventoryitemid)
WHERE i.inventoryitemid IS NULL;

SELECT r.CONSTRAINT_NAME,
       r.DELETE_RULE,
       r.UPDATE_RULE
FROM information_schema.REFERENTIAL_CONSTRAINTS r
WHERE r.CONSTRAINT_SCHEMA = DATABASE()
  AND r.TABLE_NAME = 'characters'
  AND r.REFERENCED_TABLE_NAME = 'accounts';
