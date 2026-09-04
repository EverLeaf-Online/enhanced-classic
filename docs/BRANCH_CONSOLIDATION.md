# EverLeaf branch consolidation

EverLeaf uses a small set of long-lived canonical branches. Feature, staging, review, and deploy-only branches are temporary and should be retired after their behavior is represented and verified on a canonical line.

## Canonical branches

| Branch | Purpose |
| --- | --- |
| `master` | Stable/default branch and maintained website/CMS/Discord operations history. |
| `release-dev` | Authoritative game-server/content/release integration line and production game deployment source. |
| `client-dev` | Maintained client-specific development line while unique client work is reconciled. |

`Community-files` remains reference/donor material rather than a production branch.

## Canonical v95 content landing — September 4, 2026

The previous model treated Future Henesys / Empress and Ninja Castle as separate regional work. That model is now superseded.

Production now uses a validated full-v95 server XML baseline at `/opt/everleaf/shared/wz-v95`, reconstructed from the live managed client and preserved across normal game deployments. The production verifier confirms:

- **44,236** canonical server XML files;
- Future Henesys / Empress representative maps and mobs;
- Ninja Castle maps, mobs and NPCs;
- Ninja quests **8163-8171**;
- 20/20 channels plus login;
- signed launcher manifest and public managed patch endpoints.

The exact game release verified live for this landing is `b639d7ee796da8c7b305f002ebaaf9320d8ba13a`.

Consequences:

1. `release-dev` is the canonical active line for Empress runtime behavior and full-v95 game content.
2. `empress-dev`, `content/empress-2026`, and `integrate/empress-runtime-20260904` are no longer production sources once their intended behavior is represented on `release-dev`.
3. Region-specific `wz/v95-ninja-*` staging/review/contract branches are superseded by the full-v95 baseline once no open PR uses them.
4. Generic v95 donor/exporter/profiler/tool branches remain valuable and are **not** blanket cleanup targets.
5. The old selective Ninja live normalization/publish one-shot workflows were retired after the canonical client and server baselines were verified.

## Historical cleanup

On September 1, 2026, repository consolidation removed 118 redundant branches using ancestry and patch-equivalence evidence and removed obsolete one-shot workflows. That cleanup established the rule still used today: history cleanliness is secondary to preserving behavior.

## Evidence hierarchy for cleanup

A stale branch is evaluated using:

1. commit ancestry;
2. patch equivalence;
3. final file/blob equivalence;
4. semantic/behavior verification on the canonical line;
5. production verification when the branch affected live content.

A divergent commit graph alone does not prove missing behavior because EverLeaf frequently squash-merges, rewrites, or replaces experimental implementations.

## Permanent safety gates

The maintained release line includes:

- production-contract validation;
- full server compile/test/package;
- economy, item-transfer, merchant and PlayerShop transaction/concurrency audits;
- class/skill and Evan audits;
- maps/NPCs/portals/world completeness audits;
- quest integrity/completeness audits;
- boss/PQ event-manager link audits;
- live channel/runtime verification;
- live network/character-select diagnostics;
- canonical full-v95 WZ content checks;
- signed launcher/client manifest verification.

## `master` vs `release-dev`

Do not force-update `master` from `release-dev`. `master` has independently maintained web/CMS/Discord operations history, while production game deployment currently sources `release-dev`. Reconcile remaining master-only behavior deliberately, then use a focused promotion when the behavior ledger is exhausted.

## Cleanup rule going forward

A branch is eligible for retirement/collapse when:

- no open PR uses it;
- its intended behavior is represented or explicitly superseded on a canonical branch;
- any required live replacement has been verified;
- it is not a canonical branch or still-useful donor/tool/reference branch.

Avoid chains of `-v2`, `-final`, `-fix`, and deploy-only branches for future work. Prefer one coherent feature branch and remove one-shot operational workflows after successful use.
