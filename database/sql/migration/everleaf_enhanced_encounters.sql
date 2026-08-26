-- Everleaf enhanced encounter attempt/completion tracking.
-- Weekly reward ownership is account-scoped to match Everleaf's anti-alt-multiplication policy.

CREATE TABLE IF NOT EXISTS `everleaf_encounter_attempt` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `account_id` INT NOT NULL,
  `character_id` INT NOT NULL,
  `encounter_id` VARCHAR(64) NOT NULL,
  `started_at` TIMESTAMP NOT NULL,
  `finished_at` TIMESTAMP NULL,
  `result` VARCHAR(20) NOT NULL DEFAULT 'IN_PROGRESS',
  `weekly_reward_claimed` TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_everleaf_encounter_character_started` (`character_id`, `started_at`),
  KEY `idx_everleaf_encounter_account_encounter` (`account_id`, `encounter_id`, `started_at`),
  CONSTRAINT `fk_everleaf_encounter_account`
    FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_everleaf_encounter_character`
    FOREIGN KEY (`character_id`) REFERENCES `characters` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `everleaf_encounter_weekly_reward` (
  `account_id` INT NOT NULL,
  `encounter_id` VARCHAR(64) NOT NULL,
  `week_start_utc` DATE NOT NULL,
  `attempt_id` BIGINT NOT NULL,
  `claimed_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`account_id`, `encounter_id`, `week_start_utc`),
  UNIQUE KEY `uq_everleaf_weekly_attempt` (`attempt_id`),
  CONSTRAINT `fk_everleaf_encounter_weekly_account`
    FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_everleaf_encounter_weekly_attempt`
    FOREIGN KEY (`attempt_id`) REFERENCES `everleaf_encounter_attempt` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
