# EverLeaf Player Installation and Support

This is the maintained player-facing installation/support baseline. It intentionally avoids staff-only production details.

## Supported installation path

1. Use the official EverLeaf website at `https://everleafms.online` and its Downloads surface.
2. Install/use the EverLeaf Launcher and let it obtain or repair the managed client files.
3. Allow the launcher to finish file validation/update before pressing Play.
4. Launch the game through the launcher for normal play.

EverLeaf is intentionally **launcher-only**. The launcher-managed path keeps the executable, WZ files, and native client components on the expected release and performs the required launch handoff before the game starts.

## Raw EXE launches are blocked

Do not launch `EverLeaf.exe` directly. The managed EverLeaf native bootstrap requires the launcher's one-time handoff and exits when that handoff is missing or invalid.

If Windows shortcuts or old files point directly to the game executable, remove those shortcuts and launch `EverLeafLauncher.exe` instead. Do not attempt to create/copy launcher-ticket files or bypass the launcher checks.

## One client at a time

EverLeaf policy is **one game client per machine at a time**. Multi-client play on the same machine is not allowed.

Canonical source now contains stronger launcher and native-client enforcement for this policy, including an existing-process check, a machine-wide client guard, and race-safe single-use launch handoff. That hardened build is pending managed-client publication/runtime verification; until it is published, do not treat any ability of an older launcher build to start another client as permission to multi-client.

When the hardened build is published, the expected behavior is that a second launch is refused while EverLeaf is already running. Close the existing client normally before launching again.

Do not use renamed/copy folders or multiple launcher windows to attempt to run additional clients.

## Antivirus / security software

Do **not** disable antivirus globally and do not add broad system-wide exclusions just to run EverLeaf.

Older MapleStory executables plus native proxy/bootstrap DLLs can trigger heuristic false positives even when the distributed files are expected. If security software flags a file:

- stop and record the exact filename/detection name;
- verify that the client came from the official EverLeaf launcher/download path;
- use the launcher's repair/hash validation when available;
- submit the detection details to EverLeaf support for review;
- prefer a narrow file-specific decision only after provenance/hash verification rather than disabling protection for the whole machine.

Never install an EverLeaf executable/DLL received from another player or an unofficial mirror simply because its filename looks correct.

## Update/repair problems

For launcher/update failures, record:

- what action failed (install, update, repair, Play);
- exact error text;
- affected filename if shown;
- whether the failure repeats after reopening the launcher;
- whether security software quarantined a file;
- Windows version and basic environment details.

Do not repeatedly copy random DLLs from older clients into the folder. EverLeaf's managed-client files are versioned as a set and mismatched native/WZ files can create crashes or client/server parity failures.

## Crash/freeze reports

The native client can produce local diagnostics beside the game executable, including `EverLeafClient.log`, `EverLeafCrash.dmp`, and `EverLeafFreeze.txt` when applicable. These files are not automatically uploaded.

When reporting a crash, include the log/error and the steps that triggered it. Treat dump files as potentially sensitive debugging artifacts and only submit them intentionally through an official support path.

Do not post passwords, PIC/PIN values, session/launcher tokens, or private account credentials in bug reports.

## Accounts and recovery

Website registration is the authoritative account-creation path under the current production policy.

The current account-recovery path is documented in [`ACCOUNT_RECOVERY.md`](ACCOUNT_RECOVERY.md). Recovery requests are submitted through the official `/recover` page and enter a staff-reviewed queue; the current system is not an automated password-reset-email flow.

Do not attempt database/account workarounds or send passwords/PIC/PIN/session tokens to staff.

## Progression/content help

For rates, level 200–250 progression, Verdant Marks, PQ Points, survivability/no-HP-washing policy, bosses/PQs, and major custom content, see [`PROGRESSION_AND_CONTENT.md`](PROGRESSION_AND_CONTENT.md).

## Gameplay bug reports

A useful gameplay report includes:

- character job and approximate level;
- map/NPC/boss/PQ involved;
- exact action that caused the issue;
- expected behavior vs actual behavior;
- whether relog/channel change reproduced it;
- screenshot/video when relevant;
- timestamp/time zone when a server-side log correlation may be needed.

For suspected duplication, economy abuse, account compromise, unauthorized launcher bypass, or another exploitable security bug, avoid publishing reproduction steps publicly; send the evidence through a staff/support channel.

## Known issues / validation areas

See [`../KNOWN_ISSUES.md`](../KNOWN_ISSUES.md) for the maintained known-defect and validation-risk register.

EverLeaf is closed-alpha capable but still has public-beta validation work around full boss/PQ runs, transaction/concurrency race conditions, complete class/combat parity, clean-machine launcher/client behavior, heavier load testing, and final website/account hardening. The master development checklist remains authoritative for the complete readiness roadmap.
