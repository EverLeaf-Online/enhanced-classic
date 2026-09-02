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
CREATE TABLE accounts (
    id INT NOT NULL PRIMARY KEY,
    name VARCHAR(32) NOT NULL UNIQUE,
    votepoints INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;
CREATE TABLE characters (
    id INT NOT NULL PRIMARY KEY,
    accountid INT NOT NULL,
    CONSTRAINT fk_test_character_account FOREIGN KEY (accountid) REFERENCES accounts(id) ON DELETE CASCADE
) ENGINE=InnoDB;
CREATE TABLE inventoryequipment (
    inventoryitemid BIGINT NOT NULL PRIMARY KEY,
    ringid INT NOT NULL DEFAULT -1
) ENGINE=InnoDB;
INSERT INTO accounts (id, name) VALUES (1, 'Alpha'), (2, 'Beta');
INSERT INTO characters (id, accountid) VALUES (10, 1), (11, 1), (20, 2);
SQL

structural_migrations=(
    database/sql/migration/everleaf_weekly_progression.sql
    database/sql/migration/everleaf_verdant_marks.sql
    database/sql/migration/everleaf_pq_points.sql
    database/sql/migration/everleaf_account_entitlements.sql
    database/sql/migration/everleaf_vote_rewards.sql
    database/sql/migration/everleaf_nx_rewards.sql
    database/sql/migration/everleaf_enhanced_encounters.sql
    database/sql/migration/everleaf_rooted_materials.sql
    database/sql/migration/everleaf_inventoryequipment_forge_stage.sql
    database/sql/migration/everleaf_rooted_forge.sql
)

# Run twice: release migrations must be safe to retry after an interrupted deploy.
for pass in 1 2; do
    echo "Applying EverLeaf structural migrations (pass ${pass})"
    for migration in "${structural_migrations[@]}"; do
        "${mysql_cmd[@]}" "$database" < "$migration"
    done
done

"${mysql_cmd[@]}" "$database" <<'SQL'
INSERT INTO everleaf_verdant_mark_balance (account_id, balance, lifetime_earned, lifetime_spent)
VALUES (1, 20, 20, 0);

INSERT INTO everleaf_pq_point_balance (account_id, balance, lifetime_earned, lifetime_spent)
VALUES (1, 10, 10, 0);
INSERT INTO everleaf_pq_point_ledger
    (account_id, character_id, amount, balance_after, reason_type, reason_key)
VALUES (1, 10, 10, 10, 'PQ_CLEAR', 'ci-clear-1');

INSERT INTO everleaf_account_entitlement
    (account_id, entitlement_key, expires_at, metadata)
VALUES (1, 'PET_VAC', DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 DAY), 'ci');
INSERT INTO everleaf_account_entitlement_ledger
    (account_id, character_id, entitlement_key, action, source_type, source_key, new_expires_at)
VALUES (1, 10, 'PET_VAC', 'EXTEND', 'VOTE_SHOP', 'ci-petvac-1', DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 DAY));

INSERT INTO everleaf_vote_reward_ledger
    (account_id, provider, vote_date_utc, source_username, voter_ip, vote_points, provider_reason)
VALUES (1, 'gtop100', '2026-08-30', 'Alpha', '203.0.113.10', 1, 'ci');

INSERT INTO everleaf_encounter_attempt
    (account_id, character_id, encounter_id, started_at, finished_at, result, weekly_reward_claimed)
VALUES (1, 10, 'rooted_zakum', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'CLEARED', 1);
SET @attempt_id = LAST_INSERT_ID();
INSERT INTO everleaf_encounter_weekly_reward
    (account_id, encounter_id, week_start_utc, attempt_id)
VALUES (1, 'rooted_zakum', '2026-08-24', @attempt_id);

INSERT INTO everleaf_rooted_material_balance
    (account_id, material, balance, lifetime_earned, lifetime_spent)
VALUES (1, 'EMBER_CORE', 2, 2, 0), (1, 'ANCIENT_BARK', 1, 1, 0);
INSERT INTO everleaf_rooted_forge_order
    (account_id, character_id, recipe, target_item_id, target_inventory_type, target_slot, request_key)
VALUES (1, 10, 'ROOTED_ARMOR_REFINEMENT', 1002001, 1, 1, 'ci-forge-1');
SQL

