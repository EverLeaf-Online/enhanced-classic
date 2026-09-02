CREATE TABLE IF NOT EXISTS everleaf_rooted_material_balance (
    account_id INT NOT NULL,
    material VARCHAR(32) NOT NULL,
    balance INT NOT NULL DEFAULT 0,
    lifetime_earned BIGINT NOT NULL DEFAULT 0,
    lifetime_spent BIGINT NOT NULL DEFAULT 0,
    PRIMARY KEY (account_id, material),
    CONSTRAINT fk_rooted_material_account
        FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS everleaf_rooted_material_ledger (
    id BIGINT NOT NULL AUTO_INCREMENT,
    account_id INT NOT NULL,
    character_id INT NULL,
    material VARCHAR(32) NOT NULL,
    amount INT NOT NULL,
    balance_after INT NOT NULL,
    reason_key VARCHAR(128) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_rooted_material_reason (account_id, material, reason_key),
    KEY idx_rooted_material_ledger_account (account_id, id),
    CONSTRAINT fk_rooted_material_ledger_account
        FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    CONSTRAINT fk_rooted_material_ledger_character
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
