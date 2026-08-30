-- EverLeaf account-bound PQ Points currency and immutable audit ledger.
-- Apply during the next approved production DB migration window.

CREATE TABLE IF NOT EXISTS `everleaf_pq_point_balance` (
  `account_id` INT NOT NULL,
  `balance` INT NOT NULL DEFAULT 0,
  `lifetime_earned` BIGINT NOT NULL DEFAULT 0,
  `lifetime_spent` BIGINT NOT NULL DEFAULT 0,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`account_id`),
  CONSTRAINT `fk_everleaf_pq_points_account`
    FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_everleaf_pq_points_balance` CHECK (`balance` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `everleaf_pq_point_ledger` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `account_id` INT NOT NULL,
  `character_id` INT NULL,
  `amount` INT NOT NULL,
  `balance_after` INT NOT NULL,
  `reason_type` VARCHAR(32) NOT NULL,
  `reason_key` VARCHAR(128) NOT NULL,
  `metadata` VARCHAR(255) NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_everleaf_pq_points_account_created` (`account_id`, `created_at`),
  UNIQUE KEY `uq_everleaf_pq_points_reason` (`account_id`, `reason_type`, `reason_key`),
  CONSTRAINT `fk_everleaf_pq_points_ledger_account`
    FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_everleaf_pq_points_ledger_character`
    FOREIGN KEY (`character_id`) REFERENCES `characters` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_everleaf_pq_points_nonzero` CHECK (`amount` <> 0),
  CONSTRAINT `chk_everleaf_pq_points_balance_after` CHECK (`balance_after` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
