# EverLeaf infrastructure / persistence / security hardening scope

This pass intentionally excludes Empress content.

## Automated production readiness

The production-readiness workflow now runs after successful game deployments, on a daily schedule, and manually. It verifies runtime services, the 20-channel topology, TLS, backup freshness and checksums, disk/memory guardrails, protected environment-file permissions, MySQL network exposure, SSH password/root-login policy, public endpoints, and live database structural integrity.

## Safe restore drill

The readiness workflow restores the newest compressed production database backup into a temporary schema, validates core tables, runs `mysqlcheck`, compares restored/live table counts, and drops the temporary schema. The live `cosmic` schema is never replaced by the drill.

## Persistence integrity

The production audit rejects orphan character/account relationships, orphan character/account inventory rows, orphan equipment rows, negative mesos, and negative inventory quantities. Existing character-persistence diagnostics remain available for deeper live-save investigation.

## Login abuse protection

The game login server applies bounded per-host/account failed-login tracking. Eight failures inside a one-minute window trigger a one-minute local lockout. Successful authentication clears the entry. Login and password packet strings also have explicit upper bounds before authentication/database work.

## Follow-up live validation

Player-client channel entry, destructive crash simulation, and deliberate credential rotation are not automatically executed because they can interrupt players. The automated checks are designed to cover the safety preconditions and recovery artifacts for those operational drills.
