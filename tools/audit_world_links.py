#!/usr/bin/env python3
"""EverLeaf static world-link and exact-duplicate audit.

Complements audit_world_integrity.py with checks that need a complete map index:
- static portals whose named destination portal does not exist on the target map
- exact duplicate NPC, mob, reactor, or portal records at the same coordinates

Ambiguous duplicate content is review-only. Broken named static portal destinations are
hard failures because the source map points at a concrete target map + portal pair that
cannot be resolved from Map.wz.
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"
SPECIAL_TARGETS = {"-1", "999999999"}


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


def normalize_id(value: str | None) -> str:
    if value is None:
        return ""
    value = value.strip()
    if value.lstrip("-").isdigit():
        return str(int(value))
    return value


def map_files() -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in MAP_ROOT.glob("Map*/*.img.xml"):
        raw = path.name.split(".", 1)[0]
        files[str(int(raw)) if raw.isdigit() else raw] = path
    return files


def exact_xy(node: ET.Element) -> tuple[str, str]:
    return (child_value(node, "x") or "?", child_value(node, "y") or "?")


def main() -> int:
    emit_json = "--json" in sys.argv
    if not MAP_ROOT.is_dir():
        print(f"Missing required WZ directory: {MAP_ROOT.relative_to(ROOT)}", file=sys.stderr)
        return 2

    maps = map_files()
    parsed: dict[str, ET.Element] = {}
    parse_errors: list[str] = []
    portal_names: dict[str, set[str]] = defaultdict(set)
    counts: Counter[str] = Counter()
    hard_findings: list[Finding] = []
    review_findings: list[Finding] = []

    # First pass: parse once and build the complete portal-name index.
    for map_id, path in sorted(maps.items(), key=lambda item: int(item[0])):
        try:
            root = ET.parse(path).getroot()
            parsed[map_id] = root
        except (ET.ParseError, OSError) as exc:
            parse_errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue

        portals = direct_imgdir(root, "portal")
        if portals is None:
            continue
        for node in portals:
            if node.tag != "imgdir":
                continue
            name = (child_value(node, "pn") or "").strip()
            if name:
                portal_names[map_id].add(name)

    # Second pass: validate static target portal names and exact duplicate records.
    for map_id, root in sorted(parsed.items(), key=lambda item: int(item[0])):
        life = direct_imgdir(root, "life")
        if life is not None:
            seen_life: Counter[tuple[str, str, str, str]] = Counter()
            for node in life:
                if node.tag != "imgdir":
                    continue
                life_type = (child_value(node, "type") or "").strip()
                object_id = normalize_id(child_value(node, "id"))
                x, y = exact_xy(node)
                if life_type in {"n", "m"} and object_id:
                    seen_life[(life_type, object_id, x, y)] += 1

            for (life_type, object_id, x, y), amount in seen_life.items():
                if amount <= 1:
                    continue
                kind = "duplicate_npc_spawn" if life_type == "n" else "duplicate_mob_spawn"
                counts[kind] += 1
                review_findings.append(Finding(
                    kind,
                    map_id,
                    object_id,
                    f"{amount} identical {'NPC' if life_type == 'n' else 'mob'} spawns share x={x}, y={y}",
                ))

        reactors = direct_imgdir(root, "reactor")
        if reactors is not None:
            seen_reactors: Counter[tuple[str, str, str]] = Counter()
            for node in reactors:
                if node.tag != "imgdir":
                    continue
                object_id = normalize_id(child_value(node, "id"))
                x, y = exact_xy(node)
                if object_id:
                    seen_reactors[(object_id, x, y)] += 1
            for (object_id, x, y), amount in seen_reactors.items():
                if amount <= 1:
                    continue
                counts["duplicate_reactor_spawn"] += 1
                review_findings.append(Finding(
                    "duplicate_reactor_spawn",
                    map_id,
                    object_id,
                    f"{amount} identical reactor spawns share x={x}, y={y}",
                ))

        portals = direct_imgdir(root, "portal")
        if portals is None:
            continue

        seen_portals: Counter[tuple[str, str, str]] = Counter()
        for node in portals:
            if node.tag != "imgdir":
                continue
            counts["portals"] += 1
            portal_name = (child_value(node, "pn") or node.attrib.get("name", "?")).strip()
            x, y = exact_xy(node)
            seen_portals[(portal_name, x, y)] += 1

            target_map = normalize_id(child_value(node, "tm"))
            target_name = (child_value(node, "tn") or "").strip()
            script_name = (child_value(node, "script") or "").strip()

            # Scripted/sentinel portals are validated by the existing integrity audit.
            if script_name or not target_map or target_map in SPECIAL_TARGETS or target_map not in maps:
                continue
            if not target_name:
                continue

            counts["named_static_portals"] += 1
            if target_name not in portal_names.get(target_map, set()):
                hard_findings.append(Finding(
                    "missing_target_portal",
                    map_id,
                    portal_name,
                    f"Portal {portal_name!r} targets map {target_map} portal {target_name!r}, but that portal name does not exist",
                ))

        for (portal_name, x, y), amount in seen_portals.items():
            if amount <= 1:
                continue
            counts["duplicate_portal_spawn"] += 1
            review_findings.append(Finding(
                "duplicate_portal_spawn",
                map_id,
                portal_name,
                f"{amount} identical portal records share x={x}, y={y}",
            ))

    payload = {
        "maps": len(maps),
        "counts": dict(sorted(counts.items())),
        "parseErrors": parse_errors,
        "hardFailureCount": len(hard_findings) + len(parse_errors),
        "reviewFindingCount": len(review_findings),
        "hardFindings": [asdict(f) for f in hard_findings],
        "reviewFindings": [asdict(f) for f in review_findings],
    }

    if emit_json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            "EverLeaf world link audit: "
            f"{len(maps)} maps, {counts['portals']} portals, "
            f"{counts['named_static_portals']} named static portal links"
        )
        print(
            f"Hard failures: {payload['hardFailureCount']}; "
            f"review-only findings: {payload['reviewFindingCount']}"
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
