#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify(batch: dict, profile: dict, import_manifest: dict) -> list[str]:
    errors: list[str] = []

    if batch.get("mode") != "review-only":
        errors.append("batch mode must remain review-only")
    if batch.get("automaticImport") is not False:
        errors.append("automaticImport must be false")
    if batch.get("approved") is not False:
        errors.append("batch approved must be false")

    profile_by_id = {
        str(entry.get("contentId")): entry
        for entry in profile.get("profiles", [])
        if entry.get("category") in (None, "items")
    }
    manifest_by_id = {
        str(entry.get("contentId")): entry
        for entry in import_manifest.get("candidates", [])
        if entry.get("category") == "items"
    }

    seen: set[str] = set()
    for candidate in batch.get("candidates", []):
        cid = str(candidate.get("contentId"))
        if cid in seen:
            errors.append(f"duplicate batch contentId {cid}")
            continue
        seen.add(cid)

        if candidate.get("approved") is not False:
            errors.append(f"{cid}: approved must be false")
        if candidate.get("classification") != "simple-consume":
            errors.append(f"{cid}: batch classification must be simple-consume")
        if candidate.get("family") != "Consume":
            errors.append(f"{cid}: family must be Consume")
        if candidate.get("missingDependencies"):
            errors.append(f"{cid}: batch candidate has missing dependencies")
        if candidate.get("duplicateOf"):
            errors.append(f"{cid}: batch candidate has semantic duplicates")

        p = profile_by_id.get(cid)
        if p is None:
            errors.append(f"{cid}: missing from profile")
        else:
            for key in (
                "name",
                "description",
                "sourcePath",
                "family",
                "classification",
                "restoreValues",
                "infoProperties",
                "specProperties",
                "duplicateOf",
            ):
                if candidate.get(key) != p.get(key):
                    errors.append(f"{cid}: profile mismatch for {key}")
            if p.get("approved") is not False:
                errors.append(f"{cid}: profile unexpectedly approved")
            if p.get("classification") != "simple-consume":
                errors.append(f"{cid}: current profile no longer marks simple-consume")

        m = manifest_by_id.get(cid)
        if m is None:
            errors.append(f"{cid}: missing from import manifest")
        else:
            for key in ("sourcePath", "sourceSha256"):
                if candidate.get(key) != m.get(key):
                    errors.append(f"{cid}: import manifest mismatch for {key}")
            if m.get("risk") != candidate.get("manifestRisk"):
                errors.append(f"{cid}: manifest risk changed")
            if m.get("approved") is not False:
                errors.append(f"{cid}: import manifest unexpectedly approved")
            if m.get("missingDependencies"):
                errors.append(f"{cid}: current manifest has missing dependencies")

        restore = candidate.get("restoreValues") or {}
        if not restore or set(restore) - {"hp", "mp", "hpr", "mpr"}:
            errors.append(f"{cid}: restoreValues are not HP/MP-only")
        for key, value in restore.items():
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                errors.append(f"{cid}: restore value {key} is not numeric")
                continue
            if numeric <= 0:
                errors.append(f"{cid}: restore value {key} must be positive")

    expected_ids = {"2022711", "2022712"}
    if seen != expected_ids:
        errors.append(f"batch IDs changed: expected {sorted(expected_ids)}, got {sorted(seen)}")

    simple_ids = {
        str(entry.get("contentId"))
        for entry in profile.get("profiles", [])
        if entry.get("classification") == "simple-consume"
    }
    if simple_ids != expected_ids:
        errors.append(
            f"current simple-consume set drifted: expected {sorted(expected_ids)}, got {sorted(simple_ids)}"
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a review-only WZ donor batch against freshly recomputed evidence.")
    parser.add_argument("batch", type=Path)
    parser.add_argument("profile", type=Path)
    parser.add_argument("import_manifest", type=Path)
    args = parser.parse_args()

    errors = verify(load_json(args.batch), load_json(args.profile), load_json(args.import_manifest))
    if errors:
        print("Batch verification FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    batch = load_json(args.batch)
    print(f"Batch verification passed: {batch['batchId']}")
    print("Candidates: " + ", ".join(str(c["contentId"]) for c in batch["candidates"]))
    print("Approval state: review-only / approved=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
