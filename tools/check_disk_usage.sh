#!/usr/bin/env bash
set -euo pipefail

warning_percent="${EVERLEAF_DISK_WARNING_PERCENT:-80}"
critical_percent="${EVERLEAF_DISK_CRITICAL_PERCENT:-90}"
paths=(/opt/everleaf /var/backups/everleaf)

if ! [[ "${warning_percent}" =~ ^[0-9]+$ && "${critical_percent}" =~ ^[0-9]+$ ]] \
    || (( warning_percent < 1 || critical_percent > 100 || warning_percent >= critical_percent )); then
    echo "Invalid Everleaf disk thresholds: warning=${warning_percent}, critical=${critical_percent}" >&2
    exit 2
fi

declare -A checked_devices=()
critical=0

for path in "${paths[@]}"; do
    [[ -e "${path}" ]] || continue
    read -r filesystem blocks used available capacity mountpoint < <(df -P "${path}" | awk 'NR == 2')
    used_percent="${capacity%%%}"
    [[ -n "${checked_devices[${filesystem}]:-}" ]] && continue
    checked_devices["${filesystem}"]=1

    message="Everleaf disk ${filesystem} mounted at ${mountpoint}: ${used_percent}% used, ${available} KiB available"
    if (( used_percent >= critical_percent )); then
        logger -p daemon.crit -t everleaf-disk-monitor "CRITICAL: ${message}"
        echo "CRITICAL: ${message}" >&2
        critical=1
    elif (( used_percent >= warning_percent )); then
        logger -p daemon.warning -t everleaf-disk-monitor "WARNING: ${message}"
        echo "WARNING: ${message}"
    else
        echo "OK: ${message}"
    fi
done

exit "${critical}"
