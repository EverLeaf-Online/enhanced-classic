#!/usr/bin/env python3
"""Repository-wide structural Quest.wz integrity audit for EverLeaf.

This first global quest gate is intentionally conservative. It hard-fails only
references that are structurally impossible at runtime:

* malformed Quest.wz XML
* a quest owner NPC referenced by Check.wz has no Npc.wz asset
* a prerequisite quest referenced from a Check.wz `quest` condition does not
  exist in Check.wz
* a Quest.wz quest id is not numeric

Differences between Check/Act/Say/QuestInfo are inventoried as review data,
because classic v83 contains legitimate tutorial/dialogue quests without every
section. Future regional audits can make those requirements stricter once the
content is classified.
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
    """Quest start/end NPCs are direct `npc` values on Check.wz phase nodes."""
    refs: set[str] = set()
    for phase in check_node:
        if phase.tag != "imgdir":
            continue
        npc = normalize(direct_child_value(phase, "npc"))
        if npc.isdigit() and int(npc) > 0:
            refs.add(npc)
    return refs


def prerequisite_quests(check_node: ET.Element) -> set[str]:
    """Collect prerequisite quest ids from explicit `quest` condition groups."""
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

    check_ids = set(quest_sets.get("check", {}))
    owner_refs: dict[str, set[str]] = defaultdict(set)
    prereq_refs: dict[str, set[str]] = defaultdict(set)
    missing_npcs: list[tuple[str, str]] = []
    missing_prereqs: list[tuple[str, str]] = []

    for qid, node in quest_sets.get("check", {}).items():
        owners = owner_npcs(node)
        prereqs = prerequisite_quests(node)
        owner_refs[qid].update(owners)
        prereq_refs[qid].update(prereqs)

        for npc_id in sorted(owners, key=int):
            if not npc_asset_exists(npc_id):
                missing_npcs.append((qid, npc_id))
                failures.append(f"Quest {qid} references missing owner NPC asset {npc_id}")

        for required_qid in sorted(prereqs, key=int):
            if required_qid not in check_ids:
                missing_prereqs.append((qid, required_qid))
                failures.append(f"Quest {qid} requires missing prerequisite quest {required_qid}")

    # Inventory section asymmetry without assuming every old v83 quest needs
    # every section. Regional/content-specific audits can promote individual
    # cases to hard failures after classification.
    section_missing_counts: dict[str, int] = {}
    for kind in ("act", "say", "info"):
        missing = sorted(check_ids - set(quest_sets.get(kind, {})), key=int)
        section_missing_counts[kind] = len(missing)
        if missing:
            preview = ", ".join(missing[:20])
            suffix = " ..." if len(missing) > 20 else ""
            reviews.append(
                f"{len(missing)} Check.wz quests have no {kind} section: {preview}{suffix}"
            )

    # Also inventory data present outside Check.wz. These can be historical or
    # event leftovers, so they are review-only until classified.
    orphan_section_counts: dict[str, int] = {}
    for kind in ("act", "say", "info"):
        extras = sorted(set(quest_sets.get(kind, {})) - check_ids, key=int)
        orphan_section_counts[kind] = len(extras)
        if extras:
            preview = ", ".join(extras[:20])
            suffix = " ..." if len(extras) > 20 else ""
            reviews.append(
                f"{len(extras)} {kind} sections have no Check.wz quest: {preview}{suffix}"
            )

    owner_counter = Counter(npc for refs in owner_refs.values() for npc in refs)
    prereq_edge_count = sum(len(refs) for refs in prereq_refs.values())
    payload = {
        "questCounts": {kind: len(nodes) for kind, nodes in quest_sets.items()},
        "uniqueOwnerNpcs": len(owner_counter),
        "ownerReferenceCount": sum(owner_counter.values()),
        "prerequisiteEdgeCount": prereq_edge_count,
        "missingOwnerNpcs": [
            {"quest": qid, "npc": npc} for qid, npc in missing_npcs
        ],
        "missingPrerequisites": [
            {"quest": qid, "prerequisite": required} for qid, required in missing_prereqs
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
