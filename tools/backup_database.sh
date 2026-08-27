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

echo "Everleaf database backup created: ${destination}"
