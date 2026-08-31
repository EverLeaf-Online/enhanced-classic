-- EverLeaf account-wide NX reward state.
-- NX Credit (accounts.nxCredit) is the canonical earnable balance.

CREATE TABLE IF NOT EXISTS everleaf_nx_rewards (
    account_id INT NOT NULL,
    last_daily_utc DATE NULL,
    daily_streak INT NOT NULL DEFAULT 0,
    playtime_date_utc DATE NOT NULL,
    playtime_seconds INT NOT NULL DEFAULT 0,
    playtime_steps_claimed INT NOT NULL DEFAULT 0,
    PRIMARY KEY (account_id),
    CONSTRAINT fk_everleaf_nx_rewards_account
        FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS everleaf_vote_rewards (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    account_id INT NOT NULL,
    provider VARCHAR(32) NOT NULL,
    external_vote_id VARCHAR(128) NOT NULL,
    nx_amount INT NOT NULL DEFAULT 1500,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    claimed_at TIMESTAMP NULL DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_everleaf_vote_provider_external (provider, external_vote_id),
    KEY idx_everleaf_vote_account_claimed (account_id, claimed_at),
    CONSTRAINT fk_everleaf_vote_rewards_account
        FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
