#!/usr/bin/env python3
"""Classify spawned EverLeaf reactors that lack same-ID server scripts.

The server runtime resolves reactor handlers strictly as scripts/reactor/<id>.js.
This audit uses the reactor WZ definition to distinguish scriptless reactors
that declare an action from reactors with no declared action. The former are
high-priority restoration candidates; the latter remain review-only because
many retail reactors are passive/client-driven.

This audit is read-only and excludes Empress/Cygnus 130xxxxxx maps.
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"
REACTOR_ROOT = ROOT / "wz" / "Reactor.wz"
SCRIPT_ROOT = ROOT / "scripts" / "reactor"
EXCLUDED_MAP_START = 130_000_000
EXCLUDED_MAP_END = 131_000_000


def normalize(value: str | None) -> str:
    raw = (value or "").strip()
    if raw.lstrip("-").isdigit():
        return str(int(raw))
    return raw


def child_value(node: ET.Element, name: str) -> str | None:
    for child in node:
        if child.attrib.get("name") == name:
            return child.attrib.get("value")
    return None


def direct_imgdir(root: ET.Element, name: str) -> ET.Element | None:
    return next((c for c in root if c.tag == "imgdir" and c.attrib.get("name") == name), None)


def excluded_map(map_id: str) -> bool:
    raw = normalize(map_id)
    return raw.isdigit() and EXCLUDED_MAP_START <= int(raw) < EXCLUDED_MAP_END


def spawned_reactors() -> tuple[dict[str, set[str]], list[str]]:
    usage: dict[str, set[str]] = defaultdict(set)
    errors: list[str] = []
    for path in sorted(MAP_ROOT.glob("Map*/*.img.xml")):
        map_id = normalize(path.name.split(".", 1)[0])
        if excluded_map(map_id):
            continue
        try:
            root = ET.parse(path).getroot()
        except (ET.ParseError, OSError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        reactors = direct_imgdir(root, "reactor")
        if reactors is None:
            continue
        for node in reactors:
            if node.tag != "imgdir":
                continue
            reactor_id = normalize(child_value(node, "id"))
            if reactor_id.isdigit():
                usage[reactor_id].add(map_id)
    return usage, errors


def reactor_action(reactor_id: str) -> tuple[str, str | None]:
    path = REACTOR_ROOT / f"{int(reactor_id):07d}.img.xml"
    if not path.is_file():
        return "", "missing reactor WZ definition"
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        return "", str(exc)
    return (child_value(root, "action") or "").strip(), None


def main() -> int:
    emit_json = "--json" in sys.argv
    usage, parse_errors = spawned_reactors()
    actionable: list[dict[str, object]] = []
    passive: list[dict[str, object]] = []
    definition_errors: list[dict[str, str]] = []
    scripted = 0

    for reactor_id in sorted(usage, key=int):
        if (SCRIPT_ROOT / f"{reactor_id}.js").is_file():
            scripted += 1
            continue
        action, error = reactor_action(reactor_id)
        record = {
            "reactorId": reactor_id,
            "maps": sorted(usage[reactor_id], key=int),
            "spawnMapCount": len(usage[reactor_id]),
        }
        if error:
            definition_errors.append({"reactorId": reactor_id, "error": error})
        elif action:
            record["action"] = action
            actionable.append(record)
        else:
            passive.append(record)

    payload = {
        "uniqueSpawnedReactors": len(usage),
        "spawnedReactorsWithScripts": scripted,
        "scriptlessWithDeclaredActionCount": len(actionable),
        "scriptlessWithoutDeclaredActionCount": len(passive),
        "parseErrors": parse_errors,
        "definitionErrors": definition_errors,
        "scriptlessWithDeclaredAction": actionable,
        "scriptlessWithoutDeclaredAction": passive,
    }

    if emit_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(
            "Reactor script coverage: "
            f"{len(usage)} unique spawned / {scripted} scripted / "
            f"{len(actionable)} scriptless with declared action / "
            f"{len(passive)} scriptless without declared action"
        )
        for item in actionable:
            print(
                f"[ACTION] reactor={item['reactorId']} action={item['action']} "
                f"maps={','.join(item['maps'][:8])}"
            )
        for item in definition_errors:
            print(f"[FAIL] reactor={item['reactorId']}: {item['error']}")

    return 1 if parse_errors or definition_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
