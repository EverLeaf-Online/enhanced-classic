const { db } = require(process.argv[2]);

const row = db.prepare(`SELECT discord_role_status,lifetime_cents,
  CASE WHEN discord_user_id <> '' THEN 1 ELSE 0 END AS linked
  FROM supporter_profiles ORDER BY updated_at DESC LIMIT 1`).get();
if (!row) {
  console.log("profile=missing");
  process.exitCode = 1;
} else {
  console.log("profile=present");
  console.log(`discord_identity=${row.linked ? "linked" : "missing"}`);
  console.log(`role_status=${row.discord_role_status}`);
  console.log(`confirmed_support_cents=${row.lifetime_cents}`);
}
