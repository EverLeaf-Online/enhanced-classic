#!/usr/bin/env python3
"""Profile review-first WZ item candidates for conservative v83 backports.

This tool never modifies WZ data. It narrows an existing donor import manifest
into descriptive profiles and identifies only the simplest dependency-clean
Consume items (plain HP/MP restoration) as first-batch candidates.
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

NUMERIC_ID = re.compile(r"^\d{1,10}$")
SIMPLE_RESTORE_PROPERTIES = {"hp", "mp", "hpr", "mpr"}


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
    names: set[str] = set()
    for child in list(node):
        name = child.attrib.get("name")
        if name:
            names.add(name.lower())
    return sorted(names)


def has_nested_structure(node: ET.Element | None) -> bool:
    if node is None:
        return False
    return any(child.tag == "imgdir" for child in list(node))


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


def profile_candidate(candidate: dict, donor_root: Path, strings: dict[str, dict[str, str]]) -> dict:
    content_id = str(candidate["contentId"])
    source_path = candidate["sourcePath"]
    family = item_family(source_path)
    reasons: list[str] = []
    classification = "manual-review"

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
        if candidate.get("risk") == "blocked" or missing:
            classification = "blocked"
            reasons.append("known-missing-dependency")
        elif family != "Consume":
            reasons.append(f"family-{family.lower()}-not-first-batch")
        elif spec is None:
            reasons.append("no-spec-node")
        elif has_nested_structure(spec):
            reasons.append("nested-spec-structure")
        elif not spec_props:
            reasons.append("empty-spec")
        elif not set(spec_props).issubset(SIMPLE_RESTORE_PROPERTIES):
            reasons.append("non-restore-spec:" + ",".join(spec_props))
        else:
            classification = "simple-consume"
            reasons.append("plain-hp-mp-restore-only")

    text = strings.get(content_id, {})
    if strings and not text.get("name"):
        reasons.append("missing-string-name")
        if classification == "simple-consume":
            classification = "manual-review"

    return {
        "contentId": content_id,
        "sourcePath": source_path,
        "family": family,
        "manifestRisk": candidate.get("risk"),
        "classification": classification,
        "name": text.get("name"),
        "description": text.get("desc"),
        "infoProperties": info_props,
        "specProperties": spec_props,
        "reasons": reasons,
        "approved": False,
    }


def build_profiles(manifest: dict, donor_root: Path, string_root: Path | None = None) -> dict:
    strings = build_string_index(string_root)
    profiles = [
        profile_candidate(candidate, donor_root, strings)
        for candidate in manifest.get("candidates", [])
        if candidate.get("category") == "items"
    ]
    profiles.sort(key=lambda p: int(p["contentId"]))
    counts = Counter(profile["classification"] for profile in profiles)
    family_counts = Counter(profile["family"] for profile in profiles)
    return {
        "schemaVersion": 1,
        "donorId": manifest.get("donorId"),
        "mode": "review-only",
        "automaticImport": False,
        "stringIndexLoaded": bool(strings),
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
    parser.add_argument("--output", type=Path, default=Path("tools/output/wz-item-profiles.json"))
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    report = build_profiles(manifest, args.donor, args.strings)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Item candidates: {report['itemCandidateCount']}")
    print("Classifications: " + ", ".join(f"{k}={v}" for k, v in report["classificationCounts"].items()))
    print(f"String index loaded: {report['stringIndexLoaded']}")
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
