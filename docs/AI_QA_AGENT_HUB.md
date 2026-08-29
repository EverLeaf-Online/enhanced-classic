# EverLeaf AI QA Agent Hub

Phase 1 is a **read-only structured QA layer** for EverLeaf. It borrows the useful architectural idea from AugurMS — expose game/server knowledge through narrow, purpose-built tools instead of giving an AI unrestricted access — but it does **not** copy AugurMS or grant autonomous production mutation.

## Goals

- Turn the NPC/map/content checklist into repeatable automated checks.
- Produce machine-readable findings that an AI reviewer can prioritize.
- Catch regressions on every branch/PR.
- Add controlled runtime testers later without letting agents freely alter production data.
- Keep credentials, payment systems, production databases, and player data outside the phase-1 agent surface.

## Phase-1 agents

| Agent | Purpose | Current mode |
|---|---|---|
| Inventory | Confirms expected content/script surfaces exist and inventories them | Read-only static |
| Content | Flags near-empty scripts, TODO/FIXME markers, malformed numeric script IDs | Read-only static |
| World | Inventories portal/map scripts and numeric warp targets; flags obviously malformed targets | Read-only static |
| Persistence | Confirms persistence-related schema surfaces exist; emits required runtime restart tests | Read-only static + test plan |
| Progression | Audits EverLeaf enhanced/Rooted/Forge/Zakum code and migrations | Read-only static |
| Economy | Flags suspicious negative economic values and identifies shop/merchant exploit surface | Read-only static + test plan |
| Regression | Checks test coverage surface and guarantees phase-1 performs no production mutation | Read-only static |

## Running it

```bash
python3 tools/qa/everleaf_qa.py
```

Write reports for an AI/human reviewer:

```bash
python3 tools/qa/everleaf_qa.py \
  --json build/qa-report.json \
  --markdown build/qa-report.md
```

Run one specialist:

```bash
python3 tools/qa/everleaf_qa.py --agent world
```

### Status meanings

- **PASS** — a deterministic invariant passed.
- **FAIL** — a deterministic invariant failed; CI should stop.
- **REVIEW** — static analysis found a question that needs runtime validation or human/AI judgment.

`REVIEW` deliberately does not fail CI. It is the queue for the AI tester/reviewer layer.

## Safety model

Phase 1 intentionally has no code path for:

- changing live drops, shops, NPCs, maps, config, accounts, or characters;
- connecting to production MySQL;
- sending game packets;
- reading `.env` files or credentials;
- issuing shell commands outside its own static repository scan;
- changing payment/supporter state.

This keeps the QA layer useful while we establish trust in its findings.

## Runtime Phase 2

The next layer should use a dedicated **QA-only game account and QA-only DB identity**. It should run against staging or a disposable database snapshot first.

Planned controlled testers:

1. **Persistence Bot**
   - snapshot character level/EXP/mesos/AP/SP/inventory/equipment/quests/storage;
   - disconnect/reconnect;
   - restart the game service in an explicitly authorized test environment;
   - compare pre/post state and report differences.

2. **World Traversal Bot**
   - consume map/portal metadata;
   - build a directed map graph;
   - find dead ends, missing targets, unreachable starter/town/job-advancement routes;
   - later drive a QA client through selected routes.

3. **NPC/Quest Bot**
   - correlate NPC spawn metadata with `scripts/npc` and quest references;
   - call the existing `scripts/audit_npc_spawns.py` auditor;
   - flag missing/misplaced/scriptless NPCs;
   - validate starter towns and job advancement first.

4. **Economy/Exploit Bot**
   - create controlled trade/storage/shop sequences;
   - compare item/meso totals before and after;
   - test concurrent actions for duplication;
   - never target real player accounts.

5. **Progression Bot**
   - exercise Rooted progression, Rooted Forge, Zakum requirements/rewards;
   - record pacing and reward deltas;
   - flag impossible requirements, loops, and anomalous rewards.

## AI reviewer layer

The deterministic runners should remain the source of evidence. An AI reviewer can consume `build/qa-report.json` and:

- group duplicate findings;
- rank severity and likely player impact;
- suggest investigation order;
- draft GitHub issues for confirmed failures;
- propose fixes on a separate branch.

The AI should **not** be allowed to turn a `REVIEW` finding into a production change without evidence and approval.

## Suggested rollout

1. Land phase-1 static QA and CI.
2. Run it against all active EverLeaf development branches and establish a baseline.
3. Integrate the existing NPC spawn auditor into a unified report.
4. Build staging-only database snapshot tools.
5. Add controlled persistence/world/NPC runtime probes.
6. Add an AI reviewer that reads reports and opens draft issues.
7. Only after repeated clean runs, consider narrowly scoped auto-fixes for deterministic low-risk problems.

## Why this approach

AugurMS demonstrates that MapleStory server administration can be represented as structured tools. EverLeaf uses that pattern for **testing first**: narrow tools, explicit findings, strong read-only defaults, and a clear boundary between diagnosis and mutation.
