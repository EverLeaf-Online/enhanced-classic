-- Everleaf account-bound Verdant Marks currency and auditable ledger.
-- Apply after everleaf_weekly_progression.sql.

CREATE TABLE IF NOT EXISTS `everleaf_verdant_mark_balance` (
  `account_id` INT NOT NULL,
  `balance` INT NOT NULL DEFAULT 0,
  `lifetime_earned` BIGINT NOT NULL DEFAULT 0,
  `lifetime_spent` BIGINT NOT NULL DEFAULT 0,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`account_id`),
  CONSTRAINT `fk_everleaf_marks_account`
    FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_everleaf_marks_balance` CHECK (`balance` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `everleaf_verdant_mark_ledger` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `account_id` INT NOT NULL,
  `character_id` INT NULL,
  `amount` INT NOT NULL,
  `balance_after` INT NOT NULL,
  `reason_type` VARCHAR(32) NOT NULL,
  `reason_key` VARCHAR(96) NOT NULL,
  `metadata` VARCHAR(255) NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_everleaf_marks_account_created` (`account_id`, `created_at`),
  UNIQUE KEY `uq_everleaf_marks_reason` (`account_id`, `reason_type`, `reason_key`),
  CONSTRAINT `fk_everleaf_marks_ledger_account`
    FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_everleaf_marks_ledger_character`
    FOREIGN KEY (`character_id`) REFERENCES `characters` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_everleaf_marks_nonzero` CHECK (`amount` <> 0),
  CONSTRAINT `chk_everleaf_marks_balance_after` CHECK (`balance_after` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
