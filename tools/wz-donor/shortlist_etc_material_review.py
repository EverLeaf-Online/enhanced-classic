#!/usr/bin/env python3
"""Create a conservative review-only shortlist of ordinary-looking v95 Etc materials.

This tool is deliberately not an approval or import classifier. It only reduces
manual review noise by selecting low-risk 400xxxx candidates whose direct WZ
shape contains icon/price metadata and no known system/restriction properties.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED_INFO_PROPERTIES = {"icon", "iconraw", "price", "slotmax"}
REQUIRED_INFO_PROPERTIES = {"icon", "iconraw", "price"}


def is_review_candidate(profile: dict) -> bool:
    content_id = str(profile.get("contentId") or "")
    info = set(profile.get("infoProperties") or [])
    return (
        profile.get("family") == "Etc"
        and profile.get("manifestRisk") == "low"
        and content_id.isdigit()
        and content_id.startswith("400")
        and bool(profile.get("name"))
        and not profile.get("duplicateOf")
        and not profile.get("specProperties")
        and REQUIRED_INFO_PROPERTIES.issubset(info)
        and info.issubset(ALLOWED_INFO_PROPERTIES)
        and profile.get("approved") is False
    )


def build_shortlist(report: dict) -> dict:
    candidates = []
    for profile in report.get("profiles", []):
        if not is_review_candidate(profile):
            continue
        candidates.append(
            {
                "contentId": str(profile["contentId"]),
                "name": profile.get("name"),
                "description": profile.get("description") or "",
                "sourcePath": profile.get("sourcePath"),
                "manifestRisk": profile.get("manifestRisk"),
                "infoProperties": profile.get("infoProperties") or [],
                "specProperties": profile.get("specProperties") or [],
                "classification": "ordinary-etc-material-review",
                "approved": False,
                "importAllowed": False,
            }
        )
    candidates.sort(key=lambda value: int(value["contentId"]))
    return {
        "schemaVersion": 1,
        "donorId": report.get("donorId"),
        "kind": "review-only-etc-material-shortlist",
        "candidateCount": len(candidates),
        "criteria": {
            "family": "Etc",
            "manifestRisk": "low",
            "idPrefix": "400",
            "requiredInfoProperties": sorted(REQUIRED_INFO_PROPERTIES),
            "allowedInfoProperties": sorted(ALLOWED_INFO_PROPERTIES),
            "specProperties": [],
            "requiresStringName": True,
            "requiresNoSemanticDuplicate": True,
            "requiresApprovedFalse": True,
        },
        "candidates": candidates,
        "approved": False,
        "automaticImport": False,
        "note": "Review shortlist only. Candidate presence does not establish gameplay usefulness, drop-source parity, client compatibility, or approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build review-only v95 Etc material shortlist")
    parser.add_argument("profile_report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = json.loads(args.profile_report.read_text(encoding="utf-8"))
    result = build_shortlist(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Review candidates: {result['candidateCount']}")
    for candidate in result["candidates"]:
        print(f"{candidate['contentId']}\t{candidate['name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
