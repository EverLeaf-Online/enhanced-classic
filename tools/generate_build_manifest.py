#!/usr/bin/env python3
"""Generate a small deployment manifest for Everleaf CI artifacts."""
import json
import os
from pathlib import Path

manifest = {
    "name": "Everleaf",
    "edition": "Enhanced Classic v83",
    "protocolVersion": 83,
    "levelCap": 250,
    "developmentRates": {
        "exp": 5,
        "meso": 3,
        "drop": 2,
        "bossDrop": 2,
        "quest": 1,
    },
    "gitSha": os.environ.get("GITHUB_SHA", "local"),
    "gitRef": os.environ.get("GITHUB_REF", "local"),
}

output = Path("target/everleaf-build.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {output}")
