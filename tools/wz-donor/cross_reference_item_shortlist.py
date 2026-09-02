#!/usr/bin/env python3
"""Cross-reference review-only item candidates against donor and baseline content.

This is evidence tooling, not an approval classifier. Numeric references are
reported conservatively so reviewers can spot quest/content coupling before any
candidate is considered for a backport batch.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

DONOR_FAMILIES = ("Quest.wz", "Map.wz", "Mob.wz", "Npc.wz", "Reactor.wz")
BASELINE_PATHS = (
    "scripts",
    "sql",
    "src",
    "wz/Quest.wz",
    "wz/Map.wz",
    "wz/Mob.wz",
    "wz/Npc.wz",
    "wz/Reactor.wz",
)
TEXT_SUFFIXES = {".xml", ".js", ".java", ".sql", ".py", ".properties", ".txt", ".json"}


def iter_text_files(root: Path, relative_roots: tuple[str, ...]):
    for relative in relative_roots:
        base = root / relative
        if not base.exists():
            continue
        if base.is_file():
            if base.suffix.lower() in TEXT_SUFFIXES:
                yield base
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                yield path


def scan_references(ids: list[str], root: Path, relative_roots: tuple[str, ...], sample_limit: int) -> dict[str, dict]:
    results = {
        content_id: {"referenceCount": 0, "fileCount": 0, "byRoot": Counter(), "samples": []}
        for content_id in ids
    }
    if not ids:
        return results

    alternation = "|".join(re.escape(content_id) for content_id in sorted(ids, key=len, reverse=True))
    pattern = re.compile(rf"(?<!\d)(?:{alternation})(?!\d)")

    for path in iter_text_files(root, relative_roots):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        matches = [match.group(0) for match in pattern.finditer(text)]
        if not matches:
            continue
        relative = path.relative_to(root).as_posix()
        top = relative.split("/", 1)[0]
        per_id = Counter(matches)
        for content_id, count in per_id.items():
            result = results[content_id]
            result["referenceCount"] += count
            result["fileCount"] += 1
            result["byRoot"][top] += count
            if len(result["samples"]) < sample_limit:
                result["samples"].append({"path": relative, "matches": count})

    for result in results.values():
        result["byRoot"] = dict(sorted(result["byRoot"].items()))
    return results


def build_report(shortlist: dict, donor_root: Path, baseline_root: Path, sample_limit: int = 12) -> dict:
    candidates = shortlist.get("candidates", [])
    ids = [str(candidate["contentId"]) for candidate in candidates]
    donor = scan_references(ids, donor_root, DONOR_FAMILIES, sample_limit)
    baseline = scan_references(ids, baseline_root, BASELINE_PATHS, sample_limit)

    rows = []
    coupled_count = 0
    quest_coupled_count = 0
    for candidate in candidates:
        content_id = str(candidate["contentId"])
        donor_result = donor[content_id]
        baseline_result = baseline[content_id]
        donor_quest_refs = donor_result["byRoot"].get("Quest.wz", 0)
        coupled = donor_result["referenceCount"] > 0 or baseline_result["referenceCount"] > 0
        quest_coupled = donor_quest_refs > 0
        if coupled:
            coupled_count += 1
        if quest_coupled:
            quest_coupled_count += 1
        rows.append(
            {
                "contentId": content_id,
                "name": candidate.get("name"),
                "donorReferences": donor_result,
                "baselineReferences": baseline_result,
                "hasAnyCrossReference": coupled,
                "hasDonorQuestReference": quest_coupled,
                "approved": False,
                "importAllowed": False,
            }
        )

    return {
        "schemaVersion": 1,
        "kind": "review-only-item-cross-reference-report",
        "donorId": shortlist.get("donorId"),
        "candidateCount": len(rows),
        "crossReferencedCandidateCount": coupled_count,
        "donorQuestReferencedCandidateCount": quest_coupled_count,
        "uncoupledCandidateCount": len(rows) - coupled_count,
        "scanScope": {
            "donorRoots": list(DONOR_FAMILIES),
            "baselineRoots": list(BASELINE_PATHS),
            "matchRule": "numeric token boundary; review evidence only",
        },
        "candidates": rows,
        "approved": False,
        "automaticImport": False,
        "note": "Cross-reference absence does not prove safety. Presence indicates content coupling that requires manual dependency review.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-reference an item review shortlist")
    parser.add_argument("shortlist", type=Path)
    parser.add_argument("--donor", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-limit", type=int, default=12)
    args = parser.parse_args()

    shortlist = json.loads(args.shortlist.read_text(encoding="utf-8"))
    report = build_report(shortlist, args.donor, args.baseline, max(1, args.sample_limit))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Candidates: {report['candidateCount']}")
    print(f"Cross-referenced: {report['crossReferencedCandidateCount']}")
    print(f"Donor quest-referenced: {report['donorQuestReferencedCandidateCount']}")
    print(f"No scanned references: {report['uncoupledCandidateCount']}")
    for row in report["candidates"]:
        if row["hasAnyCrossReference"]:
            print(
                f"{row['contentId']}\t{row.get('name') or ''}\t"
                f"donor={row['donorReferences']['referenceCount']}\t"
                f"baseline={row['baselineReferences']['referenceCount']}\t"
                f"quest={str(row['hasDonorQuestReference']).lower()}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
