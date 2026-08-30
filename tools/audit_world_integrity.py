#!/usr/bin/env python3
"""Static EverLeaf world-data integrity audit.

This audit is intentionally conservative: it fails CI only for references that
should be structurally impossible in a healthy client/server data set (for
example, a spawned NPC or mob with no matching WZ definition, or a normal
portal targeting a map that is absent from Map.wz).

Script coverage is reported as review information because many retail NPCs and
portals legitimately do not have a server-side script.
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"
NPC_ROOT = ROOT / "wz" / "Npc.wz"
MOB_ROOT = ROOT / "wz" / "Mob.wz"
REACTOR_ROOT = ROOT / "wz" / "Reactor.wz"
NPC_SCRIPT_ROOT = ROOT / "scripts" / "npc"
PORTAL_SCRIPT_ROOT = ROOT / "scripts" / "portal"


@dataclass(frozen=True)
class Finding:
    kind: str
    map_id: str
    object_id: str
    detail: str


def direct_imgdir(root: ET.Element, name: str) -> ET.Element | None:
    return next(
        (child for child in root if child.tag == "imgdir" and child.attrib.get("name") == name),
        None,
    )


def child_value(node: ET.Element, name: str) -> str | None:
    for child in node:
        if child.attrib.get("name") == name:
            return child.attrib.get("value")
    return None


def resource_ids(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {path.name.split(".", 1)[0].lstrip("0") or "0" for path in root.glob("*.img.xml")}


def map_files() -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in MAP_ROOT.glob("Map*/*.img.xml"):
        raw = path.name.split(".", 1)[0]
        files[str(int(raw)) if raw.isdigit() else raw] = path
    return files


def normalize_id(value: str | None) -> str:
    if value is None:
        return ""
    value = value.strip()
    if value.lstrip("-").isdigit():
        return str(int(value))
    return value


def main() -> int:
    emit_json = "--json" in sys.argv

    required_dirs = [MAP_ROOT, NPC_ROOT, MOB_ROOT, REACTOR_ROOT]
    missing_dirs = [str(path.relative_to(ROOT)) for path in required_dirs if not path.is_dir()]
    if missing_dirs:
        print("Missing required WZ directories: " + ", ".join(missing_dirs), file=sys.stderr)
        return 2

    maps = map_files()
    npc_ids = resource_ids(NPC_ROOT)
    mob_ids = resource_ids(MOB_ROOT)
    reactor_ids = resource_ids(REACTOR_ROOT)

    hard_findings: list[Finding] = []
    review_findings: list[Finding] = []
    parse_errors: list[str] = []
    counts: Counter[str] = Counter()

    for map_id, path in sorted(maps.items(), key=lambda item: int(item[0])):
        try:
            root = ET.parse(path).getroot()
        except (ET.ParseError, OSError) as exc:
            parse_errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue

        life = direct_imgdir(root, "life")
        if life is not None:
            for node in life:
                if node.tag != "imgdir":
                    continue
                life_type = child_value(node, "type")
                object_id = normalize_id(child_value(node, "id"))
                if not object_id:
                    continue

                if life_type == "n":
                    counts["npc_spawns"] += 1
                    if object_id not in npc_ids:
                        hard_findings.append(Finding(
                            "missing_npc_wz", map_id, object_id,
                            f"NPC {object_id} is spawned but wz/Npc.wz/{object_id}.img.xml is missing",
                        ))
                    script = NPC_SCRIPT_ROOT / f"{object_id}.js"
                    if not script.is_file():
                        counts["npc_without_script"] += 1
                elif life_type == "m":
                    counts["mob_spawns"] += 1
                    if object_id not in mob_ids:
                        hard_findings.append(Finding(
                            "missing_mob_wz", map_id, object_id,
                            f"Mob {object_id} is spawned but wz/Mob.wz/{object_id}.img.xml is missing",
                        ))

        reactors = direct_imgdir(root, "reactor")
        if reactors is not None:
            for node in reactors:
                if node.tag != "imgdir":
                    continue
                object_id = normalize_id(child_value(node, "id"))
                if not object_id:
                    continue
                counts["reactor_spawns"] += 1
                if object_id not in reactor_ids:
                    hard_findings.append(Finding(
                        "missing_reactor_wz", map_id, object_id,
                        f"Reactor {object_id} is spawned but wz/Reactor.wz/{object_id}.img.xml is missing",
                    ))

        portals = direct_imgdir(root, "portal")
        if portals is not None:
            for node in portals:
                if node.tag != "imgdir":
                    continue
                counts["portals"] += 1
                portal_name = child_value(node, "pn") or node.attrib.get("name", "?")
                target = normalize_id(child_value(node, "tm"))
                script_name = (child_value(node, "script") or "").strip()

                # -1 and 999999999 are standard scripted/special portal sentinels.
                if target and target not in {"-1", "999999999"} and target not in maps:
                    hard_findings.append(Finding(
                        "missing_target_map", map_id, portal_name,
                        f"Portal {portal_name!r} targets missing map {target}",
                    ))

                if script_name:
                    counts["scripted_portals"] += 1
                    if not (PORTAL_SCRIPT_ROOT / f"{script_name}.js").is_file():
                        review_findings.append(Finding(
                            "missing_portal_script", map_id, portal_name,
                            f"Portal {portal_name!r} references script {script_name!r}, but scripts/portal/{script_name}.js is missing",
                        ))

    payload = {
        "maps": len(maps),
        "npcDefinitions": len(npc_ids),
        "mobDefinitions": len(mob_ids),
        "reactorDefinitions": len(reactor_ids),
        "counts": dict(sorted(counts.items())),
        "parseErrors": parse_errors,
        "hardFailureCount": len(hard_findings) + len(parse_errors),
        "reviewFindingCount": len(review_findings),
        "hardFindings": [asdict(finding) for finding in hard_findings],
        "reviewFindings": [asdict(finding) for finding in review_findings],
    }

    if emit_json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            "EverLeaf world integrity audit: "
            f"{len(maps)} maps, {counts['npc_spawns']} NPC spawns, "
            f"{counts['mob_spawns']} mob spawns, {counts['portals']} portals"
        )
        print(
            f"Hard failures: {payload['hardFailureCount']}; "
            f"review-only findings: {payload['reviewFindingCount']}; "
            f"NPCs without dedicated scripts: {counts['npc_without_script']}"
        )
        for error in parse_errors:
            print(f"[FAIL] XML parse error: {error}")
        for finding in hard_findings:
            print(f"[FAIL] map={finding.map_id} {finding.detail}")
        for finding in review_findings[:50]:
            print(f"[REVIEW] map={finding.map_id} {finding.detail}")
        if len(review_findings) > 50:
            print(f"[REVIEW] ... {len(review_findings) - 50} additional review-only findings omitted")

    return 1 if parse_errors or hard_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
