START TRANSACTION;
DELETE FROM accounts WHERE id=1 AND BINARY name='policy';
SELECT ROW_COUNT() AS deleted_accounts;
COMMIT;
SELECT COUNT(*) AS remaining_policy_accounts FROM accounts WHERE LOWER(name)='policy';
SELECT COUNT(*) AS remaining_admin_accounts FROM accounts WHERE LOWER(name)='admin';
