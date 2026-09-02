# EverLeaf branch consolidation

EverLeaf uses a small set of long-lived canonical branches. Feature branches are temporary workspaces and should be deleted once their behavior is represented on a canonical line.

## Canonical branches

| Branch | Purpose |
| --- | --- |
| `master` | Stable/default branch and maintained website/CMS/Wiki implementation. |
| `release-dev` | Current non-Empress game-server, launcher integration, release QA and production staging line. |
| `client-dev` | Maintained v83 client source, WZ/client tooling and client-specific build work. |
| `content-dev` | Temporary legacy reconciliation source. Do **not** merge wholesale; retire after every useful non-Empress behavior is either represented on `release-dev` or explicitly superseded. |

## Explicit exclusions

- `empress-dev` is excluded from the current release and consolidation target.
- Any Empress-only maps, bosses, quests, assets, scripts or release wiring remain excluded.
- `Community-files` remains excluded by project decision.
- Active `wz/*` branches are protected while the parallel v95/WZ update work is in progress. They are not cleanup candidates until that work is consumed.

## Cleanup completed on 2026-09-01

The repository had **240 remote branches** before consolidation.

Two mechanically safe cleanup tiers have completed:

1. **69 branches deleted because their complete history was already an ancestor of a canonical branch.**
2. **49 additional branches deleted because every unique SHA was patch-equivalent to a canonical branch.**

That removed **118 redundant branches without deleting unique behavior**. The repository then contained **126 branches**, including 26 protected active `wz/*` branches and the canonical/excluded lines above.

All five stale umbrella/superseded pull requests were also closed. There are currently **0 open pull requests** from those legacy integration attempts. Closing them did not delete their source branches unless the branch independently qualified for one of the safe cleanup tiers.

## Why branches are not blindly merged

The old branches have heavily diverged histories. A raw `git compare` can report a feature as missing even when the same behavior was later cherry-picked, squashed, rewritten or replaced by a stronger implementation.

Reconciliation therefore uses four levels of evidence:

1. commit ancestry;
2. patch equivalence (`git cherry`);
3. final file/blob equivalence;
4. semantic/behavior-marker verification against the maintained implementation.

A branch with different history is not automatically missing functionality.

This process already found one genuine regression: the maintained `Ola.java` had lost the restored Ola Ola randomized portal-state logic. That feature was recovered into `release-dev` and the complete required server build subsequently passed.

## Permanent safety gates

### Branch consolidation audit

`.github/workflows/maintenance-branch-consolidation-audit.yml`

This audit inventories non-canonical branches and distinguishes:

- fully contained history;
- patch-equivalent history;
- final tree effects already represented elsewhere;
- runtime/player-facing effects still requiring semantic review;
- Empress/Community exclusions.

### Canonical feature ledger audit

`.github/workflows/audit-consolidated-features.yml`

`tools/audit_consolidated_features.py` verifies known player-facing, security, launcher, website and QoL behaviors directly on their maintained canonical branches rather than depending on old commit SHAs.

The first corrected ledger run passed **23/23 checks** across `release-dev`, `master` and `client-dev`.

## Current verified release surfaces

The maintained lines currently preserve, among other things:

- level-250 progression;
- Free Market shortcut interaction guards;
- storage session/map/NPC binding;
- NPC-shop session/proximity/client-lock validation;
- inventory/equipment packet and job-requirement validation;
- merchant and PlayerShop concurrency/transaction hardening;
- Evan's current supported release scope;
- one-time launcher launch tickets and fail-closed update behavior;
- signed-size bounded launcher downloads;
- hardened GTop100 verified-vote/NX processing;
- schema-neutral full-game MySQL backups;
- CMS/account/rankings/Wiki surfaces and Wiki provenance;
- Rooted encounter/forge content already represented in the current release line;
- Ola Ola randomized portal-state behavior restored during this consolidation.

The normal `run-build.yml` release gate also includes the economy, world, class/skill, item/transaction and quest audits plus Maven compile/test/package. The build after the Ola restoration completed successfully with every required gate green.

## Branch policy going forward

1. New feature/fix branches must target one canonical branch.
2. Do not create permanent umbrella PRs that attempt to merge hundreds of divergent commits.
3. Once a feature lands or is superseded, delete its short-lived branch.
4. Prefer a single feature branch per coherent change instead of chains of `-v2`, `-final`, `-fix`, and deploy-only branches.
5. Operations-only one-shot workflows must be removed after their run succeeds.
6. Never merge `content-dev` wholesale over newer economy/NX/Gachapon policy.
7. Never consume Empress or `Community-files` content into the current release.
8. Do not prune active `wz/*` branches until the WZ modernization work has an explicit canonical landing point.

## Remaining consolidation work

- Semantically classify the remaining non-WZ divergent branches whose patches are not mechanically equivalent.
- Retire old web/client/server branches only after the canonical feature ledger proves their behavior is represented or a deliberate supersession decision is recorded.
- Finish `content-dev` reconciliation and then retire that temporary branch.
- Re-run the branch audit after each cleanup batch.

A clean Git history is secondary to preserving behavior. No branch is deleted merely because its name looks obsolete.
