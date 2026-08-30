-- EverLeaf NX coupon economy balance
--
-- The v83 base data ships these global drops at 35,000 / 20,000 out of
-- 999,999 (~3.5% and ~2.0%). Because MapleMap rolls drop_data_global
-- independently from the normal world drop multiplier, those values create
-- thousands of NX per hour on ordinary grinding.
--
-- EverLeaf target:
--   4031865 (100 NX): 400 / 999,999 ~= 0.0400%
--   4031866 (250 NX): 100 / 999,999 ~= 0.0100%
-- Expected value: ~65 NX per 1,000 mob kills.

USE `cosmic`;

UPDATE `drop_data_global`
SET `chance` = 400,
    `comments` = 'EverLeaf - 100 NX Coupon (0.04%)'
WHERE `itemid` = 4031865
  AND `continent` = -1;

UPDATE `drop_data_global`
SET `chance` = 100,
    `comments` = 'EverLeaf - 250 NX Coupon (0.01%)'
WHERE `itemid` = 4031866
  AND `continent` = -1;

-- Fail visibly during manual verification if duplicate global rows exist.
SELECT `itemid`, `continent`, `chance`, `minimum_quantity`, `maximum_quantity`, `comments`
FROM `drop_data_global`
WHERE `itemid` IN (4031865, 4031866)
ORDER BY `itemid`, `continent`;
