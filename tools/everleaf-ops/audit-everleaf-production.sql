SELECT TABLE_NAME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA='cosmic' AND TABLE_NAME LIKE 'everleaf_%'
ORDER BY TABLE_NAME;

SELECT 'weekly_account_state' AS component,COUNT(*) AS rows_count FROM everleaf_weekly_account_state
UNION ALL SELECT 'weekly_character_objective',COUNT(*) FROM everleaf_weekly_character_objective
UNION ALL SELECT 'verdant_mark_balance',COUNT(*) FROM everleaf_verdant_mark_balance
UNION ALL SELECT 'verdant_mark_ledger',COUNT(*) FROM everleaf_verdant_mark_ledger
UNION ALL SELECT 'encounter_attempt',COUNT(*) FROM everleaf_encounter_attempt
UNION ALL SELECT 'rooted_forge_order',COUNT(*) FROM everleaf_rooted_forge_order;

SELECT COUNT(*) AS invalid_mark_balances
FROM everleaf_verdant_mark_balance
WHERE balance < 0 OR lifetime_earned < 0 OR lifetime_spent < 0;

SELECT COUNT(*) AS invalid_weekly_state
FROM everleaf_weekly_account_state
WHERE reward_points_claimed < 0 OR catchup_points_bank < 0;

SELECT COUNT(*) AS orphan_weekly_characters
FROM everleaf_weekly_character_objective o
LEFT JOIN characters c ON c.id=o.character_id
WHERE c.id IS NULL;

SELECT COUNT(*) AS orphan_mark_accounts
FROM everleaf_verdant_mark_balance b
LEFT JOIN accounts a ON a.id=b.account_id
WHERE a.id IS NULL;
