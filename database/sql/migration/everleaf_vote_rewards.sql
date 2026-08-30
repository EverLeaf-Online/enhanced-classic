-- EverLeaf verified vote reward ledger.
--
-- Vote Points are account-scoped convenience currency. A verified provider
-- callback may reward an account at most once per provider per UTC day. This
-- keeps callback retries idempotent and prevents a web retry from minting
-- duplicate Vote Points.
--
-- Apply only during an approved production DB migration window.

CREATE TABLE IF NOT EXISTS `everleaf_vote_reward_ledger` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `account_id` INT NOT NULL,
  `provider` VARCHAR(32) NOT NULL,
  `vote_date_utc` DATE NOT NULL,
  `source_username` VARCHAR(32) NOT NULL,
  `voter_ip` VARCHAR(45) NULL,
  `vote_points` INT NOT NULL,
  `provider_reason` VARCHAR(255) NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_everleaf_vote_reward_window`
    (`account_id`, `provider`, `vote_date_utc`),
  KEY `idx_everleaf_vote_reward_created` (`created_at`),
  CONSTRAINT `fk_everleaf_vote_reward_account`
    FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_everleaf_vote_reward_points` CHECK (`vote_points` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
