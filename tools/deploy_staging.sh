#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <git-commit-sha>" >&2
    exit 2
fi

commit_sha="$1"
root_dir="/opt/everleaf"
release_dir="${root_dir}/releases/${commit_sha}"
repository="https://github.com/iampolicy/enhanced-classic.git"

mkdir -p "${root_dir}/releases"

if [[ ! -d "${release_dir}/.git" ]]; then
    git clone --filter=blob:none --no-checkout "${repository}" "${release_dir}"
fi

git -C "${release_dir}" fetch --depth=1 origin "${commit_sha}"
git -C "${release_dir}" checkout --detach --force FETCH_HEAD

cd "${release_dir}"
python3 tools/apply_everleaf_config.py
python3 tools/apply_level_cap_250.py
chmod +x mvnw
chmod +x tools/backup_database.sh
./mvnw -B package --file pom.xml

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

sudo systemctl daemon-reload
sudo systemctl enable everleaf.service
sudo install -d -m 700 /var/backups/everleaf
sudo systemctl enable --now everleaf-backup.timer
sudo ufw allow 8484/tcp comment 'Everleaf login'
sudo ufw allow 7575:7577/tcp comment 'Everleaf channels'
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
ss -ltn | grep -E ':(8484|7575|7576|7577)[[:space:]]'
sudo ufw status numbered

if ! sudo systemctl start everleaf-backup.service; then
    sudo journalctl --no-pager -u everleaf-backup.service -n 200
    exit 1
fi
sudo systemctl --no-pager --full status everleaf-backup.timer
sudo find /var/backups/everleaf -maxdepth 1 -type f -name 'cosmic-*.sql.gz' \
    -printf '%TY-%Tm-%TdT%TH:%TM:%TSZ %s bytes %f\n' \
    | sort \
    | tail -n 1
