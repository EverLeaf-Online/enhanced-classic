-- EverLeaf corrective migration: move managed Papulatus rare-scroll drops to
-- the final/reward-bearing body (8500002).
--
-- The earlier boss-scroll migration targeted 8500001, but that form revives
-- into 8500002. PapulatusBattle.js records the clear on 8500002, and the
-- canonical Papulatus loot table also belongs to 8500002. Keeping rare scrolls
-- on 8500001 would allow the controlled boss reward to roll on a transitional
-- phase before the encounter is actually cleared.
--
-- Safe to run more than once: both possible Papulatus rows are normalized
-- before the intended final-body rows are inserted.

USE `cosmic`;

DELETE FROM `drop_data`
WHERE `dropperid` IN (8500001, 8500002)
  AND `itemid` IN (2049100, 2340000)
  AND `questid` = 0;

INSERT INTO `drop_data`
    (`dropperid`, `itemid`, `minimum_quantity`, `maximum_quantity`, `questid`, `chance`)
VALUES
    (8500002, 2049100, 1, 1, 0, 10000),
    (8500002, 2340000, 1, 1, 0, 1500);

SELECT `dropperid`, `itemid`, `minimum_quantity`, `maximum_quantity`, `questid`, `chance`
FROM `drop_data`
WHERE `dropperid` IN (8500001, 8500002)
  AND `itemid` IN (2049100, 2340000)
ORDER BY `dropperid`, `itemid`;
