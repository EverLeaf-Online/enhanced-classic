#!/usr/bin/env python3
"""Audit NPC spawn data in EverLeaf's server-side Map.wz XML.

Checks every map life node with type="n" for:
- missing Npc.wz asset
- missing/invalid foothold references
- reversed roaming bounds
- suspicious coordinate values
- exact duplicate NPC spawn records

Known legacy anomalies that have been independently verified against the older
v83 reference remain visible as reviewed exceptions instead of actionable
warnings.

This is intentionally read-only. It reports problems but never rewrites WZ XML.
"""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"
NPC_ROOT = ROOT / "wz" / "Npc.wz"

# Keyed by (map_id, npc_id, finding_code). These entries are intentionally very
# narrow: an exception suppresses only the exact reviewed anomaly, not other
# findings on the same map/NPC.
REVIEWED_EXCEPTIONS: dict[tuple[str, str, str], str] = {
    (
        "670010600",
        "9201045",
        "spawn_outside_roam_range",
    ): (
        "Inherited unchanged from the older Maple83 v83 reference: "
        "x=8916 with rx0=9064..rx1=9164 and fh=322. Preserve legacy/event data."
    ),
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    map_id: str
    npc_id: str
    node: str
    detail: str


@dataclass(frozen=True)
class ReviewedFinding:
    code: str
    map_id: str
    npc_id: str
    node: str
    detail: str
    review_reason: str


def child_value(node: ET.Element, name: str) -> str | None:
    for child in node:
        if child.attrib.get("name") == name:
            return child.attrib.get("value")
    return None


def int_value(node: ET.Element, name: str) -> int | None:
    value = child_value(node, name)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def direct_imgdir(root: ET.Element, name: str) -> ET.Element | None:
    for child in root:
        if child.tag == "imgdir" and child.attrib.get("name") == name:
            return child
    return None


def foothold_ids(root: ET.Element) -> set[int]:
    section = direct_imgdir(root, "foothold")
    if section is None:
        return set()

    result: set[int] = set()
    for node in section.iter("imgdir"):
        names = {child.attrib.get("name") for child in node if child.tag == "int"}
        # Actual foothold records contain endpoint coordinates. Container/group
        # imgdirs do not, so this avoids treating layer/group IDs as footholds.
        if {"x1", "y1", "x2", "y2"}.issubset(names):
            try:
                result.add(int(node.attrib["name"]))
            except (KeyError, ValueError):
                pass
    return result


def npc_asset_exists(npc_id: str) -> bool:
    try:
        normalized = f"{int(npc_id):07d}.img.xml"
    except ValueError:
        return False
    return (NPC_ROOT / normalized).is_file()


def audit_map(path: Path) -> tuple[int, list[Finding]]:
    findings: list[Finding] = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return 0, [Finding("error", "malformed_xml", path.stem.split(".")[0], "", "", str(exc))]

    map_id = path.name.split(".", 1)[0]
    life = direct_imgdir(root, "life")
    if life is None:
        return 0, findings

    footholds = foothold_ids(root)
    records: list[tuple[str, int | None, int | None, int | None, int | None, int | None, str]] = []
    npc_count = 0

    for node in life:
        if node.tag != "imgdir" or child_value(node, "type") != "n":
            continue

        npc_count += 1
        node_name = node.attrib.get("name", "?")
        npc_id = child_value(node, "id") or ""
        x = int_value(node, "x")
        y = int_value(node, "y")
        fh = int_value(node, "fh")
        rx0 = int_value(node, "rx0")
        rx1 = int_value(node, "rx1")
        hide = child_value(node, "hide") or "0"

        if not npc_id.isdigit():
            findings.append(Finding("error", "invalid_npc_id", map_id, npc_id, node_name, "NPC id is missing or non-numeric"))
        elif not npc_asset_exists(npc_id):
            findings.append(Finding("error", "missing_npc_asset", map_id, npc_id, node_name, f"wz/Npc.wz/{int(npc_id):07d}.img.xml not found"))

        if x is None or y is None:
            findings.append(Finding("error", "missing_coordinate", map_id, npc_id, node_name, "NPC requires numeric x and y coordinates"))
        elif abs(x) > 100_000 or abs(y) > 100_000:
            findings.append(Finding("warning", "extreme_coordinate", map_id, npc_id, node_name, f"suspicious position x={x}, y={y}"))

        # fh=0 is used by some special/non-grounded life nodes. A positive fh
        # should resolve to a foothold in the same map.
        if fh is not None and fh > 0 and fh not in footholds:
            findings.append(Finding("error", "missing_foothold", map_id, npc_id, node_name, f"fh={fh} does not exist in this map"))

        if rx0 is not None and rx1 is not None and rx0 > rx1:
            findings.append(Finding("error", "reversed_roam_range", map_id, npc_id, node_name, f"rx0={rx0} is greater than rx1={rx1}"))

        if x is not None and rx0 is not None and rx1 is not None and not (rx0 <= x <= rx1):
            findings.append(Finding("warning", "spawn_outside_roam_range", map_id, npc_id, node_name, f"x={x} is outside rx0={rx0}..rx1={rx1}"))

        records.append((npc_id, x, y, fh, rx0, rx1, hide))

    counts = Counter(records)
    for record, count in counts.items():
        if count > 1:
            npc_id, x, y, fh, rx0, rx1, hide = record
            findings.append(Finding(
                "warning", "duplicate_spawn", map_id, npc_id, "*",
                f"{count} identical spawns at x={x}, y={y}, fh={fh}, rx={rx0}..{rx1}, hide={hide}",
            ))

    return npc_count, findings


def split_reviewed(findings: list[Finding]) -> tuple[list[Finding], list[ReviewedFinding]]:
    actionable: list[Finding] = []
    reviewed: list[ReviewedFinding] = []
    for finding in findings:
        reason = REVIEWED_EXCEPTIONS.get((finding.map_id, finding.npc_id, finding.code))
        if reason is None:
            actionable.append(finding)
            continue
        reviewed.append(ReviewedFinding(
            code=finding.code,
            map_id=finding.map_id,
            npc_id=finding.npc_id,
            node=finding.node,
            detail=finding.detail,
            review_reason=reason,
        ))
    return actionable, reviewed


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit EverLeaf NPC map spawns")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--map", dest="map_id", help="audit one map ID only")
    args = parser.parse_args()

    if not MAP_ROOT.is_dir() or not NPC_ROOT.is_dir():
        print("Expected wz/Map.wz/Map and wz/Npc.wz under repository root", file=sys.stderr)
        return 2

    if args.map_id:
        candidates = list(MAP_ROOT.glob(f"Map*/{args.map_id}.img.xml"))
    else:
        candidates = sorted(MAP_ROOT.glob("Map*/*.img.xml"))

    total_npcs = 0
    all_findings: list[Finding] = []
    maps_with_npcs = 0
    for path in candidates:
        count, findings = audit_map(path)
        total_npcs += count
        if count:
            maps_with_npcs += 1
        all_findings.extend(findings)

    actionable, reviewed = split_reviewed(all_findings)
    errors = sum(f.severity == "error" for f in actionable)
    warnings = sum(f.severity == "warning" for f in actionable)

    if args.json:
        print(json.dumps({
            "mapsScanned": len(candidates),
            "mapsWithNpcs": maps_with_npcs,
            "npcSpawns": total_npcs,
            "errors": errors,
            "warnings": warnings,
            "reviewedExceptions": len(reviewed),
            "findings": [asdict(f) for f in actionable],
            "reviewed": [asdict(f) for f in reviewed],
        }, indent=2))
    else:
        print(f"NPC spawn audit: {len(candidates)} maps scanned, {maps_with_npcs} with NPCs, {total_npcs} NPC spawns")
        print(f"Findings: {errors} errors, {warnings} warnings; reviewed exceptions: {len(reviewed)}")
        for finding in actionable:
            print(
                f"[{finding.severity.upper()}] {finding.code}: "
                f"map={finding.map_id} npc={finding.npc_id or '-'} node={finding.node or '-'} — {finding.detail}"
            )
        for finding in reviewed:
            print(
                f"[REVIEWED] {finding.code}: "
                f"map={finding.map_id} npc={finding.npc_id or '-'} node={finding.node or '-'} — "
                f"{finding.detail} — {finding.review_reason}"
            )

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
