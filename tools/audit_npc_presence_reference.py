#!/usr/bin/env python3
"""Compare EverLeaf NPC presence per map with an older v83 reference tree.

This semantic audit detects NPC IDs that are present in one map data set but
absent (or present a different number of times) in the other. It never edits
map data. Older Maple83/HeavenMS custom NPCs are reported separately from the
small set of non-custom candidates that deserve manual review.
"""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"


@dataclass(frozen=True)
class PresenceDifference:
    map_id: str
    npc_id: str
    current_count: int
    reference_count: int
    delta: int
    kind: str
    provenance: str


def direct_imgdir(root: ET.Element, name: str) -> ET.Element | None:
    return next((child for child in root if child.tag == "imgdir" and child.attrib.get("name") == name), None)


def child_value(node: ET.Element, name: str) -> str | None:
    for child in node:
        if child.attrib.get("name") == name:
            return child.attrib.get("value")
    return None


def npc_counts(path: Path) -> Counter[str]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return Counter()
    life = direct_imgdir(root, "life")
    if life is None:
        return Counter()
    return Counter(
        child_value(node, "id") or ""
        for node in life
        if node.tag == "imgdir" and child_value(node, "type") == "n"
    )


def map_files(root: Path) -> dict[str, Path]:
    return {path.name.split(".", 1)[0]: path for path in root.glob("Map*/*.img.xml")}


def provenance(npc_id: str) -> str:
    # Maple83/HeavenMS uses the 990xxxx range heavily for source-specific custom
    # job-hall/rebirth/helper NPCs. Do not treat these as missing retail-v83 NPCs.
    return "reference_custom_990" if npc_id.startswith("990") else "review_candidate"


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare EverLeaf NPC map presence with a v83 reference")
    parser.add_argument("reference_root", type=Path, help="reference wz/Map.wz/Map directory")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    reference_root = args.reference_root.resolve()
    if not CURRENT_MAP_ROOT.is_dir():
        parser.error(f"current map root missing: {CURRENT_MAP_ROOT}")
    if not reference_root.is_dir():
        parser.error(f"reference map root missing: {reference_root}")

    current_maps = map_files(CURRENT_MAP_ROOT)
    reference_maps = map_files(reference_root)
    common_map_ids = sorted(current_maps.keys() & reference_maps.keys())

    differences: list[PresenceDifference] = []
    changed_maps: set[str] = set()
    current_total = 0
    reference_total = 0

    for map_id in common_map_ids:
        current = npc_counts(current_maps[map_id])
        reference = npc_counts(reference_maps[map_id])
        current_total += sum(current.values())
        reference_total += sum(reference.values())
        for npc_id in sorted(current.keys() | reference.keys(), key=lambda value: int(value or 0)):
            current_count = current[npc_id]
            reference_count = reference[npc_id]
            if current_count == reference_count:
                continue
            changed_maps.add(map_id)
            delta = current_count - reference_count
            if current_count == 0:
                kind = "missing_from_current"
            elif reference_count == 0:
                kind = "added_in_current"
            elif delta < 0:
                kind = "fewer_in_current"
            else:
                kind = "more_in_current"
            differences.append(PresenceDifference(
                map_id, npc_id, current_count, reference_count, delta, kind, provenance(npc_id)
            ))

    current_only_maps = sorted(current_maps.keys() - reference_maps.keys())
    reference_only_maps = sorted(reference_maps.keys() - current_maps.keys())
    missing = [d for d in differences if d.kind in {"missing_from_current", "fewer_in_current"}]
    added = [d for d in differences if d.kind in {"added_in_current", "more_in_current"}]
    custom_missing = [d for d in missing if d.provenance == "reference_custom_990"]
    review_missing = [d for d in missing if d.provenance == "review_candidate"]

    payload = {
        "currentMaps": len(current_maps),
        "referenceMaps": len(reference_maps),
        "commonMaps": len(common_map_ids),
        "currentOnlyMaps": current_only_maps,
        "referenceOnlyMaps": reference_only_maps,
        "currentNpcSpawnsOnCommonMaps": current_total,
        "referenceNpcSpawnsOnCommonMaps": reference_total,
        "mapsWithPresenceDifferences": len(changed_maps),
        "presenceDifferences": len(differences),
        "missingOrFewer": len(missing),
        "addedOrMore": len(added),
        "referenceCustomMissing": len(custom_missing),
        "nonCustomMissingReviewCandidates": len(review_missing),
        "reviewCandidates": [asdict(d) for d in review_missing],
        "differences": [asdict(d) for d in differences],
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            "NPC presence reference audit: "
            f"{len(common_map_ids)} common maps; {len(changed_maps)} maps differ; "
            f"{len(missing)} missing/fewer records; {len(added)} added/more records"
        )
        print(
            f"Missing classification: {len(custom_missing)} reference-custom 990xxxx; "
            f"{len(review_missing)} non-custom review candidates"
        )
        print(
            f"Map-set differences: {len(current_only_maps)} current-only, "
            f"{len(reference_only_maps)} reference-only"
        )
        for diff in review_missing:
            print(
                f"[REVIEW] {diff.kind} map={diff.map_id} npc={diff.npc_id} "
                f"current={diff.current_count} reference={diff.reference_count} delta={diff.delta:+d}"
            )

    # Differences are review input, not automatic CI failures; Cosmic/EverLeaf
    # legitimately diverges from Maple83 in custom/event content.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
