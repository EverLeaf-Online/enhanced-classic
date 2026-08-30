-- EverLeaf rare global-drop balance
--
-- Global drops bypass the world's normal Drop/Boss Drop multiplier. The base
-- data gives both Chaos Scroll 60% and White Scroll a 1,200 / 999,999 roll
-- (~0.12%) from essentially every eligible mob. That makes two of the most
-- progression-sensitive scrolls farmable from ordinary grinding and weakens
-- boss/event reward identity.
--
-- EverLeaf policy:
--   Chaos Scroll 60% (2049100): no ordinary global-mob drop
--   White Scroll     (2340000): no ordinary global-mob drop
--
-- Boss-, event-, quest-, gachapon-, and other explicitly authored sources are
-- separate from drop_data_global and can be audited/balanced independently.
-- This migration intentionally removes only the universal monster source.

USE `cosmic`;

DELETE FROM `drop_data_global`
WHERE `itemid` = 2049100
  AND `continent` = -1;

DELETE FROM `drop_data_global`
WHERE `itemid` = 2340000
  AND `continent` = -1;

-- Verification: this query should return zero rows after the migration.
SELECT `itemid`, `continent`, `chance`, `minimum_quantity`, `maximum_quantity`, `comments`
FROM `drop_data_global`
WHERE `itemid` IN (2049100, 2340000)
  AND `continent` = -1
ORDER BY `itemid`, `continent`;
