#!/usr/bin/env python3
"""
EverLeaf v180 missing String.wz classifier.

Adapted from the user-supplied classifier to match EverLeaf's actual
WzComparerR2 XML layout and directory-based exports.

Key properties:
- accepts one XML file OR a directory tree of *.xml files
- only treats the first >=5-digit imgdir on a branch as an ID
  (so nested option/0, option/1 etc. are never false item IDs)
- preserves leading-zero IDs as strings
- recursively handles String.wz wrappers such as Etc.img -> Etc -> ID
- can read ITEM_MANIFEST.json directly for the canonical missing-ID list
- records category and a richer structural signature for cross-version checks
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class WzNode:
    node_id: str
    category: str = ""
    source_file: str = ""
    has_icon: bool = False
    immediate_children: set[str] = field(default_factory=set)
    info_values: dict[str, str] = field(default_factory=dict)


STRUCTURE_FIELDS = (
    "price", "slotMax", "reqLevel", "reqJob", "cash", "tradeBlock",
    "notSale", "timeLimited", "only", "quest", "accountSharable",
)


def xml_files(path: str) -> list[Path]:
    p = Path(path)
    if p.is_file():
        return [p]
    if not p.is_dir():
        raise FileNotFoundError(path)
    return sorted(x for x in p.rglob("*.xml") if x.is_file())


def infer_category(xml_path: Path, root_path: str) -> str:
    root = Path(root_path)
    try:
        rel = xml_path.relative_to(root)
    except ValueError:
        rel = xml_path
    parts = rel.parts
    if len(parts) > 1:
        return parts[0]
    stem = xml_path.name.lower()
    for cat in ("cash", "consume", "etc", "install", "special", "pet"):
        if cat in stem:
            return cat.capitalize()
    return ""


def canonical_numeric_id(value: str) -> str:
    """Normalize WZ numeric folder names for manifest lookup while preserving zero itself.

    WzComparerR2 often emits 8-digit, zero-padded item folders such as 03060000,
    while ITEM_MANIFEST.json stores the same ID as integer 3060000.
    """
    stripped = value.lstrip("0")
    return stripped or "0"


def _subtree_has_icon(elem: ET.Element) -> bool:
    for child in elem.iter():
        tag = child.tag.lower()
        name = (child.get("name") or "").lower()
        if tag == "canvas" and name in ("icon", "iconraw"):
            return True
        if tag == "canvas" and "icon" in name:
            return True
    return False


def _extract_info_values(item_elem: ET.Element) -> dict[str, str]:
    result: dict[str, str] = {}
    info = None
    for child in item_elem:
        if child.tag.lower() == "imgdir" and (child.get("name") or "").lower() == "info":
            info = child
            break
    if info is None:
        return result
    wanted = {x.lower(): x for x in STRUCTURE_FIELDS}
    for child in info:
        name = child.get("name") or ""
        canonical = wanted.get(name.lower())
        if canonical and "value" in child.attrib:
            result[canonical] = child.get("value", "")
    return result


def load_xml_item_dump(path: str) -> dict[str, WzNode]:
    nodes: dict[str, WzNode] = {}
    files = xml_files(path)

    def walk(elem: ET.Element, category: str, source_file: str) -> None:
        for child in elem:
            if child.tag.lower() != "imgdir":
                continue
            name = child.get("name", "")
            if name.isdigit() and len(name) >= 5:
                # First plausible numeric ID on this branch. Do not descend
                # further for ID detection: option/0 etc. belong to this ID.
                item_id = canonical_numeric_id(name)
                node = WzNode(
                    node_id=item_id,
                    category=category,
                    source_file=source_file,
                    has_icon=_subtree_has_icon(child),
                    immediate_children={
                        (x.get("name") or "") for x in child
                        if (x.get("name") or "")
                    },
                    info_values=_extract_info_values(child),
                )
                nodes[item_id] = node
            else:
                walk(child, category, source_file)

    for f in files:
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError as exc:
            raise RuntimeError(f"Malformed XML: {f}: {exc}") from exc
        walk(root, infer_category(f, path), str(f))
    return nodes


def load_xml_string_dump(path: str) -> dict[str, dict[str, str]]:
    strings: dict[str, dict[str, str]] = {}

    def walk(elem: ET.Element) -> None:
        for child in elem:
            if child.tag.lower() != "imgdir":
                continue
            name = child.get("name", "")
            if name.isdigit() and len(name) >= 5:
                entry = {"name": "", "desc": ""}
                for sub in child:
                    if sub.tag.lower() != "string":
                        continue
                    sub_name = (sub.get("name") or "").lower()
                    if sub_name == "name":
                        entry["name"] = sub.get("value", "")
                    elif sub_name in ("desc", "description"):
                        entry["desc"] = sub.get("value", "")
                # Keep entries even when name is empty; presence itself is useful.
                strings[canonical_numeric_id(name)] = entry
            else:
                walk(child)

    for f in xml_files(path):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError as exc:
            raise RuntimeError(f"Malformed XML: {f}: {exc}") from exc
        walk(root)
    return strings


def load_manifest_ids(path: str) -> tuple[list[str], dict[str, str]]:
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    rows = data.get("missingStringItems")
    if not isinstance(rows, list):
        raise ValueError(f"{path} does not contain missingStringItems[]")
    ids: list[str] = []
    categories: dict[str, str] = {}
    for row in rows:
        if isinstance(row, dict):
            value = row.get("Id", row.get("id"))
            category = str(row.get("Category", row.get("category", "")))
        else:
            value = row
            category = ""
        if value is None:
            continue
        item_id = str(value).strip()
        if item_id:
            ids.append(item_id)
            if category:
                categories[item_id] = category
    return ids, categories


def structures_match(target: WzNode | None, older: WzNode | None) -> bool:
    if target is None or older is None:
        return False
    if target.has_icon != older.has_icon:
        return False

    # Only compare fields present on both versions. A field newly introduced
    # in v180 should not by itself imply that the ID was repurposed.
    shared = set(target.info_values) & set(older.info_values)
    if any(target.info_values[k] != older.info_values[k] for k in shared):
        return False

    # Require at least some shape continuity when both sides expose children.
    if target.immediate_children and older.immediate_children:
        a, b = target.immediate_children, older.immediate_children
        overlap = len(a & b) / max(1, min(len(a), len(b)))
        if overlap < 0.5:
            return False
    return True


def classify(
    item_id: str,
    target_items: dict[str, WzNode],
    older_items: dict[str, WzNode],
    target_strings: dict[str, dict[str, str]],
    older_strings: dict[str, dict[str, str]],
) -> tuple[str, str]:
    target = target_items.get(item_id)
    older = older_items.get(item_id)
    target_string = target_strings.get(item_id)
    older_string = older_strings.get(item_id)

    # This is a guard against stale/bad missing lists and catches exactly the
    # nested-String lookup class of bug we hit earlier.
    if target_string and target_string.get("name"):
        return "string_present_not_missing", "high"

    older_has_name = bool(older_string and older_string.get("name"))
    if older is not None and older_has_name:
        if structures_match(target, older):
            return "moved_or_renamed", "high"
        return "possibly_repurposed_id", "medium"

    if target is not None and target.has_icon:
        return "recoverable_player_facing", "medium-high"

    if target is not None:
        return "legitimately_internal", "medium"

    return "unclassified", "low"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-string", required=True, help="v180 String.wz XML file or directory")
    ap.add_argument("--donor-string", required=True, help="older/current String.wz XML file or directory")
    ap.add_argument("--target-item", required=True, help="v180 Item.wz XML file or directory")
    ap.add_argument("--donor-item", required=True, help="older/current Item.wz XML file or directory")
    source = ap.add_mutually_exclusive_group()
    source.add_argument("--ids-file")
    source.add_argument("--manifest-json", help="ITEM_MANIFEST.json containing missingStringItems[]")
    ap.add_argument("--output", default="classification.csv")
    ap.add_argument("--summary-json")
    args = ap.parse_args()

    print("Loading v180 item XML...", file=sys.stderr)
    target_items = load_xml_item_dump(args.target_item)
    print("Loading older/current item XML...", file=sys.stderr)
    older_items = load_xml_item_dump(args.donor_item)
    print("Loading v180 string XML...", file=sys.stderr)
    target_strings = load_xml_string_dump(args.target_string)
    print("Loading older/current string XML...", file=sys.stderr)
    older_strings = load_xml_string_dump(args.donor_string)

    manifest_categories: dict[str, str] = {}
    if args.manifest_json:
        missing_ids, manifest_categories = load_manifest_ids(args.manifest_json)
    elif args.ids_file:
        missing_ids = [x.strip() for x in Path(args.ids_file).read_text(encoding="utf-8-sig").splitlines() if x.strip()]
    else:
        missing_ids = [i for i in target_items if not target_strings.get(i, {}).get("name")]

    rows = []
    for item_id in missing_ids:
        target = target_items.get(item_id)
        older = older_items.get(item_id)
        classification, confidence = classify(
            item_id, target_items, older_items, target_strings, older_strings
        )
        rows.append({
            "ID": item_id,
            "Category": manifest_categories.get(item_id) or (target.category if target else ""),
            "HasIcon": "" if target is None else target.has_icon,
            "ExistsInOlderItem": older is not None,
            "OlderHasName": bool(older_strings.get(item_id, {}).get("name")),
            "StructureMatch": "" if older is None else structures_match(target, older),
            "V180StringPresent": bool(target_strings.get(item_id, {}).get("name")),
            "Classification": classification,
            "Confidence": confidence,
            "SourceFile": target.source_file if target else "",
        })

    fields = [
        "ID", "Category", "HasIcon", "ExistsInOlderItem", "OlderHasName",
        "StructureMatch", "V180StringPresent", "Classification", "Confidence",
        "SourceFile",
    ]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    counts = Counter(r["Classification"] for r in rows)
    categories = Counter(r["Category"] for r in rows)
    lengths = Counter(len(str(r["ID"])) for r in rows)
    summary = {
        "inputCount": len(missing_ids),
        "outputCount": len(rows),
        "idLengths": dict(sorted(lengths.items())),
        "classificationCounts": dict(counts.most_common()),
        "categoryCounts": dict(categories.most_common()),
        "targetItemIdsParsed": len(target_items),
        "olderItemIdsParsed": len(older_items),
        "targetStringIdsParsed": len(target_strings),
        "olderStringIdsParsed": len(older_strings),
        "targetItemsMissingFromParsedXml": sum(1 for i in missing_ids if i not in target_items),
        "staleMissingIdsWithV180Name": sum(1 for i in missing_ids if target_strings.get(i, {}).get("name")),
    }
    if args.summary_json:
        Path(args.summary_json).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2), file=sys.stderr)
    print(f"Wrote {len(rows)} rows to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
