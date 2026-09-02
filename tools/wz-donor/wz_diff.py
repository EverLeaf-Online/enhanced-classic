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
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

NUMERIC_STEM = re.compile(r"^(\d{4,10})(?:\.img)?$")
ID_VALUE = re.compile(r"^\d{1,10}$")

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

# Conservative property names whose values are unambiguous enough to treat as
# cross-content references. Ambiguous generic fields such as `id` are handled
# only in known structural contexts below.
DIRECT_REFERENCE_NAMES = {
    "map": "maps",
    "mapid": "maps",
    "targetmap": "maps",
    "returnmap": "maps",
    "forcedreturn": "maps",
    "mob": "mobs",
    "mobid": "mobs",
    "npc": "npcs",
    "npcid": "npcs",
    "item": "items",
    "itemid": "items",
    "reactor": "reactors",
    "reactorid": "reactors",
    "skill": "skills",
    "skillid": "skills",
}


@dataclass(frozen=True)
class Entry:
    category: str
    content_id: str
    relative_path: str
    sha256: str


@dataclass(frozen=True)
class Reference:
    source_category: str
    source_id: str
    target_category: str
    target_id: str
    property_name: str
    relative_path: str


def canonical_id(value: str | None) -> str | None:
    """Normalize numeric WZ IDs to the integer form used by server references."""
    if not value or not ID_VALUE.match(value):
        return None
    return str(int(value))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _semantic_element(node: ET.Element) -> tuple:
    """Return a stable XML representation that ignores formatting whitespace."""
    text = (node.text or "").strip()
    return (
        node.tag,
        tuple(sorted(node.attrib.items())),
        text,
        tuple(_semantic_element(child) for child in list(node)),
    )


