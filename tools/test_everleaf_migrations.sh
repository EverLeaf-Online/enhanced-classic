#!/usr/bin/env bash
set -euo pipefail

mysql_host="${EVERLEAF_TEST_MYSQL_HOST:-127.0.0.1}"
mysql_port="${EVERLEAF_TEST_MYSQL_PORT:-3306}"
mysql_user="${EVERLEAF_TEST_MYSQL_USER:-root}"
mysql_password="${EVERLEAF_TEST_MYSQL_PASSWORD:-everleaf_test}"
database="everleaf_migration_test"

mysql_cmd=(mysql --protocol=TCP --host="$mysql_host" --port="$mysql_port" --user="$mysql_user" "--password=$mysql_password" --batch --skip-column-names)

"${mysql_cmd[@]}" <<SQL
DROP DATABASE IF EXISTS ${database};
CREATE DATABASE ${database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ${database};
CREATE TABLE accounts (id INT NOT NULL PRIMARY KEY) ENGINE=InnoDB;
CREATE TABLE characters (id INT NOT NULL PRIMARY KEY, accountid INT NOT NULL) ENGINE=InnoDB;
CREATE TABLE inventoryequipment (inventoryitemid BIGINT NOT NULL PRIMARY KEY, ringid INT NOT NULL DEFAULT -1) ENGINE=InnoDB;
INSERT INTO accounts (id) VALUES (1);
INSERT INTO characters (id, accountid) VALUES (10, 1), (11, 1);
SQL

for migration in \
    database/sql/migration/everleaf_weekly_progression.sql \
    database/sql/migration/everleaf_verdant_marks.sql \
    database/sql/migration/everleaf_enhanced_encounters.sql \
    database/sql/migration/everleaf_rooted_materials.sql \
    database/sql/migration/everleaf_rooted_forge.sql; do
    "${mysql_cmd[@]}" "$database" < "$migration"
done

"${mysql_cmd[@]}" "$database" <<'SQL'
INSERT INTO everleaf_encounter_attempt
    (account_id, character_id, encounter_id, started_at, finished_at, result, weekly_reward_claimed)
VALUES (1, 10, 'rooted_zakum', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'CLEARED', 1);
SET @attempt_id = LAST_INSERT_ID();
INSERT INTO everleaf_encounter_weekly_reward
    (account_id, encounter_id, week_start_utc, attempt_id)
VALUES (1, 'rooted_zakum', '2026-08-24', @attempt_id);

INSERT INTO everleaf_verdant_mark_balance (account_id, balance, lifetime_earned, lifetime_spent)
VALUES (1, 20, 20, 0);
INSERT INTO everleaf_rooted_material_balance (account_id, material, balance, lifetime_earned, lifetime_spent)
VALUES (1, 'EMBER_CORE', 2, 2, 0), (1, 'ANCIENT_BARK', 1, 1, 0);

INSERT INTO everleaf_rooted_forge_order
    (account_id, character_id, recipe, target_item_id, target_inventory_type, target_slot, request_key)
VALUES (1, 10, 'ROOTED_ARMOR_REFINEMENT', 1002001, 1, 1, 'migration-smoke-order');

SELECT IF(COUNT(*) = 5, 'migration_tables_ok', 'migration_tables_missing')
FROM information_schema.tables
WHERE table_schema = DATABASE()
  AND table_name IN ('everleaf_encounter_attempt', 'everleaf_encounter_weekly_reward',
      'everleaf_verdant_mark_balance', 'everleaf_rooted_material_balance', 'everleaf_rooted_forge_order');

SELECT IF(COUNT(*) = 1, 'forge_stage_ok', 'forge_stage_missing')
FROM information_schema.columns
WHERE table_schema = DATABASE() AND table_name = 'inventoryequipment'
  AND column_name = 'everleaf_forge_stage';
SQL

if "${mysql_cmd[@]}" "$database" -e \
    "INSERT INTO everleaf_encounter_weekly_reward (account_id, encounter_id, week_start_utc, attempt_id) VALUES (1, 'rooted_zakum', '2026-08-24', 999);" \
    >/dev/null 2>&1; then
    echo "ERROR: duplicate account-scoped weekly reward was accepted"
    exit 1
fi

echo "Everleaf MySQL migration smoke test passed."
