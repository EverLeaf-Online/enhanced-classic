#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <git-commit-sha> <source-archive>" >&2
    exit 2
fi

commit_sha="$1"
source_archive="$2"
root_dir="/opt/everleaf"
release_dir="${root_dir}/releases/${commit_sha}"
persistent_config="/etc/everleaf/config.yaml"

mkdir -p "${root_dir}/releases"

if [[ ! "${commit_sha}" =~ ^[0-9a-f]{40}$ ]]; then
    echo "Invalid commit SHA: ${commit_sha}" >&2
    exit 2
fi
if [[ ! -f "${source_archive}" ]]; then
    echo "Missing deployment source archive: ${source_archive}" >&2
    exit 2
fi
if tar -tzf "${source_archive}" | awk '
    /^\// { unsafe = 1 }
    /(^|\/)\.\.(\/|$)/ { unsafe = 1 }
    END { exit(unsafe ? 0 : 1) }
'; then
    echo "Deployment source archive contains an unsafe path." >&2
    exit 2
fi

if [[ -e "${release_dir}" && ! -f "${release_dir}/.everleaf-source-sha" ]]; then
    echo "Existing release directory has no trusted source marker: ${release_dir}" >&2
    exit 1
fi

if [[ ! -f "${release_dir}/.everleaf-source-sha" ]]; then
    incoming_dir="$(mktemp -d "${root_dir}/releases/.incoming-${commit_sha}.XXXXXX")"
    cleanup_incoming() {
        rm -rf -- "${incoming_dir}"
    }
    trap cleanup_incoming EXIT

    tar -xzf "${source_archive}" -C "${incoming_dir}"
    printf '%s\n' "${commit_sha}" > "${incoming_dir}/.everleaf-source-sha"
    mv "${incoming_dir}" "${release_dir}"
    trap - EXIT
elif [[ "$(cat "${release_dir}/.everleaf-source-sha")" != "${commit_sha}" ]]; then
    echo "Existing release source marker does not match ${commit_sha}." >&2
    exit 1
fi

cd "${release_dir}"
python3 tools/apply_everleaf_config.py
python3 tools/apply_level_cap_250.py
if sudo test -f "${persistent_config}"; then
    sudo python3 tools/enable_instant_travel.py "${persistent_config}"
    sudo install -o "$(id -un)" -g "$(id -gn)" -m 600 \
        "${persistent_config}" "${release_dir}/config.yaml"
fi
chmod +x mvnw
chmod +x tools/backup_database.sh
chmod +x tools/check_disk_usage.sh
./mvnw -B package --file pom.xml

sudo tee /usr/local/sbin/everleaf-create-account >/dev/null <<'ACCOUNT_TOOL'
#!/usr/bin/env bash
set -euo pipefail

if [[ ! -t 0 || ! -t 1 ]]; then
    echo "Run this command from an interactive SSH terminal." >&2
    exit 2
fi

set -a
source /etc/everleaf/everleaf.env
set +a

exec /usr/bin/java -cp \
    /opt/everleaf/current/target/everleaf-server-1.0-SNAPSHOT.jar \
    tools.EverleafAccountProvisioner
ACCOUNT_TOOL
sudo chmod 755 /usr/local/sbin/everleaf-create-account

ln -sfn "${release_dir}" "${root_dir}/current"

sudo tee /etc/systemd/system/everleaf.service >/dev/null <<'UNIT'
[Unit]
Description=Everleaf Enhanced Classic v83 staging server
After=network-online.target mysql.service
Wants=network-online.target
Requires=mysql.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/everleaf/current
EnvironmentFile=/etc/everleaf/everleaf.env
ExecStart=/usr/bin/java -Xms1g -Xmx6g -jar /opt/everleaf/current/target/everleaf-server-1.0-SNAPSHOT.jar
Restart=on-failure
RestartSec=10
TimeoutStopSec=45
SuccessExitStatus=143
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true
ReadWritePaths=/opt/everleaf

[Install]
WantedBy=multi-user.target
UNIT

if ! sudo test -f /etc/systemd/system/everleaf-backup.service; then
sudo tee /etc/systemd/system/everleaf-backup.service >/dev/null <<'UNIT'
[Unit]
Description=Back up the Everleaf MySQL database
After=mysql.service
Requires=mysql.service

[Service]
Type=oneshot
User=root
Group=root
ExecStart=/opt/everleaf/current/tools/backup_database.sh
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true
ReadWritePaths=/var/backups/everleaf
UNIT
fi

if ! sudo test -f /etc/systemd/system/everleaf-backup.timer; then
sudo tee /etc/systemd/system/everleaf-backup.timer >/dev/null <<'UNIT'
[Unit]
Description=Daily Everleaf MySQL backup

[Timer]
OnCalendar=*-*-* 08:00:00 UTC
Persistent=true
RandomizedDelaySec=10m
Unit=everleaf-backup.service

[Install]
WantedBy=timers.target
UNIT
fi

sudo tee /etc/systemd/system/everleaf-disk-monitor.service >/dev/null <<'UNIT'
[Unit]
Description=Check Everleaf staging disk usage

[Service]
Type=oneshot
User=root
Group=root
ExecStart=/opt/everleaf/current/tools/check_disk_usage.sh
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
UNIT

sudo tee /etc/systemd/system/everleaf-disk-monitor.timer >/dev/null <<'UNIT'
[Unit]
Description=Hourly Everleaf staging disk-usage monitor

[Timer]
OnBootSec=5m
OnUnitActiveSec=1h
Persistent=true
RandomizedDelaySec=5m
Unit=everleaf-disk-monitor.service

[Install]
WantedBy=timers.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable everleaf.service
sudo install -d -m 700 /var/backups/everleaf
sudo systemctl enable --now everleaf-backup.timer
sudo systemctl enable --now everleaf-disk-monitor.timer
sudo ufw allow 8484/tcp comment 'Everleaf login'
sudo ufw allow 7575:7582/tcp comment 'Everleaf channels'
sudo systemctl restart everleaf.service

for attempt in {1..30}; do
    if ! sudo systemctl is-active --quiet everleaf.service; then
        sudo journalctl --no-pager -u everleaf.service -n 200
        exit 1
    fi
    if ss -ltn | awk '{print $4}' | grep -Eq '(^|:)8484$'; then
        break
    fi
    if [[ "${attempt}" -eq 30 ]]; then
        echo "Everleaf did not open login port 8484 within 60 seconds." >&2
        sudo journalctl --no-pager -u everleaf.service -n 200
        exit 1
    fi
    sleep 2
done

sudo systemctl --no-pager --full status everleaf.service
for port in 8484 {7575..7582}; do
    if ! ss -ltn | awk '{print $4}' | grep -Eq "(^|:)${port}$"; then
        echo "Everleaf did not open required port ${port}." >&2
        exit 1
    fi
done
sudo ufw status numbered

if ! sudo systemctl start everleaf-backup.service; then
    sudo journalctl --no-pager -u everleaf-backup.service -n 200
    exit 1
fi
sudo systemctl --no-pager --full status everleaf-backup.timer
sudo systemctl start everleaf-disk-monitor.service
sudo systemctl --no-pager --full status everleaf-disk-monitor.timer
sudo find /var/backups/everleaf -maxdepth 1 -type f -name 'cosmic-*.sql.gz' \
    -printf '%TY-%Tm-%TdT%TH:%TM:%TSZ %s bytes %f\n' \
    | sort \
    | tail -n 1
