# Production hardening, 2026-09-06
All work executed on the production VM or GitHub. OSRS files and service settings were preserved.

- Disk monitor now uses /usr/local/sbin/everleaf-disk-monitor, independent of release contents. Warning at 80% used/20GiB free; critical at 90%/10GiB.
- Verified redundant staging artifacts removed: 12,222,836,276 bytes. Exact paths and retained copies are recorded on the VM in /home/ubuntu/everleaf-staging/resource-cleanup-report.json.
- QA game and database containers stopped, volumes retained. Compose and container limits: 3GiB/1 CPU and 768MiB/0.5 CPU respectively. Start QA only for a scheduled test window; stop it afterward.
- Added 2GiB swap, swappiness 10. Maple service memory high/max 7/8GiB; website 2500MiB/3GiB; Discord 192/384MiB; avatar 384/768MiB. OSRS unchanged.
- Optional VM builds must use sudo /usr/local/sbin/everleaf-bounded-build /absolute/command args. It applies a 1 CPU/1500MiB ceiling and 30 minute timeout. Prefer GitHub builds.
- Website database user receives SELECT only on cosmic.drop_data, cosmic.shopitems and cosmic.shops.
- Removed only the redundant 7575:7582 and 7575:7577 UFW rules; retained 7575:7594, login, SSH, restricted RDP and OSRS access.
- Website stores sessions in data/sessions.sqlite next to the configured CMS DB, with expiry and logout deletion. The first deployment signs out old in-memory sessions once.
- Web forms use per-session CSRF tokens. Signed payment webhooks and launcher APIs retain their independent authentication paths. Player/admin login regenerate session IDs.
- Website binds 127.0.0.1. Discord status reads include body parsing in an 8-second timeout and retry one transient failure; failed API reads no longer falsely report a reachable login port as offline.
- qs upgraded to 6.16.0. dnsmasq-base, libproc2-0 and procps upgraded; no services or kernel reboot required by package manager.
- LAST_DEPLOYED_RELEASE reconciled with the active current symlink. It records the game server, independently of website/client releases.

Validation: 140 website tests, six Discord bot tests, template compilation; production endpoint, CSRF and session persistence checks recorded during deployment.
