-- Everleaf hybrid weekly progression persistence.
-- Character-scoped objectives + account-scoped valuable reward budget.
-- Safe to rerun after an interrupted release migration.

CREATE TABLE IF NOT EXISTS everleaf_weekly_account_state (
    account_id INT NOT NULL,
    week_start_utc DATE NOT NULL,
    reward_points_claimed INT NOT NULL DEFAULT 0,
    catchup_points_bank INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (account_id, week_start_utc),
    CONSTRAINT fk_everleaf_weekly_account
        FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    CONSTRAINT chk_everleaf_account_reward_points_nonnegative CHECK (reward_points_claimed >= 0),
    CONSTRAINT chk_everleaf_account_catchup_nonnegative CHECK (catchup_points_bank >= 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS everleaf_weekly_character_objective (
    character_id INT NOT NULL,
    week_start_utc DATE NOT NULL,
    objective_id VARCHAR(64) NOT NULL,
    progress_count INT NOT NULL DEFAULT 0,
    completed_at TIMESTAMP NULL DEFAULT NULL,
    claimed_at TIMESTAMP NULL DEFAULT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (character_id, week_start_utc, objective_id),
    CONSTRAINT fk_everleaf_weekly_character
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT chk_everleaf_objective_progress_nonnegative CHECK (progress_count >= 0)
) ENGINE=InnoDB;

SET @idx_exists = (
    SELECT COUNT(*) FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'everleaf_weekly_account_state'
      AND index_name = 'idx_everleaf_weekly_account_week'
);
SET @idx_sql = IF(@idx_exists = 0,
    'CREATE INDEX idx_everleaf_weekly_account_week ON everleaf_weekly_account_state (week_start_utc)',
    'SELECT 1');
PREPARE stmt FROM @idx_sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @idx_exists = (
    SELECT COUNT(*) FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'everleaf_weekly_character_objective'
      AND index_name = 'idx_everleaf_weekly_character_week'
);
SET @idx_sql = IF(@idx_exists = 0,
    'CREATE INDEX idx_everleaf_weekly_character_week ON everleaf_weekly_character_objective (week_start_utc)',
    'SELECT 1');
PREPARE stmt FROM @idx_sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @idx_exists = (
    SELECT COUNT(*) FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'everleaf_weekly_character_objective'
      AND index_name = 'idx_everleaf_weekly_objective_lookup'
);
SET @idx_sql = IF(@idx_exists = 0,
    'CREATE INDEX idx_everleaf_weekly_objective_lookup ON everleaf_weekly_character_objective (objective_id, week_start_utc)',
    'SELECT 1');
PREPARE stmt FROM @idx_sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
