#!/usr/bin/env python3
"""EverLeaf WZ donor inventory/diff helper.

This tool compares exported WZ XML trees. It is intentionally conservative:
it does not modify the canonical v83 tree and it never assumes a newer donor
can be copied wholesale into a v83 client/server.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

NUMERIC_STEM = re.compile(r"^(\d{4,10})(?:\.img)?$")
ID_VALUE = re.compile(r"^\d{4,10}$")

CATEGORY_ROOTS = {
    "maps": ("Map.wz",),
    "mobs": ("Mob.wz",),
    "npcs": ("Npc.wz",),
    "items": ("Item.wz",),
    "equipment": ("Character.wz",),
    "reactors": ("Reactor.wz",),
    "quests": ("Quest.wz",),
    "skills": ("Skill.wz",),
}


@dataclass(frozen=True)
class Entry:
    category: str
    content_id: str
    relative_path: str
    sha256: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_stem(path: Path) -> str | None:
    name = path.name
    if name.endswith(".xml"):
        name = name[:-4]
    match = NUMERIC_STEM.match(name)
    return match.group(1) if match else None


def first_level_numeric_ids(path: Path) -> set[str]:
    """Collect direct-ish WZ IDs without recursively harvesting animation indexes.

    This is mainly for consolidated files such as Quest.wz and Skill.wz where
    the content ID is often represented by an imgdir node instead of a file.
    We cap traversal depth to reduce false positives from frame/level indexes.
    """
    found: set[str] = set()
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return found

    frontier = [(root, 0)]
    while frontier:
        node, depth = frontier.pop()
        if depth > 4:
            continue
        name = node.attrib.get("name")
        if name and ID_VALUE.match(name):
            found.add(name)
        if depth < 4:
            frontier.extend((child, depth + 1) for child in list(node))
    return found


def iter_xml(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    return root.rglob("*.xml")


def inventory(tree: Path) -> dict[str, dict[str, Entry]]:
    result: dict[str, dict[str, Entry]] = {category: {} for category in CATEGORY_ROOTS}

    for category, roots in CATEGORY_ROOTS.items():
        for wz_root in roots:
            base = tree / wz_root
            for xml_path in iter_xml(base):
                rel = xml_path.relative_to(tree).as_posix()
                file_id = normalize_stem(xml_path)
                digest = sha256_file(xml_path)
                if file_id:
                    result[category].setdefault(
                        file_id,
                        Entry(category, file_id, rel, digest),
                    )

                if category in {"quests", "skills"}:
                    for nested_id in first_level_numeric_ids(xml_path):
                        result[category].setdefault(
                            nested_id,
                            Entry(category, nested_id, rel, digest),
                        )
    return result


def compare(baseline: dict[str, dict[str, Entry]], donor: dict[str, dict[str, Entry]]) -> dict:
    report: dict[str, object] = {"categories": {}}
    totals = {"baseline": 0, "donor": 0, "new": 0, "collisions": 0, "changed": 0}

    for category in CATEGORY_ROOTS:
        base_entries = baseline[category]
        donor_entries = donor[category]
        base_ids = set(base_entries)
        donor_ids = set(donor_entries)
        new_ids = sorted(donor_ids - base_ids, key=int)
        collisions = sorted(donor_ids & base_ids, key=int)
        changed = [
            content_id
            for content_id in collisions
            if donor_entries[content_id].sha256 != base_entries[content_id].sha256
        ]

        report["categories"][category] = {
            "baselineCount": len(base_ids),
            "donorCount": len(donor_ids),
            "newIds": new_ids,
            "collisionIds": collisions,
            "changedCollisionIds": changed,
            "newEntries": [asdict(donor_entries[i]) for i in new_ids],
        }

        totals["baseline"] += len(base_ids)
        totals["donor"] += len(donor_ids)
        totals["new"] += len(new_ids)
        totals["collisions"] += len(collisions)
        totals["changed"] += len(changed)

    report["totals"] = totals
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare a donor WZ XML export against EverLeaf v83.")
    parser.add_argument("--baseline", type=Path, default=Path("wz"), help="Canonical v83 exported WZ tree")
    parser.add_argument("--donor", type=Path, required=True, help="Donor exported WZ XML tree")
    parser.add_argument("--output", type=Path, default=Path("tools/output/wz-donor-diff.json"))
    parser.add_argument("--donor-id", default="unknown-donor")
    args = parser.parse_args()

    if not args.baseline.exists():
        parser.error(f"baseline does not exist: {args.baseline}")
    if not args.donor.exists():
        parser.error(f"donor does not exist: {args.donor}")

    baseline = inventory(args.baseline)
    donor = inventory(args.donor)
    report = compare(baseline, donor)
    report["baseline"] = str(args.baseline)
    report["donor"] = str(args.donor)
    report["donorId"] = args.donor_id
    report["safety"] = {
        "mode": "read-only-diff",
        "automaticImport": False,
        "warning": "Newer WZ content is donor material only. Review dependencies and v83 compatibility before import."
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    totals = report["totals"]
    print(f"Donor: {args.donor_id}")
    print(f"New IDs: {totals['new']}")
    print(f"Collisions: {totals['collisions']} ({totals['changed']} content-different)")
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
