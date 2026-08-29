#!/usr/bin/env python3
"""EverLeaf deep static QA.

Correlates WZ map content with scripts/assets and validates portal topology without
connecting to production or mutating data. Intended to complement everleaf_qa.py.
"""
from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict, deque
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"
NPC_ROOT = ROOT / "wz" / "Npc.wz"
NPC_SCRIPTS = ROOT / "scripts" / "npc"
PORTAL_SCRIPTS = ROOT / "scripts" / "portal"


@dataclass(frozen=True)
class Finding:
    agent: str
    status: str
    code: str
    message: str
    subject: str = ""
    path: str = ""


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def child(node: ET.Element, name: str) -> str | None:
    for c in node:
        if c.attrib.get("name") == name:
            return c.attrib.get("value")
    return None


def section(root: ET.Element, name: str) -> ET.Element | None:
    for c in root:
        if c.tag == "imgdir" and c.attrib.get("name") == name:
            return c
    return None


def map_files() -> list[Path]:
    return sorted(MAP_ROOT.glob("Map*/*.img.xml")) if MAP_ROOT.is_dir() else []


def parse_maps() -> tuple[dict[str, Path], dict[str, set[str]], list[dict], list[dict], list[Finding]]:
    maps: dict[str, Path] = {}
    portal_names: dict[str, set[str]] = defaultdict(set)
    npcs: list[dict] = []
    portals: list[dict] = []
    findings: list[Finding] = []
    for path in map_files():
        mid = path.name.split(".", 1)[0]
        maps[mid] = path
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as e:
            findings.append(Finding("world", "FAIL", "malformed-map-xml", str(e), mid, rel(path)))
            continue
        life = section(root, "life")
        if life is not None:
            for node in life:
                if node.tag == "imgdir" and child(node, "type") == "n":
                    npcs.append({"map": mid, "npc": child(node, "id") or "", "node": node.attrib.get("name", ""), "path": path})
        ps = section(root, "portal")
        if ps is not None:
            for node in ps:
                if node.tag != "imgdir":
                    continue
                pn = child(node, "pn") or ""
                tm = child(node, "tm") or ""
                tn = child(node, "tn") or ""
                script = child(node, "script") or ""
                if pn:
                    portal_names[mid].add(pn)
                portals.append({"map": mid, "pn": pn, "tm": tm, "tn": tn, "script": script, "path": path})
    return maps, portal_names, npcs, portals, findings


def npc_agent(maps: dict[str, Path], npcs: list[dict]) -> list[Finding]:
    out: list[Finding] = []
    spawned = Counter(n["npc"] for n in npcs if n["npc"].isdigit())
    out.append(Finding("npc-correlation", "PASS" if npcs else "FAIL", "spawn-inventory", f"Indexed {len(npcs)} NPC spawns across {len(maps)} maps."))

    missing_assets = []
    no_script = []
    for npc_id in sorted(spawned):
        asset = NPC_ROOT / f"{int(npc_id):07d}.img.xml"
        script = NPC_SCRIPTS / f"{npc_id}.js"
        if not asset.is_file():
            missing_assets.append(npc_id)
        if not script.is_file():
            no_script.append(npc_id)
    if missing_assets:
        for npc_id in missing_assets[:50]:
            out.append(Finding("npc-correlation", "FAIL", "spawn-missing-asset", "Spawned NPC has no Npc.wz asset.", npc_id))
    else:
        out.append(Finding("npc-correlation", "PASS", "spawn-assets", "Every spawned numeric NPC ID has a matching Npc.wz asset."))

    # Missing script is REVIEW, not FAIL: many decorative/shop NPCs are intentionally scriptless.
    out.append(Finding("npc-correlation", "REVIEW" if no_script else "PASS", "spawn-script-coverage", f"{len(no_script)} of {len(spawned)} unique spawned NPC IDs have no same-ID NPC script; review against shops/decorative NPCs."))

    numeric_scripts = {p.stem for p in NPC_SCRIPTS.glob("*.js") if p.stem.isdigit()} if NPC_SCRIPTS.is_dir() else set()
    orphan = sorted(numeric_scripts - set(spawned))
    out.append(Finding("npc-correlation", "REVIEW" if orphan else "PASS", "orphan-npc-scripts", f"{len(orphan)} numeric NPC scripts are not directly represented by a current map spawn; event/summoned NPCs may be legitimate."))
    return out


