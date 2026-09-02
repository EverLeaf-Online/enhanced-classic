#!/usr/bin/env python3
"""Profile a donor region as a complete review-only dependency cluster.

The profiler does not approve or import content. It resolves selected donor maps,
inspects map life/reactor/portal references, checks whether dependencies already
exist in the v83 baseline, and finds Quest.wz nodes that reference selected map,
mob, or item IDs.
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

ID_FILE_RE = re.compile(r"^(\d+)\.img\.xml$")
NUMERIC_RE = re.compile(r"^\d+$")


def prop_map(node: ET.Element) -> dict[str, str]:
    out: dict[str, str] = {}
    for child in list(node):
        name = child.attrib.get("name")
        if name is None:
            continue
        value = child.attrib.get("value")
        if value is not None:
            out[name] = value
    return out


def index_family(root: Path, family: str) -> dict[str, Path]:
    base = root / family
    found: dict[str, Path] = {}
    if not base.exists():
        return found
    for path in base.rglob("*.img.xml"):
        match = ID_FILE_RE.match(path.name)
        if match:
            found[match.group(1)] = path
    return found


def resolve_cluster(manifest: dict, donor_root: Path) -> tuple[list[str], list[str], list[str]]:
    donor_maps = index_family(donor_root, "Map.wz")
    donor_mobs = index_family(donor_root, "Mob.wz")
    prefixes = [str(prefix) for prefix in manifest.get("mapPrefixes", [])]
    explicit_maps = {str(value) for value in manifest.get("mapIds", [])}
    map_ids = sorted({mid for mid in donor_maps if mid in explicit_maps or any(mid.startswith(prefix) for prefix in prefixes)}, key=int)

    explicit_mobs = {str(value) for value in manifest.get("mobIds", [])}
    mob_prefixes = [str(prefix) for prefix in manifest.get("mobPrefixes", [])]
    mob_ids = sorted({mid for mid in donor_mobs if mid in explicit_mobs or any(mid.startswith(prefix) for prefix in mob_prefixes)}, key=int)
    item_ids = sorted({str(value) for value in manifest.get("itemIds", [])}, key=int)
    return map_ids, mob_ids, item_ids


def parse_map_dependencies(path: Path) -> dict:
    root = ET.parse(path).getroot()
    mobs: set[str] = set()
    npcs: set[str] = set()
    reactors: set[str] = set()
    portal_targets: set[str] = set()
    portal_scripts: set[str] = set()

    for node in root.iter():
        props = prop_map(node)
        life_type = props.get("type")
        life_id = props.get("id")
        if life_type == "m" and life_id and life_id.isdigit():
            mobs.add(life_id)
        elif life_type == "n" and life_id and life_id.isdigit():
            npcs.add(life_id)

        # Reactor entries have an id property but no life type. Restrict to
        # ancestry-by-container-name heuristics encoded in the node's own name.
        if life_type is None and life_id and life_id.isdigit():
            node_name = (node.attrib.get("name") or "").lower()
            if "reactor" in node_name:
                reactors.add(life_id)

        tm = props.get("tm")
        if tm and tm.isdigit() and tm != "999999999":
            portal_targets.add(tm)
        script = props.get("script")
        if script:
            portal_scripts.add(script)

    # Common WZ structure keeps reactor ids below an imgdir named "reactor".
    for container in root.iter():
        if (container.attrib.get("name") or "").lower() != "reactor":
            continue
        for entry in list(container):
            props = prop_map(entry)
            rid = props.get("id")
            if rid and rid.isdigit():
                reactors.add(rid)

    return {
        "mobs": sorted(mobs, key=int),
        "npcs": sorted(npcs, key=int),
        "reactors": sorted(reactors, key=int),
        "portalTargets": sorted(portal_targets, key=int),
        "portalScripts": sorted(portal_scripts),
    }


def quest_references(quest_root: Path, selected_ids: set[str]) -> dict[str, list[str]]:
    refs: dict[str, set[str]] = defaultdict(set)
    if not quest_root.exists() or not selected_ids:
        return {}
    alternation = "|".join(re.escape(value) for value in sorted(selected_ids, key=len, reverse=True))
    token_re = re.compile(rf"(?<!\d)(?:{alternation})(?!\d)")

    for path in quest_root.rglob("*.xml"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if not token_re.search(text):
            continue
        try:
            tree = ET.fromstring(text)
        except ET.ParseError:
            continue

        def walk(node: ET.Element, numeric_stack: list[str]) -> None:
            name = node.attrib.get("name")
            stack = numeric_stack
            if name and NUMERIC_RE.fullmatch(name):
                stack = numeric_stack + [name]
            haystack = " ".join([node.attrib.get("value", ""), node.text or ""])
            matched = set(token_re.findall(haystack))
            if matched:
                quest_id = stack[-1] if stack else path.stem
                refs[str(quest_id)].update(matched)
            for child in list(node):
                walk(child, stack)

        walk(tree, [])
    return {qid: sorted(values, key=int) for qid, values in sorted(refs.items(), key=lambda pair: int(pair[0]) if pair[0].isdigit() else 10**12)}


def baseline_script_exists(baseline_root: Path, script: str) -> bool:
    candidates = [
        baseline_root / "scripts" / "portal" / f"{script}.js",
        baseline_root / "scripts" / "portal" / script,
    ]
    return any(path.is_file() for path in candidates)


def build_report(manifest: dict, donor_root: Path, baseline_root: Path) -> dict:
    map_ids, selected_mobs, item_ids = resolve_cluster(manifest, donor_root)
    donor_maps = index_family(donor_root, "Map.wz")
    donor_mobs = index_family(donor_root, "Mob.wz")
    donor_npcs = index_family(donor_root, "Npc.wz")
    donor_reactors = index_family(donor_root, "Reactor.wz")
    baseline_maps = index_family(baseline_root, "Map.wz")
    baseline_mobs = index_family(baseline_root, "Mob.wz")
    baseline_npcs = index_family(baseline_root, "Npc.wz")
    baseline_reactors = index_family(baseline_root, "Reactor.wz")

    aggregate_mobs: set[str] = set(selected_mobs)
    aggregate_npcs: set[str] = set()
    aggregate_reactors: set[str] = set()
    portal_targets: set[str] = set()
    portal_scripts: set[str] = set()
    per_map: dict[str, dict] = {}

    for map_id in map_ids:
        deps = parse_map_dependencies(donor_maps[map_id])
        per_map[map_id] = deps
        aggregate_mobs.update(deps["mobs"])
        aggregate_npcs.update(deps["npcs"])
        aggregate_reactors.update(deps["reactors"])
        portal_targets.update(deps["portalTargets"])
        portal_scripts.update(deps["portalScripts"])

    selected_ids = set(map_ids) | aggregate_mobs | set(item_ids)
    quests = quest_references(donor_root / "Quest.wz", selected_ids)

    def classify(ids: set[str] | list[str], donor_index: dict[str, Path], baseline_index: dict[str, Path]) -> list[dict]:
        rows = []
        for content_id in sorted(set(ids), key=int):
            rows.append({
                "contentId": content_id,
                "inDonor": content_id in donor_index,
                "inBaseline": content_id in baseline_index,
                "needsBackport": content_id in donor_index and content_id not in baseline_index,
            })
        return rows

    target_rows = []
    cluster_set = set(map_ids)
    for target in sorted(portal_targets, key=int):
        target_rows.append({
            "mapId": target,
            "insideCluster": target in cluster_set,
            "inDonor": target in donor_maps,
            "inBaseline": target in baseline_maps,
            "unresolved": target not in donor_maps and target not in baseline_maps,
        })

    script_rows = [{"script": script, "baselineScriptExists": baseline_script_exists(baseline_root, script)} for script in sorted(portal_scripts)]
    missing_scripts = [row["script"] for row in script_rows if not row["baselineScriptExists"]]
    unresolved_targets = [row["mapId"] for row in target_rows if row["unresolved"]]

    return {
        "schemaVersion": 1,
        "kind": "review-only-region-cluster-profile",
        "clusterId": manifest.get("clusterId"),
        "donorId": manifest.get("donorId"),
        "selection": {"mapPrefixes": manifest.get("mapPrefixes", []), "mapIds": manifest.get("mapIds", []), "mobPrefixes": manifest.get("mobPrefixes", []), "mobIds": manifest.get("mobIds", []), "itemIds": item_ids},
        "counts": {
            "maps": len(map_ids), "mapReferencedMobs": len(aggregate_mobs), "mapReferencedNpcs": len(aggregate_npcs),
            "mapReferencedReactors": len(aggregate_reactors), "portalTargets": len(portal_targets), "portalScripts": len(portal_scripts),
            "questNodes": len(quests), "selectedItems": len(item_ids),
        },
        "maps": classify(set(map_ids), donor_maps, baseline_maps),
        "mobs": classify(aggregate_mobs, donor_mobs, baseline_mobs),
        "npcs": classify(aggregate_npcs, donor_npcs, baseline_npcs),
        "reactors": classify(aggregate_reactors, donor_reactors, baseline_reactors),
        "portalTargets": target_rows,
        "portalScripts": script_rows,
        "questReferences": quests,
        "items": item_ids,
        "perMapDependencies": per_map,
        "blockingReview": {"missingPortalScripts": missing_scripts, "unresolvedPortalTargets": unresolved_targets},
        "approved": False,
        "importAllowed": False,
        "automaticImport": False,
        "note": "This report only scopes dependencies. It does not establish gameplay correctness, script compatibility, client parity, drop tables, or import safety.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Profile a review-only donor region dependency cluster")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--donor", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    report = build_report(manifest, args.donor, args.baseline)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"], sort_keys=True))
    print("missing portal scripts:", len(report["blockingReview"]["missingPortalScripts"]))
    print("unresolved portal targets:", len(report["blockingReview"]["unresolvedPortalTargets"]))
    print("approved=false / importAllowed=false / automaticImport=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
