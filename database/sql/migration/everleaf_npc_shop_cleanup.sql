-- EverLeaf NPC shop cleanup
-- Resolves a duplicate sort position in shop 1338 (NPC 9090000).
-- Safe/idempotent: only moves the intended item when it is still at the old position.

UPDATE shopitems
SET position = 204
WHERE shopid = 1338
  AND itemid = 5041000
  AND position = 200;
