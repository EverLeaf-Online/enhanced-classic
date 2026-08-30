#!/usr/bin/env python3
"""Enable EverLeaf instant transport rides in a persistent config file."""

import re
import sys
from pathlib import Path


def enable_instant_travel(text: str) -> str:
    existing = re.findall(r"(?m)^\s*instant_travel:\s*(?:true|false)\s*(?:#.*)?$", text)
    if len(existing) > 1:
        raise ValueError("Multiple instant_travel settings found")
    if existing:
        return re.sub(
            r"(?m)^(\s*)instant_travel:\s*(?:true|false)\s*(?:#.*)?$",
            r"\1instant_travel: true                   # Complete transport rides after a safe one-second transition.",
            text,
            count=1,
        )

    travel_line = re.search(r"(?m)^(\s*)travel_rate:\s*\d+\s*(?:#.*)?$", text)
    if travel_line is None:
        raise ValueError("travel_rate setting not found")

    indent = travel_line.group(1)
    addition = f"\n{indent}instant_travel: true                   # Complete transport rides after a safe one-second transition."
    return text[:travel_line.end()] + addition + text[travel_line.end():]


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: enable_instant_travel.py <config.yaml>")

    path = Path(sys.argv[1])
    original = path.read_text(encoding="utf-8-sig")
    updated = enable_instant_travel(original)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        print("Enabled instant transportation rides.")


if __name__ == "__main__":
    main()
