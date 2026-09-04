-- Adjust database name if your EverLeaf schema uses a different DB name.
CREATE USER IF NOT EXISTS 'everleaf_web'@'127.0.0.1' IDENTIFIED BY 'REPLACE_WITH_STRONG_PASSWORD';
GRANT SELECT ON cosmic.accounts TO 'everleaf_web'@'127.0.0.1';
GRANT SELECT ON cosmic.characters TO 'everleaf_web'@'127.0.0.1';
-- Rankings need the saved equipped item IDs/positions to compose the real
-- Character.wz appearance. No equipment stats or write privileges are needed.
GRANT SELECT ON cosmic.inventoryitems TO 'everleaf_web'@'127.0.0.1';
FLUSH PRIVILEGES;

-- Production deployment reapplies the inventoryitems SELECT grant to every
-- existing everleaf_web host entry (for example localhost or 127.0.0.1), so
-- MySQL host resolution cannot silently strip equipped ranking appearances.
--
-- When registration is enabled later, grant only the INSERT/column access
-- required by your actual EverLeaf accounts schema.
