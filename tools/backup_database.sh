#!/usr/bin/env bash
set -euo pipefail

environment_file="/etc/everleaf/everleaf.env"
backup_dir="/var/backups/everleaf"

if [[ ! -r "${environment_file}" ]]; then
    echo "Missing readable Everleaf environment file: ${environment_file}" >&2
    exit 1
fi

set -a
# shellcheck disable=SC1090
source "${environment_file}"
set +a

required=(EVERLEAF_DB_HOST EVERLEAF_DB_USER EVERLEAF_DB_PASS)
for variable in "${required[@]}"; do
    if [[ -z "${!variable:-}" ]]; then
        echo "Missing required database setting: ${variable}" >&2
        exit 1
    fi
done

install -d -m 700 "${backup_dir}"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
temporary="${backup_dir}/.cosmic-${timestamp}.sql.gz.tmp"
destination="${backup_dir}/cosmic-${timestamp}.sql.gz"

cleanup() {
    rm -f -- "${temporary}"
}
trap cleanup EXIT

MYSQL_PWD="${EVERLEAF_DB_PASS}" mysqldump \
    --host="${EVERLEAF_DB_HOST}" \
    --user="${EVERLEAF_DB_USER}" \
    --single-transaction \
    --quick \
    --routines \
    --triggers \
    --events \
    --no-tablespaces \
    --set-gtid-purged=OFF \
    cosmic \
    | gzip -9 > "${temporary}"

gzip -t "${temporary}"
chmod 600 "${temporary}"
mv "${temporary}" "${destination}"
trap - EXIT

verification_database="everleaf_backup_verify"
cleanup_verification_database() {
    mysql -e "DROP DATABASE IF EXISTS \`${verification_database}\`;" >/dev/null
}
trap cleanup_verification_database EXIT

mysql -e "DROP DATABASE IF EXISTS \`${verification_database}\`; CREATE DATABASE \`${verification_database}\` CHARACTER SET utf8 COLLATE utf8_general_ci;"
gzip -dc "${destination}" | mysql "${verification_database}"
mysql "${verification_database}" --batch --skip-column-names <<'SQL' | grep -qx 'backup_restore_ok'
SELECT IF(
    (SELECT COUNT(*) FROM information_schema.tables
     WHERE table_schema = DATABASE()
       AND table_name IN ('accounts', 'characters', 'inventoryequipment',
                          'everleaf_weekly_account_state', 'everleaf_rooted_forge_order')) = 5
    AND
    (SELECT COUNT(*) FROM information_schema.columns
     WHERE table_schema = DATABASE()
       AND table_name = 'inventoryequipment'
       AND column_name = 'everleaf_forge_stage') = 1,
    'backup_restore_ok',
    'backup_restore_failed'
);
SQL

cleanup_verification_database
trap - EXIT

echo "Everleaf database backup created and restore-verified: ${destination}"
