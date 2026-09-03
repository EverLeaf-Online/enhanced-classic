#!/usr/bin/env python3
"""Review literal map references used by EverLeaf scripts.

The WZ world audit validates map-to-map portal data. This companion audit scans
server scripts for literal map IDs used by NPCs, events, portals, quests, and
reactors. Dynamic arithmetic and event-instance map allocation are deliberately
left as review-only because they cannot be proven safely with regex alone.

The repository's historical v83 Map.wz is intentionally smaller than the live
Community WZ package. LIVE_IMPORTED_MAPS records live-audited, deployed map IDs
that are valid script destinations even though they are not present in the old
repository XML snapshot.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"
SCRIPT_ROOTS = [
    ROOT / "scripts" / "npc",
    ROOT / "scripts" / "portal",
    ROOT / "scripts" / "event",
    ROOT / "scripts" / "quest",
    ROOT / "scripts" / "reactor",
]

SPECIAL_IDS = {-1, 0, 999999999}

# Live-audited Future Henesys / Knight Stronghold package from the Community WZ
# wholesale deployment (2026-09-03). Keep this explicit so CI cannot silently
# accept arbitrary post-v83 map IDs.
LIVE_IMPORTED_MAPS = {
    271000000, 271000100, 271000200, 271000210, 271000300,
    271010000, 271010001, 271010100, 271010200, 271010300, 271010301,
    271010400, 271010500, 271020000, 271020100, 271030000, 271030010,
    271030100, 271030101, 271030102, 271030200, 271030201, 271030202,
    271030203, 271030204, 271030205, 271030300, 271030310, 271030320,
    271030400, 271030410, 271030500, 271030510, 271030520, 271030530,
    271030540, 271030600, 271040000, 271040100, 271040200, 271040210,
    271040300,
}

KNOWN_REVIEW_REFERENCES = {
    ("scripts/portal/raid_stage.js", 970033001),
    ("scripts/npc/1013001.js", 900090101),
    ("scripts/npc/1013002.js", 900090103),
    ("scripts/npc/1096005.js", 912060300),
}

LITERAL_MAP_ID = r"(\d{6,9})\b(?!\s*[+\-*/%])"
PATTERNS = [
    re.compile(r"\b(?:cm|player|chr|victim|target)\.(?:warp|changeMap)\s*\(\s*" + LITERAL_MAP_ID),
    re.compile(r"\b(?:getMap|warpMap|warpAllPlayer|warpEveryone|warpAllPlayers)\s*\(\s*" + LITERAL_MAP_ID),
    re.compile(r"\b(?:getInstanceMap|getMapInstance)\s*\(\s*" + LITERAL_MAP_ID),
    re.compile(r"\b(?:entryMap|exitMap|recruitMap|clearMap|minMapId|maxMapId)\s*=\s*" + LITERAL_MAP_ID),
]

@dataclass(frozen=True)
class Finding:
    script: str
    line: int
    map_id: int
    snippet: str
    known_review: bool


def available_maps() -> set[int]:
    ids: set[int] = set(LIVE_IMPORTED_MAPS)
    for path in MAP_ROOT.glob("Map*/*.img.xml"):
        raw = path.name.split(".", 1)[0]
        if raw.isdigit(): ids.add(int(raw))
    return ids


def scripts() -> list[Path]:
    found: list[Path] = []
    for root in SCRIPT_ROOTS:
        if root.is_dir(): found.extend(root.rglob("*.js"))
    return sorted(set(found))


def refs_on_line(line: str) -> set[int]:
    result: set[int] = set()
    for pattern in PATTERNS: result.update(int(match) for match in pattern.findall(line))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    maps = available_maps()
    if not maps: raise SystemExit("[FAIL] No Map.wz map definitions found")

    scanned = scripts(); findings: list[Finding] = []; total_refs = 0; counts: Counter[str] = Counter()
    for path in scanned:
        relative = str(path.relative_to(ROOT)).replace("\\", "/")
        try: text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"[REVIEW] unable to read {relative}: {exc}"); continue
        for line_number, line in enumerate(text.splitlines(), 1):
            for map_id in refs_on_line(line):
                if map_id in SPECIAL_IDS: continue
                total_refs += 1
                counts[relative.split("/", 2)[1] if "/" in relative else "other"] += 1
                if map_id not in maps:
                    findings.append(Finding(relative, line_number, map_id, line.strip()[:220],
                                            (relative, map_id) in KNOWN_REVIEW_REFERENCES))

    unknown = [f for f in findings if not f.known_review]; known = [f for f in findings if f.known_review]
    payload = {
        "scriptsScanned": len(scanned), "literalMapReferences": total_refs,
        "referencesByScriptArea": dict(sorted(counts.items())), "missingReferenceCount": len(findings),
        "knownReviewCount": len(known), "unknownReviewCount": len(unknown),
        "liveImportedMapCount": len(LIVE_IMPORTED_MAPS), "findings": [asdict(f) for f in findings],
    }
    if args.json: print(json.dumps(payload, indent=2))
    else:
        print(f"EverLeaf script map-reference audit: {len(scanned)} scripts, {total_refs} literal map references, {len(findings)} references to unavailable maps")
        for f in findings[:100]:
            print(f"[{'KNOWN' if f.known_review else 'REVIEW'}] {f.script}:{f.line} -> {f.map_id} :: {f.snippet}")
        if len(findings)>100: print(f"[REVIEW] ... {len(findings)-100} additional findings omitted")
    return 1 if args.strict and unknown else 0

if __name__ == "__main__": raise SystemExit(main())
