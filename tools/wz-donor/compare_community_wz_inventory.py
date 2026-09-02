#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare staged community WZ hashes to the current launcher payload.")
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    lines = args.inventory.read_text(errors="replace").splitlines()
    section = None
    donor: dict[str, dict[str, str]] = {}
    current: dict[str, list[dict[str, str]]] = {}

    for line in lines:
        if line.startswith("=== "):
            section = line
            continue
        if not line.strip():
            continue
        if section == "=== COMMUNITY SHA256 ===":
            match = re.match(r"([0-9a-f]{64})\s+(.+)$", line)
            if match:
                donor[Path(match.group(2)).name.lower()] = {
                    "sha256": match.group(1),
                    "path": match.group(2),
                }
        elif section == "=== CURRENT LAUNCHER SHA256 ===":
            match = re.match(r"([0-9a-f]{64})\s+(.+)$", line)
            if match:
                current.setdefault(Path(match.group(2)).name.lower(), []).append(
                    {"sha256": match.group(1), "path": match.group(2)}
                )

    rows = []
    for name in sorted(donor):
        current_copies = current.get(name, [])
        identical = any(copy["sha256"] == donor[name]["sha256"] for copy in current_copies)
        status = "identical" if identical else ("different" if current_copies else "missing-from-current-patch")
        rows.append(
            {
                "name": name,
                "donorSha256": donor[name]["sha256"],
                "donorPath": donor[name]["path"],
                "currentCopies": current_copies,
                "status": status,
            }
        )

    report = {
        "donorCount": len(donor),
        "currentDistinctWzNames": len(current),
        "identical": sum(row["status"] == "identical" for row in rows),
        "different": sum(row["status"] == "different" for row in rows),
        "missingFromCurrentPatch": sum(row["status"] == "missing-from-current-patch" for row in rows),
        "files": rows,
    }
    args.json_output.write_text(json.dumps(report, indent=2) + "\n")

    markdown = [
        "# Community WZ staging analysis",
        "",
        f"- Donor WZ files: **{report['donorCount']}**",
        f"- Identical to current launcher payload: **{report['identical']}**",
        f"- Different from current launcher payload: **{report['different']}**",
        f"- Missing from current launcher payload: **{report['missingFromCurrentPatch']}**",
        "",
        "| WZ | Status |",
        "|---|---|",
    ]
    markdown.extend(f"| `{row['name']}` | {row['status']} |" for row in rows)
    markdown.extend(["", "> Analysis only. No live files are modified by this workflow."])
    args.markdown_output.write_text("\n".join(markdown) + "\n")


if __name__ == "__main__":
    main()
