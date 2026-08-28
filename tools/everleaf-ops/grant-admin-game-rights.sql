START TRANSACTION;
UPDATE characters
SET gm=6
WHERE accountid=2 AND BINARY name='Policy'
  AND EXISTS (SELECT 1 FROM accounts WHERE id=2 AND BINARY name='admin');
SELECT ROW_COUNT() AS updated_characters;
COMMIT;
SELECT a.id,a.name,a.webadmin,c.id,c.name,c.gm
FROM accounts a
JOIN characters c ON c.accountid=a.id
WHERE a.id=2 AND BINARY a.name='admin' AND BINARY c.name='Policy';
