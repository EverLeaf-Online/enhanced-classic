#!/usr/bin/env python3
"""Repository-wide structural Quest.wz integrity audit for EverLeaf.

The global quest corpus contains dormant/event/donor records that are not
reachable in the active v83 world. This audit therefore separates release-
facing quest problems from archival data cleanup:

Hard failures:
* malformed Quest.wz / active map XML
* non-numeric or duplicate Quest.wz quest ids
* an ACTIVE quest owner NPC has no Npc.wz asset
* an ACTIVE quest requires a prerequisite absent from Check.wz

Review-only inventory:
* missing NPCs referenced only by dormant quest records
* missing prerequisites referenced only by dormant quest records
* section asymmetry between Check/Act/Say/QuestInfo

A quest is considered active when at least one of its Check.wz start/completion
owner NPCs is actually spawned in the active Map.wz map corpus.
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEST_ROOT = ROOT / "wz" / "Quest.wz"
NPC_ROOT = ROOT / "wz" / "Npc.wz"
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"

QUEST_FILES = {
    "check": QUEST_ROOT / "Check.img.xml",
    "act": QUEST_ROOT / "Act.img.xml",
    "say": QUEST_ROOT / "Say.img.xml",
    "info": QUEST_ROOT / "QuestInfo.img.xml",
}


def normalize(value: str | None) -> str:
    raw = (value or "").strip()
    if raw.lstrip("-").isdigit():
        return str(int(raw))
    return raw


def parse(path: Path) -> ET.Element:
    return ET.parse(path).getroot()


def quest_nodes(root: ET.Element, source: str, failures: list[str]) -> dict[str, ET.Element]:
    result: dict[str, ET.Element] = {}
    for node in root:
        if node.tag != "imgdir":
            continue
        raw = (node.attrib.get("name") or "").strip()
        qid = normalize(raw)
        if not qid.isdigit():
            failures.append(f"{source}: non-numeric quest id {raw!r}")
            continue
        if qid in result:
            failures.append(f"{source}: duplicate quest id {qid}")
            continue
        result[qid] = node
    return result


def direct_child_value(node: ET.Element, name: str) -> str | None:
    for child in node:
        if child.attrib.get("name") == name:
            return child.attrib.get("value")
    return None


def owner_npcs(check_node: ET.Element) -> set[str]:
    refs: set[str] = set()
    for phase in check_node:
        if phase.tag != "imgdir":
            continue
        npc = normalize(direct_child_value(phase, "npc"))
        if npc.isdigit() and int(npc) > 0:
            refs.add(npc)
    return refs


def prerequisite_quests(check_node: ET.Element) -> set[str]:
    refs: set[str] = set()
    for phase in check_node:
        if phase.tag != "imgdir":
            continue
        for group in phase:
            if group.tag != "imgdir" or group.attrib.get("name") != "quest":
                continue
            for entry in group:
                if entry.tag != "imgdir":
                    continue
                qid = normalize(direct_child_value(entry, "id"))
                if qid.isdigit() and int(qid) > 0:
                    refs.add(qid)
    return refs


def npc_asset_exists(npc_id: str) -> bool:
    return (NPC_ROOT / f"{int(npc_id):07d}.img.xml").is_file()


def collect_active_npcs(failures: list[str]) -> tuple[set[str], int]:
    active: set[str] = set()
    map_count = 0
    for path in sorted(MAP_ROOT.glob("Map*/*.img.xml")):
        try:
            root = parse(path)
        except (ET.ParseError, OSError) as exc:
            failures.append(f"Unable to parse active map {path.relative_to(ROOT)}: {exc}")
            continue
        map_count += 1
        life = next(
            (c for c in root if c.tag == "imgdir" and c.attrib.get("name") == "life"),
            None,
        )
        if life is None:
            continue
        for entry in life:
            if entry.tag != "imgdir":
                continue
            life_type = normalize(direct_child_value(entry, "type"))
            if life_type != "n":
                continue
            npc_id = normalize(direct_child_value(entry, "id"))
            if npc_id.isdigit() and int(npc_id) > 0:
                active.add(npc_id)
    return active, map_count


def preview(values: list[str], limit: int = 20) -> str:
    text = ", ".join(values[:limit])
    return text + (" ..." if len(values) > limit else "")


def main() -> int:
    emit_json = "--json" in sys.argv
    failures: list[str] = []
    reviews: list[str] = []
    quest_sets: dict[str, dict[str, ET.Element]] = {}

    for kind, path in QUEST_FILES.items():
        try:
            quest_sets[kind] = quest_nodes(parse(path), path.name, failures)
        except (ET.ParseError, OSError) as exc:
            failures.append(f"Unable to parse {path.relative_to(ROOT)}: {exc}")
            quest_sets[kind] = {}

    active_npcs, active_map_count = collect_active_npcs(failures)
    check_ids = set(quest_sets.get("check", {}))
    owner_refs: dict[str, set[str]] = defaultdict(set)
    prereq_refs: dict[str, set[str]] = defaultdict(set)
    active_quests: set[str] = set()

    active_missing_npcs: list[tuple[str, str]] = []
    dormant_missing_npcs: list[tuple[str, str]] = []
    active_missing_prereqs: list[tuple[str, str]] = []
    dormant_missing_prereqs: list[tuple[str, str]] = []

    for qid, node in quest_sets.get("check", {}).items():
        owners = owner_npcs(node)
        prereqs = prerequisite_quests(node)
        owner_refs[qid].update(owners)
        prereq_refs[qid].update(prereqs)

        is_active = bool(owners & active_npcs)
        if is_active:
            active_quests.add(qid)

        for npc_id in sorted(owners, key=int):
            if npc_asset_exists(npc_id):
                continue
            pair = (qid, npc_id)
            if is_active:
                active_missing_npcs.append(pair)
                failures.append(f"Active quest {qid} references missing owner NPC asset {npc_id}")
            else:
                dormant_missing_npcs.append(pair)

        for required_qid in sorted(prereqs, key=int):
            if required_qid in check_ids:
                continue
            pair = (qid, required_qid)
            if is_active:
                active_missing_prereqs.append(pair)
                failures.append(
                    f"Active quest {qid} requires missing prerequisite quest {required_qid}"
                )
            else:
                dormant_missing_prereqs.append(pair)

    if dormant_missing_npcs:
        samples = [f"{qid}->{npc}" for qid, npc in dormant_missing_npcs]
        reviews.append(
            f"{len(dormant_missing_npcs)} dormant quest owner references have no NPC asset: "
            + preview(samples)
        )
    if dormant_missing_prereqs:
        samples = [f"{qid}->{req}" for qid, req in dormant_missing_prereqs]
        reviews.append(
            f"{len(dormant_missing_prereqs)} dormant prerequisite edges target absent Check.wz quests: "
            + preview(samples)
        )

    section_missing_counts: dict[str, int] = {}
    for kind in ("act", "say", "info"):
        missing = sorted(check_ids - set(quest_sets.get(kind, {})), key=int)
        section_missing_counts[kind] = len(missing)
        if missing:
            reviews.append(
                f"{len(missing)} Check.wz quests have no {kind} section: {preview(missing)}"
            )

    orphan_section_counts: dict[str, int] = {}
    for kind in ("act", "say", "info"):
        extras = sorted(set(quest_sets.get(kind, {})) - check_ids, key=int)
        orphan_section_counts[kind] = len(extras)
        if extras:
            reviews.append(
                f"{len(extras)} {kind} sections have no Check.wz quest: {preview(extras)}"
            )

    owner_counter = Counter(npc for refs in owner_refs.values() for npc in refs)
    prereq_edge_count = sum(len(refs) for refs in prereq_refs.values())
    payload = {
        "questCounts": {kind: len(nodes) for kind, nodes in quest_sets.items()},
        "activeMapCount": active_map_count,
        "activeNpcCount": len(active_npcs),
        "activeQuestCount": len(active_quests),
        "uniqueOwnerNpcs": len(owner_counter),
        "ownerReferenceCount": sum(owner_counter.values()),
        "prerequisiteEdgeCount": prereq_edge_count,
        "activeMissingOwnerNpcs": [
            {"quest": qid, "npc": npc} for qid, npc in active_missing_npcs
        ],
        "dormantMissingOwnerNpcs": [
            {"quest": qid, "npc": npc} for qid, npc in dormant_missing_npcs
        ],
        "activeMissingPrerequisites": [
            {"quest": qid, "prerequisite": required}
            for qid, required in active_missing_prereqs
        ],
        "dormantMissingPrerequisites": [
            {"quest": qid, "prerequisite": required}
            for qid, required in dormant_missing_prereqs
        ],
        "missingSectionCounts": section_missing_counts,
        "orphanSectionCounts": orphan_section_counts,
        "failures": failures,
        "reviews": reviews,
    }

    if emit_json:
        print(json.dumps(payload, indent=2))
    else:
        counts = payload["questCounts"]
        print(
            "Global quest integrity audit: "
            f"Check={counts.get('check', 0)} Act={counts.get('act', 0)} "
            f"Say={counts.get('say', 0)} Info={counts.get('info', 0)}"
        )
        print(
            f"Active world: {active_map_count} maps / {len(active_npcs)} NPCs / "
            f"{len(active_quests)} reachable quest records"
        )
        print(
            f"Quest owners: {payload['uniqueOwnerNpcs']} unique NPCs / "
            f"{payload['ownerReferenceCount']} references"
        )
        print(f"Prerequisite edges: {prereq_edge_count}")
        for item in reviews:
            print(f"[REVIEW] {item}")
        for item in failures:
            print(f"[FAIL] {item}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
