# Everleaf Closed Alpha

The closed alpha is invite-only. Automatic registration is disabled on staging,
and accounts are created individually by an operator.

## Operator workflow

On the staging VM, run:

```bash
sudo everleaf-create-account
```

The command prompts for the username and password interactively. The password is
hidden, BCrypt-hashed with work factor 12, and never placed in shell history or
passed as a command-line argument. Do not create accounts with direct SQL or send
passwords through GitHub issues, chat logs, or screenshots.

Usernames must contain 4-13 ASCII letters or digits. Passwords must contain
10-72 UTF-8 bytes with at least one letter and one digit.

## Tester checklist

1. Connect with the approved clean v83 client to `132.145.141.79`.
2. Log in with the assigned invite account.
3. Set PIN/PIC when prompted and create one character.
4. Enter each of the three channels and confirm channel changes complete.
5. Confirm basic movement, NPC dialogue, combat, item pickup, inventory, logout,
   and reconnect behavior.
6. Record the time, character name, channel, map, action, and observed result for
   every defect. Never include the account password in a report.

## Known alpha limitations

- There is no public account portal, launcher, or password-reset flow yet.
- Client packaging and compatibility still require clean-machine validation.
- Rooted Zakum timing and balance require live level-200 party playtesting.
- Alpha data may be reset when a migration or economy correction requires it.
- Availability is best-effort while monitoring and abuse controls are completed.
- Disk usage is checked hourly at 80% warning and 90% critical thresholds; log
  files rotate daily or at 20 MB and are compressed without automatic deletion.
- Donations grant no gameplay power, progression currency, boss access, or
  account priority.

## Safety rules

- Never disable antivirus globally. If a clean client binary is flagged, record
  its SHA-256 hash and review the exact detection before making an exception.
- Do not distribute proprietary game files through this server-source repository.
- Do not expose MySQL port 3306 or database credentials to testers.
- Revoke access for shared credentials, chargebacks, abuse, exploits, or leaked
  client/account material while preserving the relevant operational logs.
