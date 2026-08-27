-- Adjust database name if your EverLeaf schema uses a different DB name.
CREATE USER IF NOT EXISTS 'everleaf_web'@'127.0.0.1' IDENTIFIED BY 'REPLACE_WITH_STRONG_PASSWORD';
GRANT SELECT ON cosmic.accounts TO 'everleaf_web'@'127.0.0.1';
GRANT SELECT ON cosmic.characters TO 'everleaf_web'@'127.0.0.1';
FLUSH PRIVILEGES;

-- When registration is enabled later, grant only the INSERT/column access
-- required by your actual EverLeaf accounts schema.
