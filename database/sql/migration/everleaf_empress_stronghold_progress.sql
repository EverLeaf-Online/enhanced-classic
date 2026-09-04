-- EverLeaf Gate to the Future / Knight Stronghold character progression.

CREATE TABLE IF NOT EXISTS everleaf_empress_stronghold_progress (
    character_id INT NOT NULL,
    advanced_knight_mask INT NOT NULL DEFAULT 0,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL DEFAULT NULL,
    PRIMARY KEY (character_id),
    CONSTRAINT fk_everleaf_empress_stronghold_character
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    CONSTRAINT chk_everleaf_empress_knight_mask
        CHECK (advanced_knight_mask >= 0 AND advanced_knight_mask <= 31)
) ENGINE=InnoDB;
