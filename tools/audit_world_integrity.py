#!/usr/bin/env python3
"""Static EverLeaf world-data integrity audit.

This audit is intentionally conservative: it fails CI only for references that
should be structurally impossible in a healthy client/server data set (for
example, a spawned NPC or mob with no matching WZ definition, or a normal
portal targeting a map that is absent from Map.wz).

Script coverage is review information because many retail/client-side portals
do not require a server-side script. One known Boss Rush legacy reference is
also review-only: map 970033000 contains a portal named ``test`` targeting
970033001, which is absent from this v83 data set. The map is legitimate Boss
Rush content and is intentionally left unchanged until runtime progression
proves that the dormant target is required.

Boss Rush has many unused map variants in the WZ. EverLeaf's Agent Meow script
selects only lobbies 0-7, so the audit validates the 8 active lobby variants of
stages 1-27 plus the five rest maps instead of treating dormant variants as
production progression.

Empress / Knights of Cygnus content is outside EverLeaf's release scope. Maps in
the 130xxxxxx family and links targeting that family are excluded from this
audit entirely.
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
NPC_SCRIPT_ROOT = ROOT / "scripts" / "npc"
PORTAL_SCRIPT_ROOT = ROOT / "scripts" / "portal"
EXCLUDED_MAP_START = 130_000_000
EXCLUDED_MAP_END = 131_000_000

BOSS_RUSH_LOBBIES = range(8)
BOSS_RUSH_STAGE_BASES = [970030100 + (100 * index) for index in range(27)]
BOSS_RUSH_PROGRESS_BASES = BOSS_RUSH_STAGE_BASES[:-1]
BOSS_RUSH_REST_MAPS = {str(970030001 + index) for index in range(5)}
BOSS_RUSH_ACTIVE_MAPS = {
    str(base + lobby)
    for base in BOSS_RUSH_STAGE_BASES
    for lobby in BOSS_RUSH_LOBBIES
}
BOSS_RUSH_PROGRESS_MAPS = {
    str(base + lobby)
    for base in BOSS_RUSH_PROGRESS_BASES
    for lobby in BOSS_RUSH_LOBBIES
}


@dataclass(frozen=True)
class Finding:
    kind: str
    map_id: str
    object_id: str
    detail: str


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
    return {path.name.split(".", 1)[0].lstrip("0") or "0" for path in root.glob("*.img.xml")}


def normalize_id(value: str | None) -> str:
    if value is None:
        return ""
    value = value.strip()
    if value.lstrip("-").isdigit():
        return str(int(value))
    return value


def is_excluded_map(value: str | None) -> bool:
    normalized = normalize_id(value)
    if not normalized.isdigit():
        return False
    number = int(normalized)
    return EXCLUDED_MAP_START <= number < EXCLUDED_MAP_END


def map_files() -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in MAP_ROOT.glob("Map*/*.img.xml"):
        raw = path.name.split(".", 1)[0]
        map_id = str(int(raw)) if raw.isdigit() else raw
        if is_excluded_map(map_id):
            continue
        files[map_id] = path
    return files


def is_known_legacy_missing_target(map_id: str, portal_name: str, target: str) -> bool:
    return map_id == "970033000" and portal_name == "test" and target == "970033001"


def boss_rush_next_stage(map_id: str) -> str:
    current = int(map_id)
    if current % 500 >= 100:
        return str(current + 100)
    return str(970030001 + ((current - 970030100) // 500))


def main() -> int:
    emit_json = "--json" in sys.argv

    required_dirs = [MAP_ROOT, NPC_ROOT, MOB_ROOT, REACTOR_ROOT]
    missing_dirs = [str(path.relative_to(ROOT)) for path in required_dirs if not path.is_dir()]
    if missing_dirs:
        print("Missing required WZ directories: " + ", ".join(missing_dirs), file=sys.stderr)
        return 2

    maps = map_files()
    npc_ids = resource_ids(NPC_ROOT)
    mob_ids = resource_ids(MOB_ROOT)
    reactor_ids = resource_ids(REACTOR_ROOT)

    hard_findings: list[Finding] = []
    review_findings: list[Finding] = []
    parse_errors: list[str] = []
    counts: Counter[str] = Counter()
    boss_rush_raid_stage_maps: set[str] = set()

    for map_id, path in sorted(maps.items(), key=lambda item: int(item[0])):
        try:
            root = ET.parse(path).getroot()
        except (ET.ParseError, OSError) as exc:
            parse_errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue

        life = direct_imgdir(root, "life")
        if life is not None:
            for node in life:
                if node.tag != "imgdir":
                    continue
                life_type = child_value(node, "type")
                object_id = normalize_id(child_value(node, "id"))
                if not object_id:
                    continue

                if life_type == "n":
                    counts["npc_spawns"] += 1
                    if object_id not in npc_ids:
                        hard_findings.append(Finding(
                            "missing_npc_wz", map_id, object_id,
                            f"NPC {object_id} is spawned but wz/Npc.wz/{object_id}.img.xml is missing",
                        ))
                    script = NPC_SCRIPT_ROOT / f"{object_id}.js"
                    if not script.is_file():
                        counts["npc_without_script"] += 1
                elif life_type == "m":
                    counts["mob_spawns"] += 1
                    if object_id not in mob_ids:
                        hard_findings.append(Finding(
                            "missing_mob_wz", map_id, object_id,
                            f"Mob {object_id} is spawned but wz/Mob.wz/{object_id}.img.xml is missing",
                        ))

        reactors = direct_imgdir(root, "reactor")
        if reactors is not None:
            for node in reactors:
                if node.tag != "imgdir":
                    continue
                object_id = normalize_id(child_value(node, "id"))
                if not object_id:
                    continue
                counts["reactor_spawns"] += 1
                if object_id not in reactor_ids:
                    hard_findings.append(Finding(
                        "missing_reactor_wz", map_id, object_id,
                        f"Reactor {object_id} is spawned but wz/Reactor.wz/{object_id}.img.xml is missing",
                    ))

        portals = direct_imgdir(root, "portal")
        if portals is not None:
            for node in portals:
                if node.tag != "imgdir":
                    continue
                counts["portals"] += 1
                portal_name = child_value(node, "pn") or node.attrib.get("name", "?")
                target = normalize_id(child_value(node, "tm"))
                script_name = (child_value(node, "script") or "").strip()

                if is_excluded_map(target):
                    counts["excluded_empress_links"] += 1
                    continue

                if target and target not in {"-1", "999999999"} and target not in maps:
                    finding = Finding(
                        "missing_target_map", map_id, portal_name,
                        f"Portal {portal_name!r} targets missing map {target}",
                    )
                    if is_known_legacy_missing_target(map_id, portal_name, target):
                        review_findings.append(finding)
                        counts["known_legacy_missing_targets"] += 1
                    else:
                        hard_findings.append(finding)

                if script_name:
                    counts["scripted_portals"] += 1
                    if not (PORTAL_SCRIPT_ROOT / f"{script_name}.js").is_file():
                        review_findings.append(Finding(
                            "missing_portal_script", map_id, portal_name,
                            f"Portal {portal_name!r} references script {script_name!r}, but scripts/portal/{script_name}.js is missing",
                        ))
                    elif script_name == "raid_stage":
                        counts["boss_rush_stage_portals_all_variants"] += 1
                        boss_rush_raid_stage_maps.add(map_id)
                        if map_id in BOSS_RUSH_PROGRESS_MAPS:
                            counts["boss_rush_stage_portals_active"] += 1
                            next_stage = boss_rush_next_stage(map_id)
                            if next_stage not in maps:
                                hard_findings.append(Finding(
                                    "missing_boss_rush_stage", map_id, portal_name,
                                    f"Active Boss Rush portal {portal_name!r} computes missing next map {next_stage}",
                                ))

    for map_id in sorted(BOSS_RUSH_ACTIVE_MAPS, key=int):
        if map_id not in maps:
            hard_findings.append(Finding(
                "missing_boss_rush_map", map_id, "BossRushPQ",
                f"Active Boss Rush lobby/stage map {map_id} is missing",
            ))

    for map_id in sorted(BOSS_RUSH_REST_MAPS, key=int):
        if map_id not in maps:
            hard_findings.append(Finding(
                "missing_boss_rush_rest_map", map_id, "BossRushPQ",
                f"Boss Rush rest map {map_id} is missing",
            ))

    for map_id in sorted(BOSS_RUSH_PROGRESS_MAPS, key=int):
        if map_id in maps and map_id not in boss_rush_raid_stage_maps:
            hard_findings.append(Finding(
                "missing_boss_rush_progress_portal", map_id, "raid_stage",
                f"Active Boss Rush stage {map_id} has no raid_stage portal",
            ))

    payload = {
        "maps": len(maps),
        "npcDefinitions": len(npc_ids),
        "mobDefinitions": len(mob_ids),
        "reactorDefinitions": len(reactor_ids),
        "counts": dict(sorted(counts.items())),
        "parseErrors": parse_errors,
        "hardFailureCount": len(hard_findings) + len(parse_errors),
        "reviewFindingCount": len(review_findings),
        "hardFindings": [asdict(finding) for finding in hard_findings],
        "reviewFindings": [asdict(finding) for finding in review_findings],
    }

    if emit_json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            "EverLeaf world integrity audit: "
            f"{len(maps)} in-scope maps, {counts['npc_spawns']} NPC spawns, "
            f"{counts['mob_spawns']} mob spawns, {counts['portals']} portals"
        )
        print(
            f"Hard failures: {payload['hardFailureCount']}; "
            f"review-only findings: {payload['reviewFindingCount']}; "
            f"NPCs without dedicated scripts: {counts['npc_without_script']}; "
            f"excluded Empress links: {counts['excluded_empress_links']}; "
            f"active Boss Rush stage portals: {counts['boss_rush_stage_portals_active']}"
        )
        for error in parse_errors:
            print(f"[FAIL] XML parse error: {error}")
        for finding in hard_findings:
            print(f"[FAIL] map={finding.map_id} {finding.detail}")
        for finding in review_findings[:50]:
            print(f"[REVIEW] map={finding.map_id} {finding.detail}")
        if len(review_findings) > 50:
            print(f"[REVIEW] ... {len(review_findings) - 50} additional review-only findings omitted")

    return 1 if parse_errors or hard_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
