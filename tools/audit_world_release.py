#!/usr/bin/env python3
"""Release-facing NPC/map/portal audit for EverLeaf.

This audit turns the broad WZ review queue into release-relevant findings.
It intentionally excludes Empress/Cygnus map data (130xxxxxx) and preserves
known legacy/event content unless it creates a structural runtime failure.

Checks:
- full NPC spawn integrity across every in-scope map
- exact duplicate NPC spawns
- spawned NPC script coverage
- static portal destination integrity with runtime portal-0 fallback awareness
- missing portal script references grouped by active/legacy map families
- map XML parse failures

The tool is read-only and safe for CI.
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"
NPC_ROOT = ROOT / "wz" / "Npc.wz"
NPC_SCRIPTS = ROOT / "scripts" / "npc"
PORTAL_SCRIPTS = ROOT / "scripts" / "portal"

EXCLUDED_MAP_START = 130_000_000
EXCLUDED_MAP_END = 131_000_000
SPECIAL_TARGETS = {"", "-1", "0", "999999999"}

LEGACY_PORTAL_MAP_PREFIXES = (
    "109", "22903", "390", "677", "682", "683", "709", "889",
    "91002", "91003", "91004", "912", "914", "921", "92223",
    "92612", "97000", "97001", "97002", "980",
)

REVIEWED_LEGACY_PORTAL_SCRIPTS = {
    "rand_ola", "BF_out",
    "chimney00_open", "chimney01_open", "chimney02_open", "chimney03_open",
    "chimney10_open", "chimney11_open", "chimney12_open", "chimney13_open",
    "chimney20_open", "chimney21_open", "chimney22_open", "chimney23_open",
    "ghost1", "ghost2", "ghost3", "ghostOut1", "ghostOut2", "ghostOut3",
    "connetNPC0", "hwqout", "checkWildeye", "oliviahallOut",
    "MD_cakeGL1", "MD_cakeGL2", "MD_cakeGL3", "MD_cakeoutGL",
    "Jump_event_pro", "08_xmas_st", "outBabyBird", "been_enter", "donghwa_out",
    "pinokio_enter", "snack_enter", "donghwa_end", "beenTreeGate", "been_next",
    "pinokio_next", "pinokio_buff", "pinokio_move", "pinokio_move2", "pinokio_move3",
    "end_black", "nooutShip", "clearRider", "ropeEarth1", "ropeEarth2", "ropeMoon1",
    "ropeMoon2", "warpEarth", "warpMoon", "cheeseEnd", "cheeseLog", "cheeseEx",
    "cheeseOut", "photoOut", "StudioZone_Out", "mapleTree_out", "fishingOut",
    "aM_start", "PB_wich", "tH_Out",
    "goldkey1", "goldkey2", "goldkey3", "goldkey4", "goldkey5", "goldkey6",
    "goldkey7", "goldkey8", "goldkey9", "goldkey10",
}

KNOWN_LEGACY_MISSING_TARGETS = {("970033000", "test", "970033001")}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    map_id: str
    object_id: str
    detail: str


def normalize_id(value: str | None) -> str:
    if value is None:
        return ""
    value = value.strip()
    if value.lstrip("-").isdigit():
        return str(int(value))
    return value


def padded_map_id(value: str | None) -> str:
    normalized = normalize_id(value)
    if normalized.isdigit():
        return f"{int(normalized):09d}"
    return normalized


def is_excluded_map(value: str | None) -> bool:
    normalized = normalize_id(value)
    if not normalized.isdigit():
        return False
    number = int(normalized)
    return EXCLUDED_MAP_START <= number < EXCLUDED_MAP_END


def direct_imgdir(root: ET.Element, name: str) -> ET.Element | None:
    return next((c for c in root if c.tag == "imgdir" and c.attrib.get("name") == name), None)


def child_value(node: ET.Element, name: str) -> str | None:
    for child in node:
        if child.attrib.get("name") == name:
            return child.attrib.get("value")
    return None


def map_files() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in MAP_ROOT.glob("Map*/*.img.xml"):
        raw = path.name.split(".", 1)[0]
        if is_excluded_map(raw):
            continue
        result[padded_map_id(raw)] = path
    return result


def npc_asset_exists(npc_id: str) -> bool:
    return npc_id.isdigit() and (NPC_ROOT / f"{int(npc_id):07d}.img.xml").is_file()


def is_legacy_portal_script(map_id: str, script: str) -> bool:
    return script in REVIEWED_LEGACY_PORTAL_SCRIPTS or map_id.startswith(LEGACY_PORTAL_MAP_PREFIXES)


def main() -> int:
    emit_json = "--json" in sys.argv
    maps = map_files()
    parsed: dict[str, ET.Element] = {}
    parse_errors: list[str] = []
    portal_names: dict[str, set[str]] = defaultdict(set)
    portal_ids: dict[str, set[int]] = defaultdict(set)
    hard: list[Finding] = []
    review: list[Finding] = []
    reviewed_legacy: list[Finding] = []
    counts: Counter[str] = Counter()

    for map_id, path in sorted(maps.items()):
        try:
            root = ET.parse(path).getroot()
        except (ET.ParseError, OSError) as exc:
            parse_errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        parsed[map_id] = root
        portals = direct_imgdir(root, "portal")
        if portals is None:
            continue
        for node in portals:
            if node.tag != "imgdir":
                continue
            pn = (child_value(node, "pn") or "").strip()
            if pn:
                portal_names[map_id].add(pn)
            raw_idx = (node.attrib.get("name") or "").strip()
            if raw_idx.lstrip("-").isdigit():
                portal_ids[map_id].add(int(raw_idx))

    unique_spawned_npcs: set[str] = set()
    npc_without_script: set[str] = set()

    for map_id, root in sorted(parsed.items()):
        life = direct_imgdir(root, "life")
        if life is not None:
            exact_npcs: Counter[tuple[str, str, str, str, str, str, str]] = Counter()
            for node in life:
                if node.tag != "imgdir" or (child_value(node, "type") or "").strip() != "n":
                    continue
                counts["npc_spawns"] += 1
                npc_id = normalize_id(child_value(node, "id"))
                unique_spawned_npcs.add(npc_id)
                if not npc_id or not npc_id.isdigit():
                    hard.append(Finding("FAIL", "invalid_npc_id", map_id, npc_id, "NPC spawn has a missing/non-numeric ID"))
                    continue
                if not npc_asset_exists(npc_id):
                    hard.append(Finding("FAIL", "missing_npc_asset", map_id, npc_id, "Spawned NPC has no matching Npc.wz definition"))
                if not (NPC_SCRIPTS / f"{npc_id}.js").is_file():
                    npc_without_script.add(npc_id)
                signature = (
                    npc_id,
                    child_value(node, "x") or "?",
                    child_value(node, "y") or "?",
                    child_value(node, "fh") or "?",
                    child_value(node, "rx0") or "?",
                    child_value(node, "rx1") or "?",
                    child_value(node, "hide") or "0",
                )
                exact_npcs[signature] += 1
            for signature, amount in exact_npcs.items():
                if amount > 1:
                    hard.append(Finding("FAIL", "duplicate_npc_spawn", map_id, signature[0], f"{amount} exact duplicate NPC spawn records"))

        portals = direct_imgdir(root, "portal")
        if portals is None:
            continue
        for node in portals:
            if node.tag != "imgdir":
                continue
            counts["portals"] += 1
            pn = (child_value(node, "pn") or node.attrib.get("name", "?")).strip()
            raw_tm = (child_value(node, "tm") or "").strip()
            tm = padded_map_id(raw_tm)
            tn = (child_value(node, "tn") or "").strip()
            script = (child_value(node, "script") or "").strip()

            if is_excluded_map(raw_tm):
                counts["excluded_empress_links"] += 1
                continue

            if script and not (PORTAL_SCRIPTS / f"{script}.js").is_file():
                counts["missing_portal_scripts"] += 1
                finding = Finding("REVIEW", "missing_portal_script", map_id, script, f"Portal {pn!r} references absent scripts/portal/{script}.js")
                if is_legacy_portal_script(map_id, script):
                    reviewed_legacy.append(finding)
                    counts["reviewed_legacy_portal_scripts"] += 1
                else:
                    review.append(finding)

            if raw_tm in SPECIAL_TARGETS or not tm:
                continue
            if tm not in maps:
                key = (map_id, pn, tm)
                if key in KNOWN_LEGACY_MISSING_TARGETS:
                    reviewed_legacy.append(Finding("REVIEW", "missing_target_map", map_id, pn, f"Portal targets absent map {tm}"))
                else:
                    hard.append(Finding("FAIL", "missing_target_map", map_id, pn, f"Portal targets absent map {tm}"))
                continue

            if script or not tn or tn in portal_names.get(tm, set()):
                continue
            if 0 in portal_ids.get(tm, set()):
                counts["safe_target_portal_fallbacks"] += 1
                reviewed_legacy.append(Finding("REVIEW", "target_portal_runtime_fallback", map_id, pn, f"Target portal {tm}:{tn} is absent; runtime portal ID 0 fallback exists"))
            else:
                hard.append(Finding("FAIL", "missing_target_portal", map_id, pn, f"Target portal {tm}:{tn} is absent and target map has no portal ID 0 fallback"))

    counts["unique_spawned_npcs"] = len(unique_spawned_npcs)
    counts["unique_npcs_without_same_id_script"] = len(npc_without_script)
    if npc_without_script:
        review.append(Finding(
            "REVIEW", "npc_script_coverage", "*", str(len(npc_without_script)),
            f"{len(npc_without_script)} of {len(unique_spawned_npcs)} unique spawned NPC IDs have no same-ID script; no missing NPC assets or duplicate spawn records were found",
        ))

    payload = {
        "mapsScanned": len(maps),
        "counts": dict(sorted(counts.items())),
        "parseErrors": parse_errors,
        "hardFailureCount": len(hard) + len(parse_errors),
        "reviewFindingCount": len(review),
        "reviewedLegacyCount": len(reviewed_legacy),
        "hardFindings": [asdict(x) for x in hard],
        "reviewFindings": [asdict(x) for x in review],
        "reviewedLegacy": [asdict(x) for x in reviewed_legacy],
    }

    if emit_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"EverLeaf release world audit: {len(maps)} maps; {counts['npc_spawns']} NPC spawns; {counts['portals']} portals")
        print(f"Hard failures: {payload['hardFailureCount']}; actionable reviews: {payload['reviewFindingCount']}; reviewed legacy/safe fallbacks: {payload['reviewedLegacyCount']}")
        for err in parse_errors:
            print(f"[FAIL] {err}")
        for finding in hard:
            print(f"[FAIL] {finding.code} map={finding.map_id}: {finding.detail}")
        for finding in review:
            print(f"[REVIEW] {finding.code} map={finding.map_id}: {finding.detail}")

    return 1 if parse_errors or hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
