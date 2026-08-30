#!/usr/bin/env python3
"""Audit Map.wz portal-script references for Linux filename case safety.

A Windows checkout can hide filename-case mistakes that break on the Linux game
server. This audit fails only when a referenced script has a case-insensitive
match but not the exact filename Map.wz requests. Completely missing scripts
remain review-only in the broader world audit until their content is triaged.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"
PORTAL_ROOT = ROOT / "scripts" / "portal"


def child_value(node: ET.Element, name: str) -> str | None:
    for child in node:
        if child.attrib.get("name") == name:
            return child.attrib.get("value")
    return None


def direct_imgdir(root: ET.Element, name: str) -> ET.Element | None:
    for child in root:
        if child.tag == "imgdir" and child.attrib.get("name") == name:
            return child
    return None


def main() -> int:
    portal_files = {path.name: path for path in PORTAL_ROOT.glob("*.js")}
    lower_index: dict[str, list[str]] = {}
    for name in portal_files:
        lower_index.setdefault(name.lower(), []).append(name)

    mismatches: set[tuple[str, str, str, tuple[str, ...]]] = set()
    referenced = 0

    for path in MAP_ROOT.glob("Map*/*.img.xml"):
        try:
            root = ET.parse(path).getroot()
        except (ET.ParseError, OSError):
            continue
        portals = direct_imgdir(root, "portal")
        if portals is None:
            continue
        map_id = path.name.split(".", 1)[0]
        for node in portals:
            if node.tag != "imgdir":
                continue
            script = (child_value(node, "script") or "").strip()
            if not script:
                continue
            referenced += 1
            expected = f"{script}.js"
            if expected in portal_files:
                continue
            candidates = tuple(sorted(lower_index.get(expected.lower(), [])))
            if candidates:
                portal_name = child_value(node, "pn") or node.attrib.get("name", "?")
                mismatches.add((map_id, portal_name, expected, candidates))

    print(f"EverLeaf portal filename-case audit: {referenced} scripted portal refs; case mismatches={len(mismatches)}")
    for map_id, portal_name, expected, candidates in sorted(mismatches):
        print(
            f"[FAIL] map={map_id} portal={portal_name!r} expects {expected!r}, "
            f"but repository has case variant(s): {', '.join(candidates)}"
        )
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
