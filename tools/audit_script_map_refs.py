#!/usr/bin/env python3
"""Audit literal map references in EverLeaf JavaScript content.

The audit is deliberately conservative. It recognizes only explicit numeric map
IDs passed to common map/warp APIs. Dynamic expressions are ignored. Missing
references are review findings by default because the v83 script corpus contains
legacy and dormant event content. Use --strict after findings have been
classified to turn non-excluded missing references into a failing gate.

EverLeaf intentionally excludes Empress / Knights of Cygnus content. Literal
references into the Ereve/Cygnus 130xxxxxx map family are reported as excluded
and never fail strict mode.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_ROOT = ROOT / "wz" / "Map.wz" / "Map"
SCRIPT_ROOT = ROOT / "scripts"

MAP_CALL = re.compile(
    r"\b(?:cm|qm|pm|em|eim|ms)\."
    r"(?:warp|warpParty|warpMap|warpEveryone|changeMap|getMap)"
    r"\s*\(\s*(\d{6,9})\b"
)
FACTORY_MAP_CALL = re.compile(r"\bgetMap\s*\(\s*(\d{6,9})\b")


@dataclass(frozen=True)
class Finding:
    status: str
    script: str
    line: int
    map_id: int
    call: str


def available_maps() -> set[int]:
    maps: set[int] = set()
    for path in MAP_ROOT.glob("Map*/*.img.xml"):
        raw = path.name.split(".", 1)[0]
        if raw.isdigit():
            maps.add(int(raw))
    return maps


def excluded_map(map_id: int) -> bool:
    return 130_000_000 <= map_id < 131_000_000


def scan_file(path: Path, maps: set[int]) -> tuple[int, list[Finding]]:
    findings: list[Finding] = []
    references = 0
    text = path.read_text(encoding="utf-8", errors="replace")
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            continue

        matches = list(MAP_CALL.finditer(line))
        occupied = {(m.start(1), m.end(1)) for m in matches}
        matches.extend(
            m for m in FACTORY_MAP_CALL.finditer(line)
            if (m.start(1), m.end(1)) not in occupied
        )

        for match in matches:
            references += 1
            map_id = int(match.group(1))
            if map_id in maps:
                continue
            status = "EXCLUDED" if excluded_map(map_id) else "REVIEW"
            findings.append(Finding(
                status=status,
                script=str(path.relative_to(ROOT)).replace("\\", "/"),
                line=number,
                map_id=map_id,
                call=line.strip()[:240],
            ))
    return references, findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="fail on non-excluded missing literal map references")
    args = parser.parse_args()

    if not MAP_ROOT.is_dir() or not SCRIPT_ROOT.is_dir():
        print("EverLeaf map/script roots are unavailable.")
        return 2

    maps = available_maps()
    findings: list[Finding] = []
    references = 0
    scripts = 0
    for path in sorted(SCRIPT_ROOT.rglob("*.js")):
        scripts += 1
        count, found = scan_file(path, maps)
        references += count
        findings.extend(found)

    review = [finding for finding in findings if finding.status == "REVIEW"]
    excluded = [finding for finding in findings if finding.status == "EXCLUDED"]
    payload = {
        "scriptsScanned": scripts,
        "mapsIndexed": len(maps),
        "literalMapReferences": references,
        "reviewFindingCount": len(review),
        "excludedFindingCount": len(excluded),
        "strictFailureCount": len(review) if args.strict else 0,
        "findings": [asdict(finding) for finding in findings],
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            f"EverLeaf script map audit: {scripts} scripts, {references} literal map references, "
            f"{len(review)} review findings, {len(excluded)} excluded Empress/Cygnus findings"
        )
        for finding in review[:100]:
            print(f"[REVIEW] {finding.script}:{finding.line} -> missing map {finding.map_id}: {finding.call}")
        if len(review) > 100:
            print(f"[REVIEW] ... {len(review) - 100} additional findings omitted")

    return 1 if args.strict and review else 0


if __name__ == "__main__":
    raise SystemExit(main())
