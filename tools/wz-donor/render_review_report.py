#!/usr/bin/env python3
"""Render a concise Markdown review report from WZ donor diff + import manifest JSON."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

RISK_ORDER = ("low", "medium", "high", "blocked")
CATEGORY_ORDER = ("equipment", "items", "npcs", "mobs", "reactors", "maps", "quests", "skills")


def _count_category_rows(manifest: dict) -> dict[str, Counter]:
    rows: dict[str, Counter] = {}
    for candidate in manifest.get("candidates", []):
        category = str(candidate.get("category", "unknown"))
        risk = str(candidate.get("risk", "unknown"))
        rows.setdefault(category, Counter())[risk] += 1
    return rows


def render(diff: dict, manifest: dict, *, sample_limit: int = 12) -> str:
    donor = manifest.get("donorId") or diff.get("donorId") or "unknown-donor"
    totals = diff.get("totals", {})
    dependencies = diff.get("dependencies", {})
    risk_counts = manifest.get("riskCounts", {})
    candidate_count = int(manifest.get("candidateCount", len(manifest.get("candidates", []))))

    lines = [
        f"# EverLeaf WZ donor review — {donor}",
        "",
        "> Review-only report. No candidate is approved or imported by this report.",
        "",
        "## Summary",
        "",
        f"- Candidates: **{candidate_count:,}**",
        f"- New IDs: **{int(totals.get('newIds', 0)):,}**",
        f"- Collisions: **{int(totals.get('collisionIds', 0)):,}**",
        f"- Changed collisions: **{int(totals.get('changedCollisionIds', 0)):,}**",
        f"- Missing dependency references: **{int(dependencies.get('missingReferenceCount', 0)):,}**",
        "- Risk: " + ", ".join(f"{risk} **{int(risk_counts.get(risk, 0)):,}**" for risk in RISK_ORDER),
        "",
        "## Candidate breakdown",
        "",
        "| Category | Low | Medium | High | Blocked | Total |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    rows = _count_category_rows(manifest)
    ordered_categories = [c for c in CATEGORY_ORDER if c in rows] + sorted(set(rows) - set(CATEGORY_ORDER))
    for category in ordered_categories:
        counts = rows[category]
        total = sum(counts.values())
        lines.append(
            f"| {category} | {counts['low']:,} | {counts['medium']:,} | {counts['high']:,} | {counts['blocked']:,} | {total:,} |"
        )

    blocked = [c for c in manifest.get("candidates", []) if c.get("risk") == "blocked"]
    lines.extend(["", "## Blocked dependency samples", ""])
    if not blocked:
        lines.append("No blocked candidates were reported.")
    else:
        for candidate in blocked[:sample_limit]:
            deps = candidate.get("missingDependencies", [])
            dep_text = "; ".join(
                f"{d.get('target_category', '?')}:{d.get('target_id', '?')}"
                for d in deps[:5]
            ) or "unspecified dependency"
            lines.append(
                f"- `{candidate.get('category')}:{candidate.get('contentId')}` — {dep_text}"
            )
        if len(blocked) > sample_limit:
            lines.append(f"- …and {len(blocked) - sample_limit:,} more blocked candidates in the JSON manifest.")

    lines.extend(["", "## Lowest-risk review queue", ""])
    low = [c for c in manifest.get("candidates", []) if c.get("risk") == "low"]
    if not low:
        lines.append("No low-risk candidates were reported.")
    else:
        for candidate in low[:sample_limit]:
            lines.append(
                f"- [ ] `{candidate.get('category')}:{candidate.get('contentId')}` — `{candidate.get('sourcePath')}`"
            )
        if len(low) > sample_limit:
            lines.append(f"- …and {len(low) - sample_limit:,} more low-risk candidates in the JSON manifest.")

    lines.extend(
        [
            "",
            "## Review rule",
            "",
            "All manifest entries remain `approved=false`. Blocked entries must have their missing dependencies resolved before they can be considered for staging. This report never mutates EverLeaf WZ data.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a Markdown review report for a WZ donor analysis.")
    parser.add_argument("diff", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, default=Path("tools/output/wz-donor-review.md"))
    parser.add_argument("--sample-limit", type=int, default=12)
    args = parser.parse_args()

    if args.sample_limit < 0:
        parser.error("--sample-limit must be >= 0")

    diff = json.loads(args.diff.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    text = render(diff, manifest, sample_limit=args.sample_limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(f"Review report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
