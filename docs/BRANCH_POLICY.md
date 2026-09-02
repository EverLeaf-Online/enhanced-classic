# EverLeaf Branch Policy

EverLeaf keeps a deliberately small set of long-lived branches so active development, release integration, and production history remain easy to reason about.

## Long-lived branches

- `master` — integrated production/mainline history. The maintained website/CMS/Discord operations and the consolidated non-Empress release line were reconciled here by PR #247.
- `release-dev` — primary integration branch for server/game/content work before promotion to `master`.
- `client-dev` — maintained client-specific development line.

## Excluded / archive-only branches

- `Community-files` — reference/archive material only; not part of the active release line.
- `empress-dev` — deferred Empress work; excluded from the non-Empress release line.

These branches must not be merged into `master` or `release-dev` unless a future review explicitly reopens their scope.

## Temporary work branches

`consolidation/*`, ordinary feature/fix/ops/CI branches, and other clearly completed task branches are temporary workspaces.

After their pull request is merged or superseded and any successor branch has been verified, the source branch may be retired only when it is outside the protected WZ scope below.

## Protected WZ modernization scope

The updated-WZ modernization effort is intentionally excluded from routine branch cleanup.

Always preserve:

- every `wz/v95-*` branch, whether active, merged, superseded, or currently idle;
- any branch, pull request, workflow, tool, staging branch, donor-analysis branch, parity branch, exporter branch, profiler branch, client/server smoke branch, or related artifact that is known or reasonably suspected to belong to the ongoing **Find Updated WZ Files** work;
- any other WZ branch whose ownership or relationship to that effort is uncertain.

Do not delete, rename, reset, retarget, merge solely for cleanup purposes, or otherwise rewrite protected WZ branches as part of repository organization work.

When uncertain whether a branch is related to the updated-WZ effort, preserve it.

## Current cleanup rule

A non-protected branch is safe to retire only when all of the following are true:

1. Its PR is merged, or the PR is closed as explicitly superseded.
2. Any replacement/successor PR has merged when applicable.
3. No open PR currently uses the branch as its head.
4. The branch does not contain intentionally preserved unconsumed work.
5. The branch is not `wz/v95-*` and is not known or suspected to belong to the Find Updated WZ Files effort.

## Current protected set

Always preserve:

- `master`
- `release-dev`
- `client-dev`
- every `wz/v95-*` branch
- everything associated with the Find Updated WZ Files effort

Preserve as excluded/archive unless deliberately removed later:

- `Community-files`
- `empress-dev`

For any other `wz/*` branch, default to preservation unless its unrelated ownership and safe-retirement status are both established.
