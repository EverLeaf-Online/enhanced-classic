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

All `consolidation/*`, feature, fix, ops, CI, and `wz/*` branches are temporary workspaces.

After their pull request is merged or superseded and any successor branch has been verified, the source branch should be deleted. Do not keep completed task branches indefinitely.

### WZ modernization exception

An active `wz/*` branch may remain temporarily when it contains unconsumed donor-analysis, profiling, parity, staging, or client/server smoke work that is still feeding an open pull request or an immediately-following review step.

Once that work is merged or superseded, retire the branch.

## Current cleanup rule

A branch is safe to retire when all of the following are true:

1. Its PR is merged, or the PR is closed as explicitly superseded.
2. Any replacement/successor PR has merged when applicable.
3. No open PR currently uses the branch as its head.
4. The branch does not contain intentionally preserved unconsumed work.

## Current protected set

Always preserve:

- `master`
- `release-dev`
- `client-dev`

Preserve as excluded/archive unless deliberately removed later:

- `Community-files`
- `empress-dev`

Preserve active `wz/*` workspaces only while they are actually in use.
