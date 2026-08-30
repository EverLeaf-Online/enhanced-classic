# EverLeaf branch consolidation

`release-dev` is the integration branch for the current non-Empress release.

## Rules

- `master` remains the stable promotion target.
- `empress-dev` is intentionally excluded until the next major update/restart.
- `Community-files` is intentionally excluded.
- Production deployment, DB migrations, service restarts, and public client-manifest publication remain approval-gated.
- Diverged feature branches are reconciled by subsystem; they are not blindly merged over newer release work.

## Reconciliation status

| Branch | Status | Notes |
| --- | --- | --- |
| `qa-agent-hub` | Integrated | Static/deep QA, guarded runtime harness, staging probe, Docker QA stack, Windows bridge, and release-dev CI are present. |
| `client-dev` | Integrated for release development | Managed client source, launcher, installer, repair/manifest tooling and safe client/launcher CI are present. Production publishing workflow is intentionally not imported into the active release path. |
| `web-cms` | Integrated for release development | CMS, status/rankings/account surfaces, 8-channel defaults, patch-manifest scripts and safe web CI are present. Production deployment remains master/manual only. |
| `enhanced-dev` | Superseded by release-dev baseline | Level 250, survivability, identity, safety diagnostics, rates/config transforms and associated tests already exist in release-dev in equal/newer form. |
| `progression-dev` | Superseded by release-dev progression | Weekly progression and Verdant Marks already exist; release-dev additionally carries newer PQ Points, Vote/Pet Vac entitlements and Maple Leaf economy work. |
| `content-dev` | Partially integrated | Rooted/encounter Java classes, regression tests, migrations, Rooted Zakum event flow and Rooted Forge entry have been brought forward. Remaining content-dev changes are reviewed individually so older NX/Gachapon/economy behavior cannot overwrite current policy. |

## Current release validation

The integration branch has independent CI surfaces for:

- Java 21 server compile/test/package;
- economy/NX, Gachapon/reward, Vote Point, PQ Point, Pet Vac, Maple Leaf, Rooted-content and world-integrity audits;
- EverLeaf QA Agent Hub;
- Windows v83 client build and managed-package invariants;
- Windows launcher build/tests/self-update security invariants;
- Web CMS syntax/config/disposable-database checks.

Branch consolidation is considered complete only after the remaining useful `content-dev` changes are either integrated or explicitly rejected as superseded, and the complete integrated CI set is green on the same release candidate.
