-- Apply after everleaf_verdant_marks.sql and everleaf_rooted_materials.sql.
-- Payment and this fulfillment record are committed in the same transaction.

ALTER TABLE inventoryequipment
    ADD COLUMN everleaf_forge_stage TINYINT UNSIGNED NOT NULL DEFAULT 0 AFTER ringid;

CREATE TABLE IF NOT EXISTS everleaf_rooted_forge_order (
    id BIGINT NOT NULL AUTO_INCREMENT,
    account_id INT NOT NULL,
    character_id INT NOT NULL,
    recipe VARCHAR(64) NOT NULL,
    request_key VARCHAR(96) NOT NULL,
    status ENUM('PENDING', 'FULFILLED') NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fulfilled_at TIMESTAMP NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_rooted_forge_request (account_id, request_key),
    KEY idx_rooted_forge_pending (status, id),
    CONSTRAINT fk_rooted_forge_account FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    CONSTRAINT fk_rooted_forge_character FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
