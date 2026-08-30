-- EverLeaf rare global-drop balance
--
-- Global drops bypass the world's normal Drop/Boss Drop multiplier. The base
-- data gives both Chaos Scroll 60% and White Scroll a 1,200 / 999,999 roll
-- (~0.12%) from essentially every eligible mob, which is far too generous for
-- long-term Enhanced Classic progression.
--
-- EverLeaf pre-alpha targets:
--   Chaos Scroll 60% (2049100): 100 / 999,999 ~= 0.0100%
--   White Scroll     (2340000):  40 / 999,999 ~= 0.0040%
--
-- At 1,000 kills/hour this averages ~0.10 Chaos Scroll and ~0.04 White Scroll
-- per hour from the global-drop system. Boss/event-specific sources remain
-- separate and can be balanced independently.

USE `cosmic`;

UPDATE `drop_data_global`
SET `chance` = 100,
    `comments` = 'EverLeaf - Chaos Scroll 60% (0.01%)'
WHERE `itemid` = 2049100
  AND `continent` = -1;

UPDATE `drop_data_global`
SET `chance` = 40,
    `comments` = 'EverLeaf - White Scroll (0.004%)'
WHERE `itemid` = 2340000
  AND `continent` = -1;

SELECT `itemid`, `continent`, `chance`, `minimum_quantity`, `maximum_quantity`, `comments`
FROM `drop_data_global`
WHERE `itemid` IN (2049100, 2340000)
ORDER BY `itemid`, `continent`;
