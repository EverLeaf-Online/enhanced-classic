#!/usr/bin/env python3
"""Release-facing structural audit for EverLeaf maps, spawns, and reactors.

This complements the existing world integrity/link audits with checks that map
cleanly to the remaining content checklist without mutating WZ data:

- validate returnMap / forcedReturn targets used for death and forced exits
- validate NPC/mob/reactor spawn IDs against the corresponding WZ assets
- validate basic mob/NPC spawn coordinates, footholds, roam ranges, and timers
- report map mob-density outliers for manual gameplay review
- report spawned reactors that have no server reactor script
- exclude Empress/Cygnus 130xxxxxx content from non-Empress release readiness

The audit fails only on structural impossibilities. Missing reactor scripts and
high-density maps are review findings because some retail reactors are passive
and some maps intentionally contain dense spawns.
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"
NPC_ROOT = ROOT / "wz" / "Npc.wz"
MOB_ROOT = ROOT / "wz" / "Mob.wz"
REACTOR_ROOT = ROOT / "wz" / "Reactor.wz"
REACTOR_SCRIPT_ROOT = ROOT / "scripts" / "reactor"

EXCLUDED_MAP_START = 130_000_000
EXCLUDED_MAP_END = 131_000_000
SPECIAL_MAP_TARGETS = {"", "-1", "0", "999999999"}
DENSITY_REVIEW_THRESHOLD = 80


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    map_id: str
    object_id: str
    detail: str


def normalize(value: str | None) -> str:
    raw = (value or "").strip()
    if raw.lstrip("-").isdigit():
        return str(int(raw))
    return raw


def padded(value: str | None) -> str:
    raw = normalize(value)
    return f"{int(raw):09d}" if raw.isdigit() else raw


def is_excluded_map(value: str | None) -> bool:
    raw = normalize(value)
    return raw.isdigit() and EXCLUDED_MAP_START <= int(raw) < EXCLUDED_MAP_END


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


def resource_ids(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {normalize(path.name.split(".", 1)[0]) for path in root.glob("*.img.xml")}


def map_files() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in MAP_ROOT.glob("Map*/*.img.xml"):
        raw = path.name.split(".", 1)[0]
        if is_excluded_map(raw):
            continue
        result[padded(raw)] = path
    return result


def numeric_field(
    hard: list[Finding], map_id: str, object_id: str, node: ET.Element, name: str, *, required: bool = False
) -> int | None:
    raw = (child_value(node, name) or "").strip()
    if not raw:
        if required:
            hard.append(Finding("FAIL", f"missing_{name}", map_id, object_id, f"Missing required spawn field {name}"))
        return None
    try:
        return int(raw)
    except ValueError:
        hard.append(Finding("FAIL", f"invalid_{name}", map_id, object_id, f"Spawn field {name} is not numeric: {raw!r}"))
        return None


def main() -> int:
    emit_json = "--json" in sys.argv
    maps = map_files()
    npc_ids = resource_ids(NPC_ROOT)
    mob_ids = resource_ids(MOB_ROOT)
    reactor_ids = resource_ids(REACTOR_ROOT)

    hard: list[Finding] = []
    review: list[Finding] = []
    parse_errors: list[str] = []
    counts: Counter[str] = Counter()
    density: list[tuple[int, str]] = []
    reactors_without_scripts: set[str] = set()

    required_dirs = [MAP_ROOT, NPC_ROOT, MOB_ROOT, REACTOR_ROOT, REACTOR_SCRIPT_ROOT]
    missing_dirs = [str(path.relative_to(ROOT)) for path in required_dirs if not path.is_dir()]
    if missing_dirs:
        print("Missing required content directories: " + ", ".join(missing_dirs), file=sys.stderr)
        return 2

    for map_id, path in sorted(maps.items()):
        try:
            root = ET.parse(path).getroot()
        except (ET.ParseError, OSError) as exc:
            parse_errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue

        counts["maps_scanned"] += 1

        info = direct_imgdir(root, "info")
        if info is not None:
            for field in ("returnMap", "forcedReturn"):
                raw_target = (child_value(info, field) or "").strip()
                if not raw_target or raw_target in SPECIAL_MAP_TARGETS:
                    continue
                if is_excluded_map(raw_target):
                    counts["excluded_empress_map_targets"] += 1
                    continue
                target = padded(raw_target)
                counts[f"{field}_references"] += 1
                if target not in maps:
                    hard.append(Finding(
                        "FAIL",
                        f"missing_{field}_map",
                        map_id,
                        field,
                        f"Map {map_id} {field} points to absent map {target}",
                    ))

        mob_count = 0
        life = direct_imgdir(root, "life")
        if life is not None:
            for node in life:
                if node.tag != "imgdir":
                    continue
                life_type = (child_value(node, "type") or "").strip()
                if life_type not in {"n", "m"}:
                    continue
                object_id = normalize(child_value(node, "id"))
                if not object_id or not object_id.isdigit():
                    hard.append(Finding("FAIL", "invalid_spawn_id", map_id, object_id, f"{life_type!r} spawn has a missing/non-numeric id"))
                    continue

                if life_type == "n":
                    counts["npc_spawns"] += 1
                    if object_id not in npc_ids:
                        hard.append(Finding("FAIL", "missing_npc_asset", map_id, object_id, "Spawned NPC has no matching Npc.wz asset"))
                else:
                    counts["mob_spawns"] += 1
                    mob_count += 1
                    if object_id not in mob_ids:
                        hard.append(Finding("FAIL", "missing_mob_asset", map_id, object_id, "Spawned mob has no matching Mob.wz asset"))

                x = numeric_field(hard, map_id, object_id, node, "x", required=True)
                y = numeric_field(hard, map_id, object_id, node, "y", required=True)
                fh = numeric_field(hard, map_id, object_id, node, "fh", required=True)
                rx0 = numeric_field(hard, map_id, object_id, node, "rx0")
                rx1 = numeric_field(hard, map_id, object_id, node, "rx1")
                if rx0 is not None and rx1 is not None and rx0 > rx1:
                    hard.append(Finding("FAIL", "reversed_roam_range", map_id, object_id, f"Spawn rx0={rx0} is greater than rx1={rx1}"))
                if x is not None and rx0 is not None and rx1 is not None and not (rx0 <= x <= rx1):
                    review.append(Finding("REVIEW", "spawn_outside_roam_range", map_id, object_id, f"Spawn x={x} lies outside rx0/rx1 range {rx0}..{rx1}"))
                if fh is not None and fh < 0:
                    hard.append(Finding("FAIL", "negative_foothold", map_id, object_id, f"Spawn foothold is negative: {fh}"))
                if life_type == "m":
                    mob_time = numeric_field(hard, map_id, object_id, node, "mobTime")
                    if mob_time is not None and mob_time < -1:
                        hard.append(Finding("FAIL", "invalid_mob_time", map_id, object_id, f"mobTime={mob_time} is below supported sentinel -1"))

        density.append((mob_count, map_id))
        if mob_count >= DENSITY_REVIEW_THRESHOLD:
            review.append(Finding(
                "REVIEW",
                "high_mob_density",
                map_id,
                str(mob_count),
                f"Map contains {mob_count} mob spawn records; review intended density and respawn load",
            ))

        reactors = direct_imgdir(root, "reactor")
        if reactors is not None:
            for node in reactors:
                if node.tag != "imgdir":
                    continue
                object_id = normalize(child_value(node, "id"))
                counts["reactor_spawns"] += 1
                if not object_id or not object_id.isdigit():
                    hard.append(Finding("FAIL", "invalid_reactor_id", map_id, object_id, "Reactor spawn has a missing/non-numeric id"))
                    continue
                if object_id not in reactor_ids:
                    hard.append(Finding("FAIL", "missing_reactor_asset", map_id, object_id, "Spawned reactor has no matching Reactor.wz asset"))
                if not (REACTOR_SCRIPT_ROOT / f"{object_id}.js").is_file():
                    reactors_without_scripts.add(object_id)
                numeric_field(hard, map_id, object_id, node, "x", required=True)
                numeric_field(hard, map_id, object_id, node, "y", required=True)

    for reactor_id in sorted(reactors_without_scripts, key=lambda value: int(value)):
        review.append(Finding(
            "REVIEW",
            "reactor_without_server_script",
            "*",
            reactor_id,
            f"Spawned reactor {reactor_id} has no scripts/reactor/{reactor_id}.js; confirm it is intentionally passive/client-driven",
        ))

    top_density = [
        {"map": map_id, "mobSpawns": amount}
        for amount, map_id in sorted(density, reverse=True)[:25]
        if amount > 0
    ]
    counts["unique_spawned_reactors_without_scripts"] = len(reactors_without_scripts)

    payload = {
        "counts": dict(sorted(counts.items())),
        "topMobDensityMaps": top_density,
        "parseErrors": parse_errors,
        "hardFailureCount": len(hard) + len(parse_errors),
        "reviewFindingCount": len(review),
        "hardFindings": [asdict(item) for item in hard],
        "reviewFindings": [asdict(item) for item in review],
    }

    if emit_json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            "EverLeaf world content completeness audit: "
            f"{counts['maps_scanned']} maps / {counts['npc_spawns']} NPC spawns / "
            f"{counts['mob_spawns']} mob spawns / {counts['reactor_spawns']} reactor spawns"
        )
        print(
            f"Hard failures: {payload['hardFailureCount']}; reviews: {payload['reviewFindingCount']}; "
            f"reactor IDs without server scripts: {counts['unique_spawned_reactors_without_scripts']}"
        )
        for error in parse_errors:
            print(f"[FAIL] XML parse error: {error}")
        for item in hard:
            print(f"[FAIL] {item.code} map={item.map_id} object={item.object_id}: {item.detail}")
        for item in review[:80]:
            print(f"[REVIEW] {item.code} map={item.map_id} object={item.object_id}: {item.detail}")
        if len(review) > 80:
            print(f"[REVIEW] ... {len(review) - 80} additional review findings omitted")

    return 1 if parse_errors or hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
