# EverLeaf QA and Automation

EverLeaf uses deterministic, evidence-first QA layers for repository integrity, runtime scenarios, and selected artificial-player gameplay testing. Current QA gaps and priority are authoritative in [`../EVERLEAF_MASTER_CHECKLIST.md`](../EVERLEAF_MASTER_CHECKLIST.md).

## QA layers

### Static and correlation audits

Maintained tooling covers areas such as:

- content/script inventory;
- map/NPC/portal/reactor references;
- quest structure/actions/rewards;
- class/skill consistency;
- progression/economy surfaces;
- trade/storage/shop/merchant transaction risk;
- event-manager and boss/PQ linkage;
- consolidated feature/release invariants.

Static success proves repository consistency, not a complete real-client playthrough.

### Deep QA

`tools/qa/everleaf_deep_qa.py` performs cross-domain correlation such as NPC/map consistency, portal-graph checks, progression correlation, and exploit-surface inventory.

### Runtime QA harness

`tools/qa/everleaf_runtime_qa.py` provides controlled before/after scenario comparison for staging/disposable/local-QA environments.

It supports:

- JSON snapshots;
- exact persistence comparisons;
- numeric conservation checks for economy/transaction scenarios;
- structured PASS/REVIEW/FAIL output;
- argument-array command adapters rather than `shell=True`;
- dry-run validation;
- explicit safety gates.

Runtime actions are permitted only for an approved non-production environment, a QA-prefixed account, explicit `--allow-actions`, and the maintained arming environment variable. Production and normal player accounts must fail closed.

## Common local commands

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

Staging dry run:

```bash
python3 tools/qa/everleaf_runtime_qa.py run --environment staging --account qa_persist01 --adapter tools/qa/runtime-adapter.example.json --scenario disconnect-reconnect --mode persistence --json build/runtime.json
```

## Runtime scenario priorities

Persistence scenarios should compare level/EXP/mesos/AP/SP/inventory/equipment/quests/storage across disconnect, reconnect, channel change, controlled restart, and clean logout/login.

Economy scenarios should use controlled accounts and conservation checks around trade, storage, NPC shops, drop/pickup, disconnect transitions, and concurrent operations. Unexpected positive deltas are suspected duplication; unexpected negative deltas are suspected loss.

## SoloMapling gameplay-agent layer

EverLeaf integrated a pinned SoloMapling-derived server-side artificial-player foundation for QA. The useful current pieces include controlled bot provisioning, movement/travel graph integration, potion restock, combat reachability, projectile supplies, loadout reapply, untargetable-map rerouting, and basic hunt/death/fleet/soak/class behavior testing.

Automatic synthetic-bot persistence is disabled. Further pathfinding/terrain/autonomous-progression work is intentionally parked unless the project returns to it.

The historical integration branch/PR notes and dated disposable-suite result are archived. They are evidence, not present operating instructions.

## AI reviewer boundary

AI may summarize deterministic findings, rank impact, draft issues, and propose fixes. A REVIEW finding is never sufficient authority for an automatic production mutation. Production changes still require normal source review, tests, deployment gates, and explicit production validation.

## CI usage

Heavy QA/build workflows are intentionally manual-only where continuous triggering would waste hosted-runner capacity. Run expensive audits when the changed surface or release decision justifies them; do not infer that a manual workflow is missing simply because it is not running on every push.

Every fixed exploit or critical bug should gain a regression test when practical, and the project should maintain a machine-readable known-issues list as public-beta hardening continues.
