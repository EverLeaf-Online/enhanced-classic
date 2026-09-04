-- EverLeaf rare-scroll drops for ordinary boss encounters.
--
-- Policy:
--   * Chaos Scroll 60% (2049100) and White Scroll (2340000) do NOT drop
--     globally from ordinary monsters.
--   * They remain rare Gachapon rewards and controlled PQ/boss rewards.
--   * Normal boss encounters get tiered direct drop chances so bossing has
--     meaningful economic value outside PQs.
--
-- Chances below are BASE drop_data probabilities out of 1,000,000. EverLeaf's
-- current Boss Drop rate is 2x, so effective live chances are approximately
-- twice these values unless that server rate is changed later.
--
-- Effective targets at current 2x boss-drop rate:
--   Papulatus / Pianus:        Chaos 2.0%, White 0.30%
--   Scarlion / Targa:          Chaos 3.0%, White 0.50%
--   Zakum:                     Chaos 4.0%, White 0.70%
--   Horntail:                  Chaos 6.0%, White 1.50%
--   Empress Cygnus:            Chaos 8.0%, White 2.00%
--   Pink Bean:                 Chaos 10.0%, White 3.00%
--
-- Only final/reward-bearing boss bodies are included; arms, preheads, summons,
-- Chief Knights, Shinsoo, and transitional forms are intentionally excluded to
-- prevent multiple rare-scroll rolls from one clear.

USE `cosmic`;

DROP TEMPORARY TABLE IF EXISTS `everleaf_boss_scroll_targets`;
CREATE TEMPORARY TABLE `everleaf_boss_scroll_targets` (
    `dropperid` INT NOT NULL,
    `boss_name` VARCHAR(64) NOT NULL,
    `chaos_chance` INT NOT NULL,
    `white_chance` INT NOT NULL,
    PRIMARY KEY (`dropperid`)
);

INSERT INTO `everleaf_boss_scroll_targets`
    (`dropperid`, `boss_name`, `chaos_chance`, `white_chance`)
VALUES
    (8500001, 'Papulatus Clock',   10000,  1500),
    (8510000, 'Pianus',            10000,  1500),
    (9420549, 'Furious Scarlion',  15000,  2500),
    (9420544, 'Furious Targa',     15000,  2500),
    (8800002, 'Zakum',             20000,  3500),
    (8810018, 'Horntail',          30000,  7500),
    (8850011, 'Empress Cygnus',    40000, 10000),
    (8820001, 'Pink Bean',         50000, 15000);

-- Idempotently replace EverLeaf-managed Chaos rows for these bosses.
DELETE d
FROM `drop_data` d
JOIN `everleaf_boss_scroll_targets` t ON t.`dropperid` = d.`dropperid`
WHERE d.`itemid` = 2049100
  AND d.`questid` = 0;

INSERT INTO `drop_data`
    (`dropperid`, `itemid`, `minimum_quantity`, `maximum_quantity`, `questid`, `chance`)
SELECT
    t.`dropperid`, 2049100, 1, 1, 0, t.`chaos_chance`
FROM `everleaf_boss_scroll_targets` t;

-- Idempotently replace EverLeaf-managed White Scroll rows for these bosses.
DELETE d
FROM `drop_data` d
JOIN `everleaf_boss_scroll_targets` t ON t.`dropperid` = d.`dropperid`
WHERE d.`itemid` = 2340000
  AND d.`questid` = 0;

INSERT INTO `drop_data`
    (`dropperid`, `itemid`, `minimum_quantity`, `maximum_quantity`, `questid`, `chance`)
SELECT
    t.`dropperid`, 2340000, 1, 1, 0, t.`white_chance`
FROM `everleaf_boss_scroll_targets` t;

-- Manual verification output.
SELECT
    t.`boss_name`, d.`dropperid`, d.`itemid`, d.`chance`,
    d.`minimum_quantity`, d.`maximum_quantity`, d.`questid`
FROM `everleaf_boss_scroll_targets` t
JOIN `drop_data` d ON d.`dropperid` = t.`dropperid`
WHERE d.`itemid` IN (2049100, 2340000)
ORDER BY t.`chaos_chance`, t.`dropperid`, d.`itemid`;

DROP TEMPORARY TABLE `everleaf_boss_scroll_targets`;
