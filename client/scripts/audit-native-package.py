#!/usr/bin/env python3
"""Read-only native candidate audit. A pass does not certify UI or runtime QA."""
import argparse
import hashlib
import json
from pathlib import Path

TOKENS = ("yuna", "yunams", "yuna.ms", "mapleezorsia", "ezorsia", "redly",
          "solomapling", "madara", "gameguard")
DONOR_FILES = {"yunams.exe", "yunams.dll", "yunamsw.dll", "settings.ini",
               "version.data", "backups.rar", "fixmodifierkeys.bat", "run_fixes.reg"}
REQUIRED = {"everleaf.exe", "dinput8.dll", "ui.wz", "map.wz", "item.wz",
            "mob.wz", "skill.wz", "string.wz", "config.ini"}
# UI is the only donor replacement approved for this candidate. All other
# production payloads, including v95 data and the native runtime, must match.
ALLOWED_CHANGES = {"ui.wz"}
CHUNK = 1024 * 1024

def fingerprint(path):
    digest = hashlib.sha256()
    hits = set()
    patterns = [(token, token.encode(encoding))
                for token in TOKENS for encoding in ("ascii", "utf-16le")]
    overlap = max(len(pattern) for _, pattern in patterns) - 1
    tail = b""
    with path.open("rb") as source:
        while True:
            block = source.read(CHUNK)
            if not block:
                break
            digest.update(block)
            window = (tail + block).lower()
            hits.update(token for token, pattern in patterns if pattern in window)
            tail = window[-overlap:]
    return digest.hexdigest(), sorted(hits)

def inventory(root):
    files, errors = {}, []
    for path in sorted(root.iterdir()):
        if path.is_symlink() or not path.is_file():
            errors.append("Unexpected non-regular entry: " + path.name)
            continue
        key = path.name.casefold()
        if key in files:
            errors.append("Windows filename collision: " + path.name)
        files[key] = path
    return files, errors

def audit(candidate, baseline):
    current, errors = inventory(candidate)
    reference, baseline_errors = inventory(baseline)
    errors.extend("Baseline: " + error for error in baseline_errors)
    for name in sorted(REQUIRED - current.keys()):
        errors.append("Missing required candidate file: " + name)
    for name in sorted(REQUIRED - reference.keys()):
        errors.append("Missing required baseline file: " + name)
    records, review = [], []
    for name, path in current.items():
        digest, hits = fingerprint(path)
        original = reference.get(name)
        baseline_hash = fingerprint(original)[0] if original else None
        if name in DONOR_FILES or name.startswith("yunams"):
            errors.append("Forbidden donor runtime/support file: " + path.name)
        if original is None:
            errors.append("Unapproved additional file: " + path.name)
        elif digest != baseline_hash and name not in ALLOWED_CHANGES:
            errors.append("Protected production file differs: " + path.name)
        if hits:
            review.append({"file": path.name, "tokens": hits,
                           "sameAsBaseline": digest == baseline_hash,
                           "interpretation": "Raw byte match; inspect decoded resources before classifying branding."})
        records.append({"file": path.name, "bytes": path.stat().st_size,
                        "sha256": digest, "baselineSha256": baseline_hash,
                        "sameAsBaseline": digest == baseline_hash})
    for name in sorted(reference.keys() - current.keys()):
        errors.append("Production file omitted: " + reference[name].name)
    return {"schemaVersion": 1, "candidate": str(candidate.resolve()),
            "baseline": str(baseline.resolve()),
            "structuralAndPreservationChecksPassed": not errors,
            "releaseReady": False,
            "unverified": ["Decoded WZ branding and connected panorama",
                           "Windows startup and login/world/character/map QA",
                           "EverLeaf Discord integration and application configuration"],
            "errors": errors, "rawBrandingMatchesForReview": review,
            "files": records}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    for root in (args.candidate, args.baseline):
        if not root.is_dir():
            parser.error("Not a directory: " + str(root))
        if args.report.resolve().is_relative_to(root.resolve()):
            parser.error("Report must be outside both audited directories")
    report = audit(args.candidate, args.baseline)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in
                     ("structuralAndPreservationChecksPassed", "releaseReady", "errors",
                      "rawBrandingMatchesForReview")}, indent=2))
    return 0 if report["structuralAndPreservationChecksPassed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
