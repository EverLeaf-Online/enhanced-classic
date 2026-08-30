#!/usr/bin/env bash
set -euo pipefail

# EverLeaf production/staging backup helper.
# This script is intentionally inert until an operator supplies the protected
# environment file and explicitly runs it on the target host.
environment_file="${EVERLEAF_ENV_FILE:-/etc/everleaf/everleaf.env}"
backup_dir="${EVERLEAF_BACKUP_DIR:-/var/backups/everleaf}"
database="${EVERLEAF_DB_NAME:-cosmic}"

if [[ ! -r "${environment_file}" ]]; then
    echo "Missing readable EverLeaf environment file: ${environment_file}" >&2
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

if [[ "${EVERLEAF_DB_USER}" == "root" ]]; then
    echo "Refusing backup with MySQL root. Configure the dedicated EverLeaf backup/database account." >&2
    exit 1
fi

mysql_base=(
    mysql --protocol=TCP
    --host="${EVERLEAF_DB_HOST}"
    --port="${EVERLEAF_DB_PORT:-3306}"
    --user="${EVERLEAF_DB_USER}"
)

install -d -m 700 "${backup_dir}"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
temporary="${backup_dir}/.${database}-${timestamp}.sql.gz.tmp"
destination="${backup_dir}/${database}-${timestamp}.sql.gz"
verification_database="everleaf_backup_verify_${timestamp//[^0-9A-Za-z]/_}"

cleanup() {
    rm -f -- "${temporary}"
    MYSQL_PWD="${EVERLEAF_DB_PASS}" "${mysql_base[@]}" \
        -e "DROP DATABASE IF EXISTS \`${verification_database}\`;" >/dev/null 2>&1 || true
}
trap cleanup EXIT

MYSQL_PWD="${EVERLEAF_DB_PASS}" mysqldump \
    --protocol=TCP \
    --host="${EVERLEAF_DB_HOST}" \
    --port="${EVERLEAF_DB_PORT:-3306}" \
    --user="${EVERLEAF_DB_USER}" \
    --single-transaction \
    --quick \
    --routines \
    --triggers \
    --events \
    --no-tablespaces \
    --set-gtid-purged=OFF \
    "${database}" \
    | gzip -9 > "${temporary}"

gzip -t "${temporary}"
[[ -s "${temporary}" ]] || { echo "Backup archive is empty" >&2; exit 1; }
chmod 600 "${temporary}"
mv "${temporary}" "${destination}"

MYSQL_PWD="${EVERLEAF_DB_PASS}" "${mysql_base[@]}" \
    -e "CREATE DATABASE \`${verification_database}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
gzip -dc "${destination}" | MYSQL_PWD="${EVERLEAF_DB_PASS}" "${mysql_base[@]}" "${verification_database}"

verification="$(MYSQL_PWD="${EVERLEAF_DB_PASS}" "${mysql_base[@]}" --batch --skip-column-names "${verification_database}" <<'SQL'
SELECT IF(
    (SELECT COUNT(*) FROM information_schema.tables
     WHERE table_schema = DATABASE()
       AND table_name IN ('accounts', 'characters', 'inventoryitems', 'inventoryequipment')) = 4,
    'backup_restore_ok',
    'backup_restore_failed'
);
SQL
)"

if [[ "${verification}" != "backup_restore_ok" ]]; then
    echo "Backup restore verification failed" >&2
    exit 1
fi

MYSQL_PWD="${EVERLEAF_DB_PASS}" "${mysql_base[@]}" \
    -e "DROP DATABASE \`${verification_database}\`;"
trap - EXIT

echo "EverLeaf database backup created and restore-verified: ${destination}"
