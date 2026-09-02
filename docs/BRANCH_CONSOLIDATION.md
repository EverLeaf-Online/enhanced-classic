# EverLeaf branch consolidation

EverLeaf uses a small set of long-lived canonical branches. Feature branches are temporary workspaces and should be deleted once their behavior is represented on a canonical line.

## Canonical branches

| Branch | Purpose |
| --- | --- |
| `master` | Stable/default branch and maintained website/CMS/Wiki implementation. |
| `release-dev` | Current non-Empress game-server, launcher integration, release QA and production staging line. |
| `client-dev` | Maintained v83 client source and remaining client-specific experimental history while unique changes are reconciled. |

## Explicit exclusions

- `empress-dev` is excluded from the current release and consolidation target.
- Any Empress-only maps, bosses, quests, assets, scripts or release wiring remain excluded.
- `Community-files` remains excluded by project decision.
- Active `wz/*` branches are protected while the parallel v95/WZ update work is in progress. They are not cleanup candidates until that work is consumed.

## Cleanup completed on 2026-09-01

The repository had **240 remote branches** before consolidation.

Two mechanically safe cleanup tiers completed earlier:

1. **69 branches deleted because their complete history was already an ancestor of a canonical branch.**
2. **49 additional branches deleted because every unique SHA was patch-equivalent to a canonical branch.**

That removed **118 redundant branches without deleting unique behavior**. The repository then contained **126 branches**, including protected active `wz/*` branches and the canonical/excluded lines above.

All stale umbrella/superseded pull requests were closed. In particular, old client PR #4 is closed as an obsolete umbrella PR rather than as rejected client work.

The former umbrella branches `content-dev`, `progression-dev`, `enhanced-dev`, `qa-agent-hub`, and `web-cms` are no longer present. Their names must not be treated as required canonical branches in future maintenance.

### One-shot workflow cleanup — 2026-09-01 evening

A second repository-hygiene pass removed **17 successful/obsolete one-shot workflows** from `release-dev`:

- `reset-asdf-beginner.yml`
- `reset-asdf-beginner-v2.yml`
- `deploy-evan-v84-maps-production.yml`
- `deploy-evan-v84-maps-production-v2.yml`
- `deploy-evan-v84-maps-production-v3.yml`
- `deploy-evan-v84-maps-production-v4.yml`
- `finalize-evan-v84-maps-production.yml`
- `fix-evan-v84-map-dependencies.yml`
- `rollback-evan-mapwz.yml`
- `trigger-evan-npc-deploy.yml`
- `restore-evan-beginner-quest-skills.yml`
- `evan-recovery-aura-apply.yml`
- `fix-launcher-repair-once.yml`
- `trigger-launcher-repair-publish.yml`
- `everleafosrs-oracle-inventory.yml` (cross-project stray)
- `diagnose-final-quest-scripts.yml`
- `diagnose-quest-script-blockers.yml`

Reusable production deployment/recovery workflows, permanent quest audits, generic runtime/network diagnostics, client/WZ tests, and the active v95/WZ modernization workflows were intentionally retained.

## Why branches are not blindly merged

The old branches have heavily diverged histories. A raw `git compare` can report a feature as missing even when the same behavior was later cherry-picked, squashed, rewritten or replaced by a stronger implementation.

Reconciliation therefore uses four levels of evidence:

1. commit ancestry;
2. patch equivalence (`git cherry`);
3. final file/blob equivalence;
4. semantic/behavior-marker verification against the maintained implementation.

A branch with different history is not automatically missing functionality.

This process previously found one genuine regression: the maintained `Ola.java` had lost the restored Ola Ola randomized portal-state logic. That feature was recovered into `release-dev` and the complete required server build subsequently passed.

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

The corrected ledger has passed its maintained canonical feature checks across `release-dev`, `master` and `client-dev`.

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
- Ola Ola randomized portal-state behavior restored during consolidation.

The normal `run-build.yml` release gate includes economy, world, class/skill, item/transaction and quest audits plus Maven compile/test/package.

## `master` vs `release-dev` reconciliation status

As of the current cleanup pass, the branches are intentionally divergent rather than merge-ready:

- `release-dev` is hundreds of commits ahead of the common base and contains the current integrated non-Empress game/launcher/QA work.
- `master` still has **45 unique commits** relative to `release-dev`.
- Those master-only commits include maintained web/CMS/Discord operations history and therefore must not be discarded by force-updating `master`.
- Several apparent master-only server hardening changes are already represented or superseded on `release-dev`:
  - `MessengerHandler.java` is blob-identical on both branches;
  - `PartyOperationHandler.java` is blob-identical on both branches;
  - `BuddylistModifyHandler.java` is stricter on `release-dev` (invalid-mode rejection and pending-request validation);
  - `MultiChatHandler.java` is stricter on `release-dev` (early type validation and duplicate-recipient rejection).

This is the model for the remaining reconciliation: compare final behavior, not commit counts.

## `client-dev` status

`client-dev` remains highly divergent from `release-dev` and is **not safe to merge wholesale**. Its unique side is dominated by client-source/WZ/Evan-selector experiments and historical one-shot workflows, while the maintained release already contains the production launcher/client distribution surface.

The native Evan selector experiment remains deferred. Client source that is generally useful should be reconciled file-by-file; selector-only experiments should not be allowed to pull obsolete workflow history into the canonical release line.

## Branch policy going forward

1. New feature/fix branches must target one canonical branch.
2. Do not create permanent umbrella PRs that attempt to merge hundreds of divergent commits.
3. Once a feature lands or is superseded, delete its short-lived branch.
4. Prefer a single feature branch per coherent change instead of chains of `-v2`, `-final`, `-fix`, and deploy-only branches.
5. Operations-only one-shot workflows must be removed after their run succeeds.
6. Never merge obsolete donor/economy branches wholesale over newer economy/NX/Gachapon policy.
7. Never consume Empress or `Community-files` content into the current release.
8. Do not prune active `wz/*` branches until the WZ modernization work has an explicit canonical landing point.
9. Do not force-update `master` from `release-dev`; reconcile master-only maintained web/ops behavior first.

## Remaining consolidation work

- Reconcile the 45 master-only commits by behavior, prioritizing web/CMS/Discord/operations files that are genuinely newer on `master`.
- Semantically classify the remaining non-WZ divergent branches whose patches are not mechanically equivalent.
- Reconcile generally useful `client-dev` source/tool changes without importing obsolete Evan-selector/one-shot workflow history.
- Re-run the branch audit after each cleanup batch.
- Once the master-only ledger is exhausted, run the full `release-dev` server build plus web/client/launcher checks and create a focused promotion PR to `master`.

A clean Git history is secondary to preserving behavior. No branch is deleted merely because its name looks obsolete.
