#!/usr/bin/env python3
"""Profile review-first WZ item candidates for conservative v83 backports.

This tool never modifies WZ data. It narrows an existing donor import manifest
into descriptive profiles and identifies only the simplest dependency-clean
Consume items (plain positive HP/MP restoration) as first-batch candidates.
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

NUMERIC_ID = re.compile(r"^\d{1,10}$")
SIMPLE_RESTORE_PROPERTIES = {"hp", "mp", "hpr", "mpr"}
ITEM_FAMILIES = {"Cash", "Consume", "Etc", "Install", "Pet", "Special"}
FIRST_BATCH_BLOCKING_INFO = {
    "cash",
    "quest",
    "tradeblock",
    "notsale",
    "only",
    "expireonlogout",
    "accountsharable",
}


def canonical_id(value: str | None) -> str | None:
    if not value or not NUMERIC_ID.fullmatch(value):
        return None
    return str(int(value))


def item_family(relative_path: str) -> str:
    parts = Path(relative_path).parts
    if len(parts) >= 3 and parts[0] == "Item.wz":
        return parts[1]
    return "unknown"


def find_item_node(path: Path, content_id: str) -> ET.Element | None:
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return None

    target = canonical_id(content_id)
    for child in list(root):
        if child.tag == "imgdir" and canonical_id(child.attrib.get("name")) == target:
            return child

    root_name = root.attrib.get("name", "")
    if root_name.endswith(".img"):
        root_name = root_name[:-4]
    if canonical_id(root_name) == target:
        return root
    return None


def named_child(node: ET.Element, name: str) -> ET.Element | None:
    for child in list(node):
        if child.tag == "imgdir" and child.attrib.get("name", "").lower() == name.lower():
            return child
    return None


def property_names(node: ET.Element | None) -> list[str]:
    if node is None:
        return []
    return sorted({child.attrib["name"].lower() for child in list(node) if child.attrib.get("name")})


def scalar_properties(node: ET.Element | None) -> dict[str, str]:
    """Return direct scalar properties only; nested structures are excluded."""
    if node is None:
        return {}
    values: dict[str, str] = {}
    for child in list(node):
        if child.tag == "imgdir":
            continue
        name = child.attrib.get("name")
        value = child.attrib.get("value")
        if name and value is not None:
            values[name.lower()] = value
    return values


def has_nested_structure(node: ET.Element | None) -> bool:
    if node is None:
        return False
    return any(child.tag == "imgdir" for child in list(node))


def positive_restore_values(spec: ET.Element | None) -> tuple[bool, dict[str, float]]:
    values = scalar_properties(spec)
    parsed: dict[str, float] = {}
    for name, raw in values.items():
        if name not in SIMPLE_RESTORE_PROPERTIES:
            continue
        try:
            number = float(raw)
        except ValueError:
            return False, {}
        if number <= 0:
            return False, {**parsed, name: number}
        parsed[name] = number
    return bool(parsed), parsed


def build_string_index(string_root: Path | None) -> dict[str, dict[str, str]]:
    """Index numeric String.wz nodes that directly expose name/desc strings."""
    if string_root is None or not string_root.exists():
        return {}

    index: dict[str, dict[str, str]] = {}
    for path in string_root.rglob("*.xml"):
        try:
            root = ET.parse(path).getroot()
        except (ET.ParseError, OSError):
            continue
        for node in root.iter("imgdir"):
            content_id = canonical_id(node.attrib.get("name"))
            if content_id is None:
                continue
            text: dict[str, str] = {}
            for child in list(node):
                if child.tag != "string":
                    continue
                key = child.attrib.get("name", "").lower()
                if key in {"name", "desc"}:
                    text[key] = child.attrib.get("value", "")
            if "name" in text:
                index.setdefault(content_id, text)
    return index


def iter_item_nodes(item_root: Path):
    """Yield (content_id, node) for real Item.wz families only."""
    for family in sorted(ITEM_FAMILIES):
        family_root = item_root / family
        if not family_root.exists():
            continue
        for path in family_root.rglob("*.xml"):
            try:
                root = ET.parse(path).getroot()
            except (ET.ParseError, OSError):
                continue
            found_child = False
            for child in list(root):
                if child.tag != "imgdir":
                    continue
                content_id = canonical_id(child.attrib.get("name"))
                if content_id is None:
                    continue
                found_child = True
                yield content_id, child
            if found_child:
                continue
            root_name = root.attrib.get("name", "")
            if root_name.endswith(".img"):
                root_name = root_name[:-4]
            content_id = canonical_id(root_name)
            if content_id is not None:
                yield content_id, root


def restore_signature(node: ET.Element) -> tuple[tuple[str, float], ...] | None:
    spec = named_child(node, "spec")
    if spec is None or has_nested_structure(spec):
        return None
    props = property_names(spec)
    if not props or not set(props).issubset(SIMPLE_RESTORE_PROPERTIES):
        return None
    valid, values = positive_restore_values(spec)
    if not valid or set(values) != set(props):
        return None
    return tuple(sorted(values.items()))


def build_baseline_restore_index(
    baseline_root: Path | None,
) -> dict[tuple[str, tuple[tuple[str, float], ...]], list[str]]:
    """Index classic v83 restore items by normalized name + exact restore behavior."""
    if baseline_root is None or not baseline_root.exists():
        return {}
    strings = build_string_index(baseline_root / "String.wz")
    matches: dict[tuple[str, tuple[tuple[str, float], ...]], list[str]] = defaultdict(list)
    for content_id, node in iter_item_nodes(baseline_root / "Item.wz"):
        name = strings.get(content_id, {}).get("name", "").strip().casefold()
        signature = restore_signature(node)
        if not name or signature is None:
            continue
        matches[(name, signature)].append(content_id)
    return dict(matches)


def profile_candidate(
    candidate: dict,
    donor_root: Path,
    strings: dict[str, dict[str, str]],
    baseline_restore_index: dict[tuple[str, tuple[tuple[str, float], ...]], list[str]],
) -> dict:
    content_id = str(candidate["contentId"])
    source_path = candidate["sourcePath"]
    family = item_family(source_path)
    reasons: list[str] = []
    classification = "manual-review"
    restore_values: dict[str, float] = {}
    duplicate_of: list[str] = []

    node = find_item_node(donor_root / source_path, content_id)
    if node is None:
        reasons.append("item-node-not-found")
        info_props: list[str] = []
        spec_props: list[str] = []
    else:
        info = named_child(node, "info")
        spec = named_child(node, "spec")
        info_props = property_names(info)
        spec_props = property_names(spec)

        missing = candidate.get("missingDependencies") or []
        blocking_info = sorted(set(info_props) & FIRST_BATCH_BLOCKING_INFO)
        if candidate.get("risk") == "blocked" or missing:
            classification = "blocked"
            reasons.append("known-missing-dependency")
        elif family != "Consume":
            reasons.append(f"family-{family.lower()}-not-first-batch")
        elif blocking_info:
            reasons.append("special-info-flags:" + ",".join(blocking_info))
        elif spec is None:
            reasons.append("no-spec-node")
        elif has_nested_structure(spec):
            reasons.append("nested-spec-structure")
        elif not spec_props:
            reasons.append("empty-spec")
        elif not set(spec_props).issubset(SIMPLE_RESTORE_PROPERTIES):
            reasons.append("non-restore-spec:" + ",".join(spec_props))
        else:
            values_valid, restore_values = positive_restore_values(spec)
            if not values_valid or set(restore_values) != set(spec_props):
                reasons.append("non-positive-or-invalid-restore-value")
            else:
                classification = "simple-consume"
                reasons.append("plain-positive-hp-mp-restore-only")

    text = strings.get(content_id, {})
    name = text.get("name")
    if strings and not name:
        reasons.append("missing-string-name")
        if classification == "simple-consume":
            classification = "manual-review"

    if classification == "simple-consume" and name and baseline_restore_index:
        signature = tuple(sorted(restore_values.items()))
        duplicate_of = baseline_restore_index.get((name.strip().casefold(), signature), [])
        if duplicate_of:
            classification = "semantic-duplicate"
            reasons.append("matches-v83-item:" + ",".join(duplicate_of))

    return {
        "contentId": content_id,
        "sourcePath": source_path,
        "family": family,
        "manifestRisk": candidate.get("risk"),
        "classification": classification,
        "name": name,
        "description": text.get("desc"),
        "infoProperties": info_props,
        "specProperties": spec_props,
        "restoreValues": restore_values,
        "duplicateOf": duplicate_of,
        "reasons": reasons,
        "approved": False,
    }


def build_profiles(
    manifest: dict,
    donor_root: Path,
    string_root: Path | None = None,
    baseline_root: Path | None = None,
) -> dict:
    strings = build_string_index(string_root)
    baseline_restore_index = build_baseline_restore_index(baseline_root)
    profiles = [
        profile_candidate(candidate, donor_root, strings, baseline_restore_index)
        for candidate in manifest.get("candidates", [])
        if candidate.get("category") == "items"
    ]
    profiles.sort(key=lambda p: int(p["contentId"]))
    counts = Counter(profile["classification"] for profile in profiles)
    family_counts = Counter(profile["family"] for profile in profiles)
    return {
        "schemaVersion": 2,
        "donorId": manifest.get("donorId"),
        "mode": "review-only",
        "automaticImport": False,
        "stringIndexLoaded": bool(strings),
        "baselineDuplicateIndexLoaded": bool(baseline_restore_index),
        "itemCandidateCount": len(profiles),
        "classificationCounts": dict(sorted(counts.items())),
        "familyCounts": dict(sorted(family_counts.items())),
        "profiles": profiles,
        "approvalRule": "Profiler classifications are review hints only; every profile remains approved=false.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Profile donor item candidates for conservative v83 backport review.")
    parser.add_argument("manifest", type=Path, help="Import manifest produced by build_import_manifest.py")
    parser.add_argument("--donor", type=Path, required=True, help="Extracted donor XML root containing Item.wz")
    parser.add_argument("--strings", type=Path, help="Optional extracted String.wz donor root")
    parser.add_argument("--baseline", type=Path, help="Optional canonical v83 WZ root for semantic duplicate detection")
    parser.add_argument("--output", type=Path, default=Path("tools/output/wz-item-profiles.json"))
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    report = build_profiles(manifest, args.donor, args.strings, args.baseline)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Item candidates: {report['itemCandidateCount']}")
    print("Classifications: " + ", ".join(f"{k}={v}" for k, v in report["classificationCounts"].items()))
    print(f"String index loaded: {report['stringIndexLoaded']}")
    print(f"Baseline duplicate index loaded: {report['baselineDuplicateIndexLoaded']}")
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
