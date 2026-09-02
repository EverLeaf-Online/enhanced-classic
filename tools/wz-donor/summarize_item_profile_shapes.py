#!/usr/bin/env python3
"""Summarize structural shapes in a review-only WZ item profile report."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def shape_key(profile: dict) -> tuple:
    return (
        profile.get("manifestRisk"),
        tuple(sorted(profile.get("infoProperties") or [])),
        tuple(sorted(profile.get("specProperties") or [])),
        bool(profile.get("name")),
    )


def summarize(report: dict, family: str, sample_limit: int = 8) -> dict:
    selected = [p for p in report.get("profiles", []) if p.get("family") == family]
    counts: Counter[tuple] = Counter(shape_key(p) for p in selected)
    samples: dict[tuple, list[dict]] = defaultdict(list)
    for profile in selected:
        key = shape_key(profile)
        if len(samples[key]) < sample_limit:
            samples[key].append({
                "contentId": str(profile.get("contentId")),
                "name": profile.get("name"),
                "classification": profile.get("classification"),
                "reasons": profile.get("reasons") or [],
            })

    shapes = []
    for key, count in counts.most_common():
        risk, info_props, spec_props, has_name = key
        shapes.append({
            "count": count,
            "manifestRisk": risk,
            "infoProperties": list(info_props),
            "specProperties": list(spec_props),
            "hasStringName": has_name,
            "samples": samples[key],
        })

    return {
        "schemaVersion": 1,
        "donorId": report.get("donorId"),
        "mode": "review-only",
        "family": family,
        "profileCount": len(selected),
        "shapeCount": len(shapes),
        "shapes": shapes,
        "automaticImport": False,
        "note": "Structural frequency report only; no shape is automatically safe or approved.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize item profile structural shapes")
    parser.add_argument("profile_report", type=Path)
    parser.add_argument("--family", default="Etc")
    parser.add_argument("--sample-limit", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = json.loads(args.profile_report.read_text(encoding="utf-8"))
    summary = summarize(report, args.family, args.sample_limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Family: {summary['family']}")
    print(f"Profiles: {summary['profileCount']}")
    print(f"Distinct shapes: {summary['shapeCount']}")
    for index, shape in enumerate(summary["shapes"][:20], start=1):
        print(
            f"{index}. count={shape['count']} risk={shape['manifestRisk']} "
            f"info={','.join(shape['infoProperties']) or '-'} "
            f"spec={','.join(shape['specProperties']) or '-'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
