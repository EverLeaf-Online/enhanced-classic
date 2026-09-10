# EverLeaf Change, Patch, Hotfix, and Migration Policy

This document combines EverLeaf's post-launch change cadence, emergency hotfix process, launcher/client manifest version policy, and database migration release policy. These concerns are kept together because a single player-visible change can require coordinated server, client, launcher, WZ, website, and schema changes.

For production release mechanics, use [`PRODUCTION_AND_RELEASE.md`](PRODUCTION_AND_RELEASE.md). For rollback/restore commands, use [`../staff/RECOVERY_AND_RESTORE.md`](../staff/RECOVERY_AND_RESTORE.md).

## Principles

- `master` is the canonical source line.
- Do not patch production by editing `/opt/everleaf/current` or live patch files ad hoc.
- Use the smallest release surface necessary: server-only, website-only, client overlay, launcher, DB migration, or a coordinated release.
- Every production-affecting change needs an explicit rollback/recovery path.
- Client/server protocol or data compatibility must be treated as one release contract when they depend on each other.
- Database migrations are not automatically reversible; backup and compatibility planning happen before application.
- Hosted CI/runners should be used when execution adds evidence, not merely because a documentation/source commit exists.

## Release classes

### Routine patch

Use for normal fixes, QoL improvements, content corrections, balance changes, and nonurgent maintenance.

A routine patch should:

1. land on canonical `master`;
2. pass the relevant static/unit/build checks;
3. include any required migration/client/content changes in the release plan;
4. use the maintained server/client/website publication workflows;
5. receive post-release verification;
6. be recorded in the changelog/release record when player-visible.

Routine patches should be grouped into coherent releases rather than producing one production restart for every tiny source commit.

### Emergency hotfix

Use when production has an active or high-impact defect where waiting for the normal patch window creates materially more risk: duplication/economy corruption, authentication/authorization bypass, widespread login/play failure, data-loss risk, or a release regression affecting many players.

Hotfix sequence:

1. contain the harmful path first if it is still active;
2. preserve evidence/current release identity;
3. make the smallest authoritative fix on `master` or a deliberately reviewed short-lived hotfix branch;
4. add focused regression coverage where practical;
5. run the minimum sufficient build/security checks for the affected surface;
6. take the required production backup;
7. deploy through the maintained release mechanism rather than mutating the active release in place;
8. verify the exact affected path plus normal login/channel health;
9. roll back if the release is unhealthy;
10. perform separate persistent-state remediation if the bug already wrote bad data.

Do not skip backup/rollback planning merely because the change is urgent.

## Suggested cadence

Until public launch and real population data justify a different schedule:

- security/data-corruption hotfixes: as soon as safely validated;
- blocking gameplay/client/launcher regressions: expedited patch;
- ordinary fixes/QoL/content/balance: batch into coherent release windows;
- documentation-only changes: no production game deployment required;
- large client visual/architecture changes: dedicated tested release, not bundled into unrelated server maintenance.

The cadence is intentionally policy-based rather than tied to a fixed weekday. During alpha/beta, evidence and change risk matter more than pretending a mature weekly release train already exists.

## Coordinated change matrix

Before release, identify which surfaces change:

| Surface | Typical release action |
| --- | --- |
| Java server/config | guarded production game deploy |
| DB schema/data contract | reviewed SQL migration + backup + verification |
| managed client overlay | `publish-everleaf-client.yml` |
| WZ/client managed files | managed client publication/manifest regeneration |
| launcher binary | launcher build/publish plus launcher metadata/version |
| website/CMS | website Git-backed deployment/restart path |
| docs only | Git change only; no production game restart |

If multiple surfaces are coupled, define the safe order before deploying.

## Managed client baseline

EverLeaf's patch builder uses a managed-client baseline to constrain what the launcher patch surface may contain.

The manifest builder rejects:

- files outside the approved managed baseline;
- files whose baseline entry is not marked redistributable;
- duplicate case-insensitive paths;
- symbolic links in the patch payload;
- missing managed files;
- empty/invalid files;
- malformed SHA-256 values.

Do not bypass the baseline by manually dropping an extra file into `/opt/everleaf/patches/files`. Add or change managed files through the reviewed package/baseline process so the manifest generator can enforce the distribution contract.

## Patch manifest version policy

`web/scripts/build-patch-manifest.js` generates `manifest.json` with:

- a top-level patch `version`;
- every managed file path/URL/SHA-256/size;
- optional launcher version/URL/SHA-256/size when both launcher binary and launcher-version metadata are present.

The production client publication workflow currently passes the exact Git commit SHA as the manifest version. That is the preferred production policy because it gives every published managed-client state a direct source identity.

Therefore:

- production managed-client manifest version = exact source Git SHA that produced the overlay;
- do not reuse a prior manifest version for different file hashes;
- do not invent `v2-final-final` style patch identifiers;
- regenerate the manifest after any managed file/baseline change;
- publish the manifest atomically only after the payload is installed and validated;
- keep the previous manifest/payload backup until the new publication verifies.

The builder's timestamp fallback is useful for local/manual tooling but should not replace source SHA identity in the maintained production workflow.

