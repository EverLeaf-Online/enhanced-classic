# EverLeaf AI QA Agent Hub

EverLeaf's QA hub is a **structured, evidence-first testing layer** inspired by the useful architectural idea in AugurMS: expose game/server knowledge through narrow purpose-built tools instead of giving an AI unrestricted control.

The current implementation remains production-safe. It does not connect to live MySQL, alter player data, edit WZ content, or autonomously deploy fixes.

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

`tools/qa/everleaf_deep_qa.py` adds repository-wide cross-checks that are much closer to actual game QA:

- **NPC Correlation** — parses server-side Map.wz NPC spawns, verifies matching Npc.wz assets, measures same-ID NPC script coverage, and identifies scripts not directly represented by current map spawns. Scriptless/orphan NPCs are REVIEW rather than automatic failures because shops, event NPCs, and decorative NPCs can be legitimate.
- **Portal Graph** — parses map portal metadata, verifies numeric target maps, checks referenced portal scripts, checks named target portals, detects explicit self-loops, and builds an advisory reachability graph.
- **Progression Deep Audit** — searches Java, migrations, and scripts for Rooted, Forge, Zakum, weekly, and Verdant progression surfaces and checks migration table overlap/idempotency risk.
- **Exploit Surface Audit** — inventories trade/storage/shop/drop-related Java code and flags mutation-heavy transaction-sensitive files for manual/runtime concurrency testing.
- **Existing NPC Spawn Auditor Integration** — CI now also runs `scripts/audit_npc_spawns.py`, which already validates NPC assets, coordinates, footholds, roaming ranges, duplicate spawn records, and reviewed legacy exceptions.

## CI behavior

The `EverLeaf QA Agents` workflow now runs when scripts, database migrations, Java server code/tests, Map.wz, Npc.wz, or QA tooling change. It produces four artifacts:

- `qa-report.json`
- `qa-report.md`
- `npc-spawn-audit.json`
- `deep-qa-report.json`

Deterministic FAIL findings stop CI. REVIEW findings remain visible evidence for an AI/human tester but do not automatically modify content.

## Running locally

```bash
python3 tools/qa/everleaf_qa.py \
  --json build/qa-report.json \
  --markdown build/qa-report.md
python3 scripts/audit_npc_spawns.py --json > build/npc-spawn-audit.json
python3 tools/qa/everleaf_deep_qa.py --json build/deep-qa-report.json
```

### Status meanings

- **PASS** — a deterministic invariant passed.
- **FAIL** — a deterministic invariant failed and should block the regression gate.
- **REVIEW** — evidence requires runtime validation or human/AI judgment.

## Safety model

The current hub has no code path for:

- changing live drops, shops, NPCs, maps, config, accounts, or characters;
- connecting to production MySQL;
- sending game packets;
- reading `.env` files or credentials;
- restarting production services;
- changing payment/supporter state;
- autonomously applying a proposed fix.

This is intentional. The deterministic agents establish trustworthy evidence before we add controlled runtime capabilities.

## Controlled runtime phase

The next layer will run only against a dedicated QA account and staging/disposable database snapshot unless explicitly authorized otherwise.

### Persistence Bot

1. Snapshot level, EXP, mesos, AP/SP, inventory, equipment, quests, and storage.
2. Perform a controlled state change on a QA-only character.
3. Disconnect/reconnect and compare.
4. Restart the authorized staging game service and compare again.
5. Report exact field/table deltas as PASS/FAIL.

### World Traversal Bot

1. Consume the portal graph produced by deep QA.
2. Prioritize starter areas, towns, job advancement, transport routes, and EverLeaf custom progression maps.
3. Drive a QA client through selected routes.
4. Compare observed destination/map state against static metadata.

### NPC/Quest Bot

1. Start from deterministic NPC spawn findings.
2. Resolve scriptless NPCs against shop/event/decorative classifications.
3. Exercise dialogs and quest prerequisites using a QA character.
4. Flag missing, misplaced, unusable, or progression-blocking NPCs.

### Economy/Exploit Bot

1. Use two or more QA-only clients.
2. Snapshot total controlled items/mesos before each sequence.
3. Exercise trade, storage, shops, drops/pickups, disconnect races, and concurrent actions.
4. Require conservation of controlled assets unless the tested mechanic explicitly creates/destroys them.
5. Never target real player accounts.

### Progression Bot

Exercise Rooted progression, Rooted Forge, Zakum requirements/rewards, weekly state, and Verdant rewards. Record pacing and exact deltas, and flag impossible requirements, loops, duplicated rewards, and anomalous resets.

## AI reviewer layer

Deterministic runners remain the source of evidence. An AI reviewer may consume the JSON reports to:

- group duplicate findings;
- rank severity/player impact;
- identify likely root causes;
- draft GitHub issues;
- propose fixes on a separate branch;
- compare results across commits and identify regressions.

A REVIEW finding must never become a production mutation solely because an AI inferred that it was wrong.

## Rollout

1. Establish baseline static/deep QA on the active branches.
2. Resolve deterministic FAIL findings and classify REVIEW findings.
3. Add staging-only persistence snapshots/restart tests.
4. Add controlled world/NPC runtime probes.
5. Add multi-client economy/dupe probes.
6. Add progression simulation/runtime tests.
7. Add AI issue drafting and regression triage.
8. Consider narrowly scoped auto-fixes only for repeatedly proven deterministic low-risk failures.
