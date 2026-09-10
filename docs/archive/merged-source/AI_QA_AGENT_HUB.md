# EverLeaf AI QA Agent Hub

EverLeaf's QA hub is a **structured, evidence-first testing layer** inspired by the useful architectural idea in AugurMS: expose game/server knowledge through narrow purpose-built tools instead of giving an AI unrestricted control.

The implementation is production-safe by default. Static/deep agents do not connect to live MySQL, alter player data, edit WZ content, or autonomously deploy fixes. The runtime harness added in Phase 2 refuses production and real-player accounts.

## What is implemented

### Baseline agents

| Agent | Purpose | Mode |
|---|---|---|
| Inventory | Confirms expected content/script surfaces exist and inventories them | Read-only static |
| Content | Flags near-empty scripts, TODO/FIXME markers, malformed numeric IDs | Read-only static |
| World | Inventories map/portal scripts and warp references | Read-only static |
| Persistence | Confirms persistence schema surfaces and emits restart-test requirements | Read-only static + test plan |
| Progression | Audits EverLeaf enhanced/Rooted/Forge/Zakum code and migrations | Read-only static |
| Economy | Flags suspicious economic values and identifies exploit surfaces | Read-only static + test plan |
| Regression | Tracks test surfaces and safety invariants | Read-only static |

### Deep correlation agents

`tools/qa/everleaf_deep_qa.py` adds repository-wide cross-checks:

- **NPC Correlation** — parses Map.wz NPC spawns, verifies Npc.wz assets, measures same-ID NPC script coverage, and identifies orphan numeric scripts.
- **Portal Graph** — normalizes Maple WZ map IDs, checks target maps/portal names/scripts, self-loops, and advisory reachability.
- **Progression Deep Audit** — searches Java, migrations, and scripts for Rooted, Forge, Zakum, weekly, and Verdant systems.
- **Exploit Surface Audit** — inventories trade/storage/shop/drop code and flags transaction-sensitive mutation surfaces.
- **NPC Spawn Auditor Integration** — CI also runs `scripts/audit_npc_spawns.py` for assets, coordinates, footholds, roam ranges, duplicates, and reviewed legacy exceptions.

### Guarded runtime harness

`tools/qa/everleaf_runtime_qa.py` is now the common runner for persistence and economy scenarios.

It provides:

- before/after JSON snapshots;
- exact persistence comparison;
- numeric asset-conservation comparison for trade/storage/shop scenarios;
- structured PASS/REVIEW/FAIL JSON reports;
- command adapters supplied as JSON arrays (never `shell=True`);
- dry-run validation without executing adapter commands;
- CI-tested safety gates.

Runtime actions are allowed only when **all** of these conditions hold:

1. environment is exactly `staging`, `disposable`, or `local-qa`;
2. account name starts with `qa_` (or an explicitly configured QA prefix);
3. `--allow-actions` is supplied;
4. `EVERLEAF_QA_RUNTIME=I_UNDERSTAND_STAGING_ONLY` is present.

`production` is rejected by code. A normal player account is rejected by code.

An adapter example is in `tools/qa/runtime-adapter.example.json`. It defines snapshot and scenario commands for disconnect/reconnect, staging restart, trade roundtrip, storage roundtrip, and shop buy/sell. The actual staging adapter binaries are intentionally deployment-specific and must point at a disposable/staging server rather than production.

## CI behavior

The `EverLeaf QA Agents` workflow runs when scripts, database migrations, Java code/tests, Map.wz, Npc.wz, or QA tooling change. CI now also runs `tools/qa/test_runtime_qa.py`, which proves the runtime harness refuses production, refuses non-QA accounts, requires an arming token, and detects persistence/conservation failures.

Static/deep reports:

- `qa-report.json`
- `qa-report.md`
- `npc-spawn-audit.json`
- `deep-qa-report.json`

Artifact upload is best-effort so GitHub storage-quota exhaustion does not hide the actual QA result.

## Running locally

```bash
python3 tools/qa/everleaf_qa.py --json build/qa-report.json --markdown build/qa-report.md
python3 scripts/audit_npc_spawns.py --json > build/npc-spawn-audit.json
python3 tools/qa/everleaf_deep_qa.py --json build/deep-qa-report.json
python3 -m unittest tools/qa/test_runtime_qa.py -v
```

Offline persistence comparison:

```bash
python3 tools/qa/everleaf_runtime_qa.py compare --before before.json --after after.json --mode persistence --json build/persistence.json
```

Staging dry run (executes nothing):

```bash
python3 tools/qa/everleaf_runtime_qa.py run --environment staging --account qa_persist01 --adapter tools/qa/runtime-adapter.example.json --scenario disconnect-reconnect --mode persistence --json build/runtime.json
```

A real staging action additionally requires `--allow-actions` and the explicit arming environment variable.

## Runtime scenario plan

### Persistence Bot

Snapshot level, EXP, mesos, AP/SP, inventory, equipment, quests, and storage, then compare across:

- disconnect/reconnect;
- channel change;
- authorized staging service restart;
- clean logout/login.

Unexpected deltas are FAIL.

### Economy/Exploit Bot

Use QA-only clients and conservation snapshots around:

- trade roundtrip;
- storage deposit/withdraw roundtrip;
- shop buy/sell with explicitly expected cost deltas;
- pickup/drop races;
- disconnect during trade/storage;
- concurrent operations.

For neutral roundtrips, controlled item and meso totals must be conserved. Any unplanned positive delta is a suspected dupe; any negative delta is suspected item/meso loss.

### World/NPC runtime phase

The next adapter family will consume deep-QA portal/NPC evidence, prioritize starter towns/job advancement/custom EverLeaf progression, and drive a QA client through selected routes and dialogs.

## AI reviewer layer

Deterministic runners remain the source of evidence. An AI reviewer may group findings, rank impact, identify likely root causes, draft GitHub issues, and propose fixes on a separate branch. A REVIEW finding must never become a production mutation solely because an AI inferred it was wrong.

## Rollout

1. Establish static/deep QA baseline.
2. Classify legacy portal/NPC REVIEW findings.
3. Deploy a disposable/staging QA adapter and dedicated `qa_` accounts.
4. Run persistence reconnect/restart scenarios.
5. Run multi-client trade/storage/shop conservation scenarios.
6. Add world/NPC runtime probes.
7. Add progression runtime tests.
8. Add AI issue drafting/regression triage.
9. Consider narrowly scoped auto-fixes only for repeatedly proven deterministic low-risk failures.