def sha256_element(node: ET.Element) -> str:
    payload = json.dumps(_semantic_element(node), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_stem(path: Path) -> str | None:
    name = path.name
    if name.endswith(".xml"):
        name = name[:-4]
    match = NUMERIC_STEM.match(name)
    return canonical_id(match.group(1)) if match else None


def first_level_numeric_ids(path: Path) -> set[str]:
    """Collect direct-ish WZ IDs without harvesting animation/frame indexes."""
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
        content_id = canonical_id(node.attrib.get("name"))
        if content_id:
            found.add(content_id)
        if depth < 4:
            frontier.extend((child, depth + 1) for child in list(node))
    return found


def item_entries(path: Path, relative_path: str) -> list[Entry]:
    """Inventory real Item.wz IDs rather than grouped container filenames.

    Classic Item.wz families such as Consume/Install/Etc/Cash group many actual
    items under files like ``0200.img.xml``. Their direct child imgdirs are the
    real item IDs. Pet files are generally one item per file and therefore fall
    back to the filename ID when no numeric direct children exist.
    """
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return []

    nested: list[Entry] = []
    for child in list(root):
        if child.tag != "imgdir":
            continue
        content_id = canonical_id(child.attrib.get("name"))
        if not content_id:
            continue
        nested.append(Entry("items", content_id, relative_path, sha256_element(child)))

    if nested:
        return nested

    file_id = normalize_stem(path)
    if file_id:
        return [Entry("items", file_id, relative_path, sha256_file(path))]
    return []


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

                if category == "items":
                    for entry in item_entries(xml_path, rel):
                        result[category].setdefault(entry.content_id, entry)
                    continue

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


def _add_reference(
    output: set[Reference],
    source_category: str,
    source_id: str,
    target_category: str,
    target_id: str | None,
    property_name: str,
    relative_path: str,
) -> None:
    normalized_target = canonical_id(target_id)
    if normalized_target is not None:
        output.add(
            Reference(
                source_category,
                source_id,
                target_category,
                normalized_target,
                property_name,
                relative_path,
            )
        )


def _scope_entry_root(root: ET.Element, entry: Entry) -> ET.Element:
    """Limit grouped Item.wz dependency scanning to the selected item node."""
    if entry.category != "items":
        return root
    for child in list(root):
        if child.tag != "imgdir":
            continue
        if canonical_id(child.attrib.get("name")) == entry.content_id:
            return child
    return root


def references_for_entry(tree: Path, entry: Entry) -> set[Reference]:
    """Extract high-confidence cross-content references from one donor entry.

    This deliberately under-reports rather than guessing. It recognizes common
    direct reference property names plus v83-style map portal/life structures.
    """
    path = tree / entry.relative_path
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return set()

    root = _scope_entry_root(root, entry)
    refs: set[Reference] = set()

    for node in root.iter():
        name = node.attrib.get("name", "").lower()
        value = node.attrib.get("value")
        target_category = DIRECT_REFERENCE_NAMES.get(name)
        if target_category:
            _add_reference(
                refs,
                entry.category,
                entry.content_id,
                target_category,
                value,
                name,
                entry.relative_path,
            )

    if entry.category == "maps":
        for parent in root.iter("imgdir"):
            parent_name = parent.attrib.get("name", "").lower()

            if parent_name == "portal":
                for portal in parent.findall("imgdir"):
                    for node in portal:
                        if node.attrib.get("name", "").lower() == "tm":
                            _add_reference(
                                refs,
                                entry.category,
                                entry.content_id,
                                "maps",
                                node.attrib.get("value"),
                                "portal.tm",
                                entry.relative_path,
                            )

            if parent_name == "life":
                for life in parent.findall("imgdir"):
                    values = {
                        child.attrib.get("name", "").lower(): child.attrib.get("value")
                        for child in life
                    }
                    life_type = values.get("type")
                    target = {"m": "mobs", "n": "npcs", "r": "reactors"}.get(life_type or "")
                    if target:
                        _add_reference(
                            refs,
                            entry.category,
                            entry.content_id,
                            target,
                            values.get("id"),
                            f"life.{life_type}.id",
                            entry.relative_path,
                        )

    return refs


def analyze_dependencies(
    donor_tree: Path,
    baseline: dict[str, dict[str, Entry]],
    donor: dict[str, dict[str, Entry]],
) -> dict:
    available = {
        category: set(baseline[category]) | set(donor[category])
        for category in CATEGORY_ROOTS
    }

    references: set[Reference] = set()
    for category in CATEGORY_ROOTS:
        new_ids = set(donor[category]) - set(baseline[category])
        for content_id in new_ids:
            references.update(references_for_entry(donor_tree, donor[category][content_id]))

    ordered = sorted(
        references,
        key=lambda ref: (
            ref.source_category,
            int(ref.source_id),
            ref.target_category,
            int(ref.target_id),
            ref.property_name,
        ),
    )
    missing = [ref for ref in ordered if ref.target_id not in available[ref.target_category]]

    by_source: dict[str, list[dict]] = {}
    for ref in missing:
        key = f"{ref.source_category}:{ref.source_id}"
        by_source.setdefault(key, []).append(asdict(ref))

    return {
        "referenceCount": len(ordered),
        "missingReferenceCount": len(missing),
        "references": [asdict(ref) for ref in ordered],
        "missingReferences": [asdict(ref) for ref in missing],
        "missingBySource": by_source,
        "scope": "high-confidence references from donor-new entries only; absence from this report does not prove dependency completeness",
    }


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
    parser.add_argument(
        "--skip-dependencies",
        action="store_true",
        help="Skip conservative cross-content reference analysis",
    )
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
    if not args.skip_dependencies:
        report["dependencies"] = analyze_dependencies(args.donor, baseline, donor)
    report["safety"] = {
        "mode": "read-only-diff",
        "automaticImport": False,
        "warning": "Newer WZ content is donor material only. Review dependencies and v83 compatibility before import.",
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    totals = report["totals"]
    print(f"Donor: {args.donor_id}")
    print(f"New IDs: {totals['new']}")
    print(f"Collisions: {totals['collisions']} ({totals['changed']} content-different)")
    if "dependencies" in report:
        deps = report["dependencies"]
        print(f"High-confidence references: {deps['referenceCount']}")
        print(f"Missing references: {deps['missingReferenceCount']}")
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
