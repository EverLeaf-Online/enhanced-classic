# EverLeaf Branch Policy

EverLeaf keeps a deliberately small set of long-lived branches so active development, release integration, and production history remain easy to reason about.

## Long-lived branches

- `master` — stable/default repository mainline and maintained website/CMS/Discord operations history. It is reconciled by behavior, not by force-updating it from another branch.
- `release-dev` — authoritative game-server/content/release integration line and the source used by the production game deployment.
- `client-dev` — maintained client-specific development line while unique client-source work is reconciled.

## Canonical production content

`release-dev` now contains the active Future Henesys / Empress runtime work and the production deployment contract for the canonical full-v95 WZ baseline. Ninja Castle is also consumed through that full-v95 baseline. These are no longer deferred regional imports.

The production WZ source of truth is the validated shared baseline at `/opt/everleaf/shared/wz-v95`, reconstructed from the live managed v95 client and guarded by the production deployment workflow. Selective Empress/Ninja staging branches are not deployment sources.

## Reference / archive material

- `Community-files` — reference/donor material only; not a deployment branch.
- Generic v95 donor/exporter/profiler/tooling branches may be retained when they still provide reusable evidence or maintenance tooling.
- Closed PRs and commit SHAs remain the historical record for completed regional experiments.

## Temporary work branches

Ordinary feature/fix/ops/CI branches and region-specific staging/review branches are temporary workspaces.

After their pull request is merged or superseded and the replacement behavior is verified on the canonical line, the source branch should be retired or collapsed when no open PR uses it.

## WZ cleanup policy

Do **not** prune generic donor/tooling work merely because it has a `wz/` prefix. Preserve reusable pipelines and reference evidence such as donor extraction, exporters, profilers, and cross-version diagnostics.

Region-specific `wz/v95-ninja-*` staging/review/contract branches are different: after the full-v95 baseline is live, verified, and no open PR uses them, they are superseded cleanup candidates. The same rule applies to obsolete Empress-only integration branches after Empress is represented on `release-dev` and verified live.

## Safe-retirement rule

A branch may be retired/collapsed only when all of the following are true:

1. It is not `master`, `release-dev`, `client-dev`, or `Community-files`.
2. No open PR currently uses the branch as its head.
3. Its intended production behavior is merged, patch-equivalent, or explicitly superseded by a stronger canonical implementation.
4. Any required live content has passed production verification after the replacement landed.
5. It is not a generic donor/tooling/reference branch that remains useful for future WZ work.

## Current canonical verification

The September 4, 2026 production verification established:

- exact live game release `b639d7ee796da8c7b305f002ebaaf9320d8ba13a`;
- canonical full-v95 server WZ with **44,236 XML files**;
- Future Henesys / Empress representative assets present;
- Ninja Castle maps, mobs, NPCs, and quests **8163-8171** present;
- 20/20 channels healthy plus login on port 8484;
- signed launcher manifest and managed client patch endpoints healthy.

## Mainline reconciliation rule

Do not force-update `master` from `release-dev` while `master` contains independently maintained web/ops behavior. Reconcile those surfaces semantically, then use a focused promotion when the unique-behavior ledger is exhausted. Production game deployment remains sourced from `release-dev` until that promotion is intentionally completed.