def portal_agent(maps: dict[str, Path], portal_names: dict[str, set[str]], portals: list[dict]) -> list[Finding]:
    out: list[Finding] = []
    graph: dict[str, set[str]] = defaultdict(set)
    broken_maps = []
    broken_names = []
    missing_scripts = []
    self_loops = []
    ignored_targets = {"", "0", "999999999"}

    for p in portals:
        tm = p["tm"]
        src = p["map"]
        if p["script"]:
            script_file = PORTAL_SCRIPTS / f"{p['script']}.js"
            if not script_file.is_file():
                missing_scripts.append((src, p["pn"], p["script"]))
        if tm in ignored_targets or not tm.isdigit():
            continue
        if tm not in maps:
            broken_maps.append((src, p["pn"], tm))
            continue
        graph[src].add(tm)
        if tm == src:
            self_loops.append((src, p["pn"]))
        tn = p["tn"]
        if tn and tn not in {"sp", "portal"} and tn not in portal_names.get(tm, set()):
            broken_names.append((src, p["pn"], tm, tn))

    for src, pn, tm in broken_maps[:100]:
        out.append(Finding("portal-graph", "FAIL", "missing-target-map", f"Portal {pn or '?'} targets map {tm}, which is absent from Map.wz.", src))
    for src, pn, tm, tn in broken_names[:100]:
        out.append(Finding("portal-graph", "REVIEW", "missing-target-portal", f"Portal {pn or '?'} targets {tm}:{tn}, but that target portal name was not found.", src))
    for src, pn, script in missing_scripts[:100]:
        out.append(Finding("portal-graph", "FAIL", "missing-portal-script", f"Portal {pn or '?'} references missing script {script}.js.", src))

    out.append(Finding("portal-graph", "PASS" if not broken_maps else "FAIL", "target-map-integrity", f"Checked {len(portals)} portals; {len(broken_maps)} reference missing target maps."))
    out.append(Finding("portal-graph", "PASS" if not missing_scripts else "FAIL", "portal-script-integrity", f"{len(missing_scripts)} portal script references are missing."))
    out.append(Finding("portal-graph", "REVIEW" if broken_names else "PASS", "target-portal-integrity", f"{len(broken_names)} cross-map target portal names require review."))
    out.append(Finding("portal-graph", "REVIEW" if self_loops else "PASS", "self-loops", f"{len(self_loops)} explicit numeric portal self-loops found."))

    # Reachability is advisory because scripted/event portals are intentionally absent from the numeric graph.
    starts = [m for m in ("0", "100000000", "104000000") if m in maps]
    reached: set[str] = set(starts)
    q = deque(starts)
    while q:
        src = q.popleft()
        for dst in graph.get(src, ()):
            if dst not in reached:
                reached.add(dst); q.append(dst)
    if starts:
        unreachable = len(set(maps) - reached)
        out.append(Finding("portal-graph", "REVIEW", "static-reachability", f"Numeric portal graph reaches {len(reached)}/{len(maps)} maps from {', '.join(starts)}; {unreachable} maps depend on other starts, scripted transport, events, or are unreachable."))
    return out


def progression_agent() -> list[Finding]:
    out: list[Finding] = []
    roots = [ROOT / "src/main/java", ROOT / "database/sql/migration", ROOT / "scripts"]
    files = [p for r in roots if r.exists() for p in r.rglob("*") if p.is_file() and p.suffix.lower() in {".java", ".sql", ".js"}]
    corpus = "\n".join(p.read_text(encoding="utf-8", errors="replace").lower() for p in files)
    checks = {
        "rooted": "Rooted progression",
        "everleaf_rooted_forge": "Rooted Forge persistence",
        "zakum": "Zakum progression",
        "everleaf_weekly": "weekly progression persistence",
        "verdant": "Verdant progression/rewards",
    }
    for needle, label in checks.items():
        ok = needle in corpus
        out.append(Finding("progression-deep", "PASS" if ok else "REVIEW", f"presence-{needle}", f"{label}: {'detected' if ok else 'not detected by repository-wide static scan'}."))

    migration_dir = ROOT / "database/sql/migration"
    migrations = sorted(migration_dir.glob("*.sql")) if migration_dir.is_dir() else []
    duplicate_create: dict[str, list[str]] = defaultdict(list)
    create_re = re.compile(r"create\s+table\s+(?:if\s+not\s+exists\s+)?`?([a-zA-Z0-9_]+)`?", re.I)
    for p in migrations:
        for table in create_re.findall(p.read_text(encoding="utf-8", errors="replace")):
            duplicate_create[table.lower()].append(rel(p))
    dupes = {k:v for k,v in duplicate_create.items() if len(v) > 1}
    out.append(Finding("progression-deep", "REVIEW" if dupes else "PASS", "duplicate-table-migrations", f"{len(dupes)} tables are CREATEd by more than one migration; review idempotency/order if nonzero."))
    return out


def exploit_agent() -> list[Finding]:
    out: list[Finding] = []
    java = list((ROOT / "src/main/java").rglob("*.java")) if (ROOT / "src/main/java").is_dir() else []
    keywords = {
        "trade": ("trade", "playertrade", "tradehandler"),
        "storage": ("storage", "storagehandler"),
        "shop": ("shop", "merchant"),
        "drop": ("drop", "pickup"),
    }
    for surface, needles in keywords.items():
        hits = [p for p in java if any(n in p.name.lower() for n in needles)]
        out.append(Finding("exploit-surface", "PASS" if hits else "REVIEW", f"surface-{surface}", f"Indexed {len(hits)} Java files for {surface} exploit/regression review."))

    # Detect suspicious DB mutation sequences in transaction-sensitive handlers.
    risky = []
    for p in java:
        name = p.name.lower()
        if not any(k in name for k in ("trade", "storage", "shop", "merchant")):
            continue
        body = p.read_text(encoding="utf-8", errors="replace").lower()
        mutations = sum(body.count(x) for x in ("delete", "insert", "update", "removeitem", "additem"))
        has_tx = any(x in body for x in ("setautocommit(false", "commit()", "rollback()", "transaction"))
        if mutations >= 4 and not has_tx:
            risky.append(rel(p))
    out.append(Finding("exploit-surface", "REVIEW" if risky else "PASS", "transaction-review", f"{len(risky)} trade/storage/shop Java files show multiple mutation-like operations without an obvious transaction marker; static heuristic only."))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="json_path")
    args = ap.parse_args()
    maps, portal_names, npcs, portals, findings = parse_maps()
    findings += npc_agent(maps, npcs)
    findings += portal_agent(maps, portal_names, portals)
    findings += progression_agent()
    findings += exploit_agent()
    summary = {s: sum(f.status == s for f in findings) for s in ("PASS", "REVIEW", "FAIL")}
    report = {"schema_version": 1, "summary": summary, "findings": [asdict(f) for f in findings]}
    if args.json_path:
        p = ROOT / args.json_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    for f in findings:
        if f.status != "PASS":
            print(f"[{f.status}] {f.agent}/{f.code}: {f.message}" + (f" ({f.subject})" if f.subject else ""))
    return 1 if summary["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
