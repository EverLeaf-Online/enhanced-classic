SELECT id,name,webadmin,banned,loggedin
FROM accounts
WHERE LOWER(name) IN ('policy','admin');

SELECT id,accountid,name,gm,level,job
FROM characters
WHERE accountid IN (SELECT id FROM accounts WHERE LOWER(name) IN ('policy','admin'))
ORDER BY accountid,id;

SELECT k.TABLE_NAME,k.COLUMN_NAME,r.DELETE_RULE
FROM information_schema.KEY_COLUMN_USAGE k
JOIN information_schema.REFERENTIAL_CONSTRAINTS r
  ON r.CONSTRAINT_SCHEMA=k.CONSTRAINT_SCHEMA AND r.CONSTRAINT_NAME=k.CONSTRAINT_NAME
WHERE k.REFERENCED_TABLE_SCHEMA='cosmic' AND k.REFERENCED_TABLE_NAME='accounts'
ORDER BY k.TABLE_NAME,k.COLUMN_NAME;
