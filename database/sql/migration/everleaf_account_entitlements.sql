-- EverLeaf timed/permanent account entitlements.
-- Initial consumer: Vote Point-funded Pet Vac.
-- Apply during the next approved production DB migration window.

CREATE TABLE IF NOT EXISTS `everleaf_account_entitlement` (
  `account_id` INT NOT NULL,
  `entitlement_key` VARCHAR(48) NOT NULL,
  `expires_at` TIMESTAMP NULL DEFAULT NULL,
  `metadata` VARCHAR(255) NULL,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`account_id`, `entitlement_key`),
  KEY `idx_everleaf_entitlement_expiry` (`entitlement_key`, `expires_at`),
  CONSTRAINT `fk_everleaf_entitlement_account`
    FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `everleaf_account_entitlement_ledger` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `account_id` INT NOT NULL,
  `character_id` INT NULL,
  `entitlement_key` VARCHAR(48) NOT NULL,
  `action` VARCHAR(24) NOT NULL,
  `source_type` VARCHAR(32) NOT NULL,
  `source_key` VARCHAR(128) NOT NULL,
  `old_expires_at` TIMESTAMP NULL DEFAULT NULL,
  `new_expires_at` TIMESTAMP NULL DEFAULT NULL,
  `metadata` VARCHAR(255) NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_everleaf_entitlement_source`
    (`account_id`, `entitlement_key`, `source_type`, `source_key`),
  KEY `idx_everleaf_entitlement_ledger_account_created` (`account_id`, `created_at`),
  CONSTRAINT `fk_everleaf_entitlement_ledger_account`
    FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_everleaf_entitlement_ledger_character`
    FOREIGN KEY (`character_id`) REFERENCES `characters` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
