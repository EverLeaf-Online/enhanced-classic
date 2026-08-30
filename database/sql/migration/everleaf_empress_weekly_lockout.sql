-- EverLeaf Empress weekly account clear lockout.
-- Uses the same Monday 00:00 UTC week boundary as WeeklyWindow.

CREATE TABLE IF NOT EXISTS everleaf_empress_weekly_clear (
    account_id INT NOT NULL,
    week_start_utc DATE NOT NULL,
    cleared_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (account_id, week_start_utc),
    CONSTRAINT fk_everleaf_empress_weekly_account
        FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_everleaf_empress_week_start
    ON everleaf_empress_weekly_clear (week_start_utc);