## Client overlay publication

The maintained workflow builds the source-pinned Win32 client integration and packages only the approved managed overlay. The current production publish path:

1. checks out `master`;
2. applies current client transforms;
3. builds the Win32 release;
4. validates compiled branding/runtime invariants;
5. builds the managed overlay;
6. runs patch/client invariants;
7. stages the overlay on the Oracle origin;
8. saves the previous manifest/baseline/managed files as rollback material;
9. installs payload files using `.new` then atomic move;
10. regenerates a manifest using the source SHA;
11. verifies local endpoints and managed-file hashes;
12. automatically restores prior files/manifest on publish failure;
13. verifies the public patch endpoints.

Do not replace this with manual copy-over publication for normal releases.

## Launcher version policy

Launcher version metadata is distinct from the managed-client manifest source SHA.

When launcher release files are present, the manifest generator requires both:

- `EverLeafLauncher-portable.zip`;
- `EverLeafLauncher-version.txt`.

The launcher version string is constrained to a short safe identifier composed of letters, numbers, `.`, `_`, `+`, and `-`.

Policy:

- increment/change launcher version only when the launcher application itself changes;
- a managed WZ/native/config overlay update does not need a fake launcher version bump if the launcher binary is unchanged;
- never publish new launcher binary bytes under an unchanged launcher version;
- preserve SHA-256/size metadata so the client can verify the release artifact;
- test launcher self-update/update detection before treating a new launcher version as public-ready.

## Server/client compatibility changes

If a change alters protocol behavior, packet structure, native bootstrap expectations, required WZ content, or login/launcher ticket behavior:

1. state whether old clients remain compatible;
2. state whether the server can safely accept both versions during rollout;
3. if not, coordinate client publication and server deployment to avoid a mixed incompatible window;
4. verify clean managed-client login → world → character → game after rollout;
5. keep rollback artifacts for both affected sides where practical.

## Database migration release policy

Migration files live under `database/sql/migration/`. The current migration framework is manual; the inherited README explicitly warns that migration scripts are generally intended to run once and should be applied in required order.

A migration becomes part of a production release only after its dependency and rollback/recovery behavior are understood.

### Migration requirements

Every new production migration should document or make obvious:

- purpose/feature;
- required preceding migration(s), if any;
- whether it is safe to rerun/idempotent;
- expected tables/columns/indexes/constraints affected;
- whether application code can run safely before the migration;
- whether the old application release can run safely after the migration;
- verification queries/checks;
- rollback or forward-fix strategy.

Do not assume every historical migration is idempotent.

### Pre-migration sequence

1. Review the exact SQL from canonical `master`.
2. Test against a disposable/representative database when practical.
3. Confirm dependency order.
4. Confirm application compatibility during the transition.
5. Take a fresh production backup immediately before application.
6. Record the current release/source SHA and schema state relevant to the migration.

### Apply

Use an approved administrative connection (for example the configured DBeaver/tunneled path) and apply only the intended migration(s).

For multiple required migrations, apply them in their documented dependency order rather than filesystem/name guesswork alone.

### Post-migration verification

Verify:

- expected tables/columns exist;
- indexes/uniqueness/constraints match the intended schema;
- no partial migration state remains;
- the affected server subsystem starts/operates correctly;
- representative reads/writes succeed;
- no new startup/SQL errors appear.

Then record the migration(s) applied and result.

## Migration failure

If a migration fails partway:

- stop and inspect actual schema/data state;
- do not blindly rerun unless the SQL is proven idempotent from that partial state;
- do not continue deploying application code that requires missing schema;
- use transaction rollback if the migration was safely transactional and remains open;
- otherwise choose a reviewed forward-fix or database restore/targeted repair based on impact;
- preserve the failed state/evidence before broad cleanup when useful.

## Application rollback after migration

A server release rollback does not undo a DB migration. Before applying a migration, determine whether the previous application release remains compatible with the new schema.

If rollback compatibility is not guaranteed, the release plan must include an explicit database recovery/forward-fix strategy. Do not discover this only after the new server fails health checks.

## Patch rollback

For managed-client publication, the maintained workflow already saves the previous manifest, baseline, and managed files and installs the old set if publish verification errors.

For an issue discovered after publication:

1. identify the last known-good source SHA/manifest;
2. restore/rebuild the matching managed payload as a set rather than mixing individual files from unrelated versions;
3. regenerate/publish a manifest whose hashes match the restored files;
4. verify local and public endpoints;
5. test launcher repair/update behavior from a client containing the bad version.

## Change record

For every production-affecting release, preserve enough information to answer:

- What source SHA changed?
- Which server/client/launcher/WZ/web/DB surfaces changed?
- Which migration(s), if any, ran?
- Which manifest/launcher version was published?
- What backup preceded the change?
- What validation passed?
- What is the rollback target?

## Post-launch review

After public population exists, revisit cadence using real operational data: release failure rate, hotfix frequency, player concurrency windows, launcher adoption/update success, schema-change frequency, and balance-content needs. Change the cadence deliberately rather than accumulating ad hoc production pushes.