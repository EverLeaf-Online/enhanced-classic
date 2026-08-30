#!/usr/bin/env python3
"""Review literal map references used by EverLeaf scripts.

The WZ world audit validates map-to-map portal data. This companion audit scans
server scripts for literal map IDs used by NPCs, events, portals, quests, and
reactors. Dynamic arithmetic and event-instance map allocation are deliberately
left as review-only because they cannot be proven safely with regex alone.

By default findings are reported without failing CI. Use --strict only after a
finding has been triaged and the allowlist is complete.
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

# Explicit non-map constants/sentinels that commonly appear in map APIs.
SPECIAL_IDS = {-1, 0, 999999999}

# Known legacy Boss Rush target is already documented by audit_world_integrity.
KNOWN_REVIEW_REFERENCES = {
    ("scripts/portal/raid_stage.js", 970033001),
}

# A reference is literal only when the numeric token is not immediately used as
# the base of an arithmetic expression. For example, getMap(970030100 + lobby)
# is dynamic allocation and must not be reported as if 970030100 itself were the
# final target map.
LITERAL_MAP_ID = r"(\d{6,9})\b(?!\s*[+\-*/%])"

# Match only APIs where a numeric literal is in map-id position. Keep this list
# narrow rather than treating every 9-digit number in scripts as a map.
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
    ids: set[int] = set()
    for path in MAP_ROOT.glob("Map*/*.img.xml"):
        raw = path.name.split(".", 1)[0]
        if raw.isdigit():
            ids.add(int(raw))
    return ids


def scripts() -> list[Path]:
    found: list[Path] = []
    for root in SCRIPT_ROOTS:
        if root.is_dir():
            found.extend(root.rglob("*.js"))
    return sorted(set(found))


def refs_on_line(line: str) -> set[int]:
    result: set[int] = set()
    for pattern in PATTERNS:
        result.update(int(match) for match in pattern.findall(line))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    maps = available_maps()
    if not maps:
        raise SystemExit("[FAIL] No Map.wz map definitions found")

    scanned = scripts()
    findings: list[Finding] = []
    total_refs = 0
    counts: Counter[str] = Counter()

    for path in scanned:
        relative = str(path.relative_to(ROOT)).replace("\\", "/")
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"[REVIEW] unable to read {relative}: {exc}")
            continue

        for line_number, line in enumerate(text.splitlines(), 1):
            for map_id in refs_on_line(line):
                if map_id in SPECIAL_IDS:
                    continue
                total_refs += 1
                counts[relative.split("/", 2)[1] if "/" in relative else "other"] += 1
                if map_id not in maps:
                    findings.append(Finding(
                        script=relative,
                        line=line_number,
                        map_id=map_id,
                        snippet=line.strip()[:220],
                        known_review=(relative, map_id) in KNOWN_REVIEW_REFERENCES,
                    ))

    unknown = [finding for finding in findings if not finding.known_review]
    known = [finding for finding in findings if finding.known_review]
    payload = {
        "scriptsScanned": len(scanned),
        "literalMapReferences": total_refs,
        "referencesByScriptArea": dict(sorted(counts.items())),
        "missingReferenceCount": len(findings),
        "knownReviewCount": len(known),
        "unknownReviewCount": len(unknown),
        "findings": [asdict(finding) for finding in findings],
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            "EverLeaf script map-reference audit: "
            f"{len(scanned)} scripts, {total_refs} literal map references, "
            f"{len(findings)} references to maps absent from current Map.wz"
        )
        for finding in findings[:100]:
            label = "KNOWN" if finding.known_review else "REVIEW"
            print(
                f"[{label}] {finding.script}:{finding.line} -> {finding.map_id} :: "
                f"{finding.snippet}"
            )
        if len(findings) > 100:
            print(f"[REVIEW] ... {len(findings) - 100} additional findings omitted")

    return 1 if args.strict and unknown else 0


if __name__ == "__main__":
    raise SystemExit(main())