expect_query_value() {
    local label="$1"
    local expected="$2"
    local statement="$3"
    local actual
    actual="$("${mysql_cmd[@]}" "$database" -e "$statement")"
    if [[ "$actual" != "$expected" ]]; then
        echo "ERROR: ${label}: expected ${expected}, got ${actual}" >&2
        exit 1
    fi
    echo "${label} OK: ${actual}"
}

expect_query_value \
    "migration table count" \
    "12" \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name IN ('everleaf_weekly_account_state','everleaf_weekly_character_objective','everleaf_verdant_mark_balance','everleaf_pq_point_balance','everleaf_pq_point_ledger','everleaf_account_entitlement','everleaf_account_entitlement_ledger','everleaf_vote_reward_ledger','everleaf_encounter_attempt','everleaf_encounter_weekly_reward','everleaf_rooted_material_balance','everleaf_rooted_forge_order');"

# information_schema.statistics has one row per indexed column. Count distinct
# table/index identities so the two-column objective lookup index counts once.
expect_query_value \
    "weekly progression secondary indexes" \
    "3" \
    "SELECT COUNT(DISTINCT CONCAT(table_name, ':', index_name)) FROM information_schema.statistics WHERE table_schema = DATABASE() AND ((table_name='everleaf_weekly_account_state' AND index_name='idx_everleaf_weekly_account_week') OR (table_name='everleaf_weekly_character_objective' AND index_name IN ('idx_everleaf_weekly_character_week','idx_everleaf_weekly_objective_lookup')));"

expect_query_value \
    "forge stage column" \
    "1" \
    "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name='inventoryequipment' AND column_name='everleaf_forge_stage';"

expect_duplicate_rejected() {
    local label="$1"
    local statement="$2"
    if "${mysql_cmd[@]}" "$database" -e "$statement" >/dev/null 2>&1; then
        echo "ERROR: duplicate protection failed: ${label}" >&2
        exit 1
    fi
    echo "Duplicate protection OK: ${label}"
}

expect_duplicate_rejected \
    "PQ clear ledger" \
    "INSERT INTO everleaf_pq_point_ledger (account_id, character_id, amount, balance_after, reason_type, reason_key) VALUES (1,10,1,11,'PQ_CLEAR','ci-clear-1');"

expect_duplicate_rejected \
    "Pet Vac entitlement source" \
    "INSERT INTO everleaf_account_entitlement_ledger (account_id, character_id, entitlement_key, action, source_type, source_key) VALUES (1,10,'PET_VAC','EXTEND','VOTE_SHOP','ci-petvac-1');"

expect_duplicate_rejected \
    "one verified vote reward per provider/day/account" \
    "INSERT INTO everleaf_vote_reward_ledger (account_id, provider, vote_date_utc, source_username, vote_points) VALUES (1,'gtop100','2026-08-30','Alpha',1);"

# Weekly boss reward ownership is account-scoped: a second character on the same
# account cannot consume the same encounter/week reward bucket.
"${mysql_cmd[@]}" "$database" -e \
    "INSERT INTO everleaf_encounter_attempt (account_id, character_id, encounter_id, started_at, finished_at, result, weekly_reward_claimed) VALUES (1,11,'rooted_zakum',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,'CLEARED',1);" >/dev/null
second_attempt="$("${mysql_cmd[@]}" "$database" -e 'SELECT MAX(id) FROM everleaf_encounter_attempt WHERE character_id=11;')"
expect_duplicate_rejected \
    "account-scoped weekly encounter reward" \
    "INSERT INTO everleaf_encounter_weekly_reward (account_id, encounter_id, week_start_utc, attempt_id) VALUES (1,'rooted_zakum','2026-08-24',${second_attempt});"

# These schemas independently reference account_id and character_id. The
# service layer additionally verifies that the character belongs to that
# account; keep that ownership check in runtime tests as well.
if "${mysql_cmd[@]}" "$database" -e \
    "INSERT INTO everleaf_pq_point_ledger (account_id, character_id, amount, balance_after, reason_type, reason_key) VALUES (1,20,1,11,'PQ_CLEAR','cross-account-ci');" >/dev/null 2>&1; then
    echo "NOTE: schema FKs do not prove account-character ownership; service-layer ownership validation remains required."
    "${mysql_cmd[@]}" "$database" -e "DELETE FROM everleaf_pq_point_ledger WHERE reason_key='cross-account-ci';" >/dev/null
fi

echo "EverLeaf migration smoke/idempotency test passed."
