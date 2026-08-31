# EverLeaf production secret rotation

Use this procedure for SESSION_SECRET, GAME_DB_PASSWORD, payment-provider credentials, Discord bot credentials, and deployment SSH material.

1. Create the replacement credential in the authoritative provider or password manager. Never commit the value to Git.
2. Back up the current production configuration using the normal EverLeaf backup workflow before changing database or application credentials.
3. Update the protected production secret source first (GitHub Actions secret or root-owned `/etc/everleaf/*.env` file as appropriate).
4. For database-password rotation, create or set the MySQL credential, update `/opt/everleaf/web/.env` and the game-server protected configuration in the same maintenance window, then restart only the affected services.
5. For `SESSION_SECRET`, update `/opt/everleaf/web/.env`, keep mode `0600`, restart `everleaf-web`, and expect existing website sessions to be invalidated.
6. For Discord or payment credentials, update only the service-specific protected environment file and restart that service. Do not copy those values into the game-server tree.
7. For deployment SSH keys, install the new public key on production before replacing `EVERLEAF_SSH_PRIVATE_KEY`; verify a deployment/audit succeeds, then remove the old public key.
8. Run the `Audit EverLeaf production readiness` workflow after every rotation. It verifies protected file permissions, non-default session-secret policy, host exposure, backups, restore viability, database integrity, TLS, and public endpoints.
9. Revoke/delete the old credential only after the audit passes.
10. Record the rotation date and credential type in the staff operations log without recording the secret value.

Emergency compromise order: revoke the exposed credential, block affected access, rotate it, restart the smallest affected service set, run the production-readiness audit, then review logs and active sessions before reopening access.
