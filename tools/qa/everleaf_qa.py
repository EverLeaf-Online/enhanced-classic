#!/usr/bin/env python3
"""EverLeaf QA Agent Hub (phase 1).

Read-only deterministic QA runners inspired by AugurMS's structured-tool approach.
No production mutation, credentials, network calls, or database writes are performed.

Usage:
  python3 tools/qa/everleaf_qa.py
  python3 tools/qa/everleaf_qa.py --json build/qa-report.json --markdown build/qa-report.md
  python3 tools/qa/everleaf_qa.py --agent content

Exit codes:
  0 = no FAIL findings
  1 = one or more FAIL findings
  2 = configuration/usage error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]

STATUS_ORDER = {"PASS": 0, "REVIEW": 1, "FAIL": 2}


@dataclass(frozen=True)
class Finding:
    agent: str
    check: str
    status: str
    message: str
    path: str | None = None
    evidence: str | None = None


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def text_files(base: Path, suffixes: tuple[str, ...]) -> Iterable[Path]:
    if not base.exists():
        return []
    return (p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in suffixes)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def finding(agent: str, check: str, status: str, message: str, path: Path | None = None, evidence: str | None = None) -> Finding:
    if status not in STATUS_ORDER:
        raise ValueError(status)
    return Finding(agent, check, status, message, rel(path) if path else None, evidence)


def inventory_agent() -> list[Finding]:
    agent = "inventory"
    findings: list[Finding] = []
    expected = {
        "npc": ROOT / "scripts/npc",
        "portal": ROOT / "scripts/portal",
        "quest": ROOT / "scripts/quest",
        "map": ROOT / "scripts/map",
        "event": ROOT / "scripts/event",
        "reactor": ROOT / "scripts/reactor",
        "item": ROOT / "scripts/item",
    }
    missing = [name for name, path in expected.items() if not path.is_dir()]
    if missing:
        findings.append(finding(agent, "script-directories", "FAIL", f"Missing script directories: {', '.join(missing)}"))
    else:
        findings.append(finding(agent, "script-directories", "PASS", "All expected script directories exist."))
    for name, path in expected.items():
        if path.exists():
            count = sum(1 for _ in path.rglob("*.js"))
            findings.append(finding(agent, f"{name}-count", "PASS" if count else "REVIEW", f"{count} JavaScript files discovered.", path))
    return findings


def content_agent() -> list[Finding]:
    agent = "content"
    findings: list[Finding] = []
    dirs = [ROOT / "scripts/npc", ROOT / "scripts/portal", ROOT / "scripts/quest", ROOT / "scripts/map", ROOT / "scripts/event", ROOT / "scripts/reactor", ROOT / "scripts/item"]
    files: list[Path] = []
    for d in dirs:
        if d.exists():
            files.extend(d.rglob("*.js"))
    findings.append(finding(agent, "script-inventory", "PASS" if files else "FAIL", f"Scanned {len(files)} gameplay scripts."))

    suspicious: list[tuple[Path, str]] = []
    todo: list[Path] = []
    numeric_bad: list[Path] = []
    for p in files:
        body = read(p)
        compact = re.sub(r"\s+", "", body)
        if len(compact) < 20:
            suspicious.append((p, "near-empty"))
        if re.search(r"\b(TODO|FIXME|XXX)\b", body, re.I):
            todo.append(p)
        if p.parent.name in {"npc", "quest", "reactor"} and p.stem.isdigit() and int(p.stem) <= 0:
            numeric_bad.append(p)

    if suspicious:
        for p, why in suspicious[:25]:
            findings.append(finding(agent, "script-body", "REVIEW", f"Gameplay script is {why}.", p))
        if len(suspicious) > 25:
            findings.append(finding(agent, "script-body", "REVIEW", f"{len(suspicious)-25} additional suspicious scripts omitted from console detail."))
    else:
        findings.append(finding(agent, "script-body", "PASS", "No near-empty gameplay scripts found."))

    if todo:
        findings.append(finding(agent, "todo-markers", "REVIEW", f"{len(todo)} gameplay scripts contain TODO/FIXME/XXX markers.", todo[0], "first match"))
    else:
        findings.append(finding(agent, "todo-markers", "PASS", "No TODO/FIXME/XXX markers found in gameplay scripts."))

    if numeric_bad:
        findings.append(finding(agent, "script-ids", "FAIL", f"{len(numeric_bad)} numeric script filenames contain invalid non-positive IDs.", numeric_bad[0]))
    else:
        findings.append(finding(agent, "script-ids", "PASS", "Numeric NPC/quest/reactor script IDs are positive."))

    return findings


def world_agent() -> list[Finding]:
    agent = "world"
    findings: list[Finding] = []
    portal_dir = ROOT / "scripts/portal"
    map_dir = ROOT / "scripts/map"
    portal_files = list(portal_dir.rglob("*.js")) if portal_dir.exists() else []
    map_files = list(map_dir.rglob("*.js")) if map_dir.exists() else []
    findings.append(finding(agent, "portal-inventory", "PASS" if portal_files else "FAIL", f"Found {len(portal_files)} portal scripts."))
    findings.append(finding(agent, "map-script-inventory", "PASS" if map_files else "REVIEW", f"Found {len(map_files)} map scripts."))

    warp_pattern = re.compile(r"\b(?:warp|changeMap|warpMap)\s*\(\s*(\d{5,9})")
    targets: dict[int, list[Path]] = {}
    malformed: list[Path] = []
    for p in portal_files + map_files:
        body = read(p)
        for m in warp_pattern.finditer(body):
            targets.setdefault(int(m.group(1)), []).append(p)
        if re.search(r"\b(?:warp|changeMap|warpMap)\s*\(\s*[-]?\d{1,4}\b", body):
            malformed.append(p)

    if malformed:
        for p in malformed[:20]:
            findings.append(finding(agent, "warp-target-shape", "REVIEW", "Suspicious short/negative map target in warp-style call.", p))
    else:
        findings.append(finding(agent, "warp-target-shape", "PASS", "No obviously malformed numeric warp targets found."))

    findings.append(finding(agent, "warp-reference-inventory", "PASS" if targets else "REVIEW", f"Collected {len(targets)} unique numeric map targets for later WZ/runtime validation."))
    return findings


def persistence_agent() -> list[Finding]:
    agent = "persistence"
    findings: list[Finding] = []
    sql_files = list(text_files(ROOT / "database", (".sql",)))
    corpus = "\n".join(read(p).lower() for p in sql_files)
    required = {
        "accounts": "account persistence",
        "characters": "character persistence",
        "inventoryitems": "inventory persistence",
        "inventoryequipment": "equipment persistence",
        "storages": "storage persistence",
        "queststatus": "quest persistence",
    }
    for table, purpose in required.items():
        if re.search(rf"\b{re.escape(table)}\b", corpus):
            findings.append(finding(agent, f"schema-{table}", "PASS", f"Schema references {table} ({purpose})."))
        else:
            findings.append(finding(agent, f"schema-{table}", "FAIL", f"No database SQL reference found for {table} ({purpose})."))

    findings.append(finding(agent, "runtime-restart-test", "REVIEW", "Static audit cannot prove logout/reconnect/restart persistence. Run controlled test-character snapshots before and after a service restart."))
    return findings


def progression_agent() -> list[Finding]:
    agent = "progression"
    findings: list[Finding] = []
    enhanced = ROOT / "src/main/java/service/enhanced"
    migration = ROOT / "database/sql/migration"
    java_files = list(text_files(enhanced, (".java",)))
    sql_files = list(text_files(migration, (".sql",)))
    corpus = "\n".join(read(p).lower() for p in java_files + sql_files)

    concepts = {
        "rooted": "Rooted progression",
        "forge": "Rooted Forge",
        "zakum": "Zakum encounter/progression",
        "weekly": "weekly progression",
    }
    for needle, label in concepts.items():
        status = "PASS" if needle in corpus else "REVIEW"
        findings.append(finding(agent, f"concept-{needle}", status, f"{label} {'is represented in enhanced code/migrations' if status == 'PASS' else 'was not detected by static keyword scan'}."))

    todo_files = [p for p in java_files + sql_files if re.search(r"\b(TODO|FIXME|XXX)\b", read(p), re.I)]
    if todo_files:
        findings.append(finding(agent, "enhanced-todos", "REVIEW", f"{len(todo_files)} enhanced progression files contain TODO/FIXME/XXX markers.", todo_files[0]))
    else:
        findings.append(finding(agent, "enhanced-todos", "PASS", "No TODO/FIXME/XXX markers in enhanced progression code/migrations."))
    return findings


def economy_agent() -> list[Finding]:
    agent = "economy"
    findings: list[Finding] = []
    sql_files = list(text_files(ROOT / "database", (".sql",)))
    risky: list[tuple[Path, str]] = []
    for p in sql_files:
        body = read(p)
        for pattern, reason in [
            (r"\b(quantity|maximum_quantity)\s*[=,)]\s*-\d+", "negative quantity"),
            (r"\b(chance|probability|dropchance)\s*[=,)]\s*-\d+", "negative chance"),
            (r"\b(price|meso|mesos)\s*[=,)]\s*-\d+", "negative price/meso value"),
        ]:
            if re.search(pattern, body, re.I):
                risky.append((p, reason))
    if risky:
        for p, reason in risky[:20]:
            findings.append(finding(agent, "negative-economic-value", "REVIEW", f"Potential {reason}; inspect context before changing data.", p))
    else:
        findings.append(finding(agent, "negative-economic-value", "PASS", "No obvious negative quantity/chance/price patterns found in SQL."))

    merchant = [p for p in ROOT.rglob("*.java") if "merchant" in p.name.lower() or "shop" in p.name.lower()]
    findings.append(finding(agent, "shop-surface", "PASS" if merchant else "REVIEW", f"Identified {len(merchant)} Java files with merchant/shop in the filename for exploit review."))
    findings.append(finding(agent, "runtime-dupe-test", "REVIEW", "Static audit cannot prove absence of trade/storage/shop duplication exploits. Controlled concurrent-client tests are required."))
    return findings


def regression_agent() -> list[Finding]:
    agent = "regression"
    findings: list[Finding] = []
    tests = list((ROOT / "src/test").rglob("*.java")) if (ROOT / "src/test").exists() else []
    qa_script = ROOT / "scripts/audit_npc_spawns.py"
    findings.append(finding(agent, "java-tests", "PASS" if tests else "REVIEW", f"Found {len(tests)} Java test files."))
    findings.append(finding(agent, "npc-auditor", "PASS" if qa_script.exists() else "REVIEW", "Existing NPC spawn auditor is available and should be incorporated into runtime/content regression." if qa_script.exists() else "Existing NPC spawn auditor not found."))
    findings.append(finding(agent, "production-mutation", "PASS", "Phase-1 QA runner performs no production writes or network calls."))
    return findings


AGENTS = {
    "inventory": inventory_agent,
    "content": content_agent,
    "world": world_agent,
    "persistence": persistence_agent,
    "progression": progression_agent,
    "economy": economy_agent,
    "regression": regression_agent,
}


def render_markdown(findings: list[Finding], generated: str) -> str:
    totals = {s: sum(1 for f in findings if f.status == s) for s in STATUS_ORDER}
    lines = [
        "# EverLeaf QA Agent Report",
        "",
        f"Generated: {generated}",
        "",
        f"**PASS:** {totals['PASS']}  **REVIEW:** {totals['REVIEW']}  **FAIL:** {totals['FAIL']}",
        "",
    ]
    for agent in AGENTS:
        rows = [f for f in findings if f.agent == agent]
        if not rows:
            continue
        lines += [f"## {agent.title()} Agent", "", "| Status | Check | Finding | Path |", "|---|---|---|---|"]
        for f in rows:
            msg = f.message.replace("|", "\\|")
            path = (f.path or "").replace("|", "\\|")
            lines.append(f"| {f.status} | `{f.check}` | {msg} | `{path}` |")
        lines.append("")
    lines += [
        "## Interpretation",
        "",
        "`FAIL` means a deterministic invariant failed. `REVIEW` means the agent found something requiring runtime validation or human/AI judgment. The phase-1 hub is intentionally read-only.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run EverLeaf read-only QA agents")
    parser.add_argument("--agent", choices=["all", *AGENTS], default="all")
    parser.add_argument("--json", dest="json_path")
    parser.add_argument("--markdown", dest="markdown_path")
    args = parser.parse_args()

    names = list(AGENTS) if args.agent == "all" else [args.agent]
    findings: list[Finding] = []
    for name in names:
        findings.extend(AGENTS[name]())

    findings.sort(key=lambda f: (STATUS_ORDER[f.status], f.agent, f.check), reverse=True)
    generated = datetime.now(timezone.utc).isoformat()
    report = {
        "schema_version": 1,
        "generated_at": generated,
        "root": str(ROOT),
        "agents": names,
        "summary": {s: sum(1 for f in findings if f.status == s) for s in STATUS_ORDER},
        "findings": [asdict(f) for f in findings],
    }

    if args.json_path:
        p = ROOT / args.json_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.markdown_path:
        p = ROOT / args.markdown_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(render_markdown(findings, generated), encoding="utf-8")

    print(json.dumps(report["summary"], sort_keys=True))
    for f in findings:
        print(f"[{f.status}] {f.agent}/{f.check}: {f.message}" + (f" ({f.path})" if f.path else ""))

    return 1 if any(f.status == "FAIL" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
