#!/usr/bin/env python3
"""Audit high-impact EverLeaf reward sources.

This is a static/read-only audit. It intentionally reports authored sources
without trying to decide balance from filenames alone. Hard failures are kept
for policy invariants we have already decided (rare scrolls stay rare in gacha,
and ordinary global mob drops are removed by the separate economy migration).
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GACHA_DIR = ROOT / "src/main/java/server/gachapon"
SCRIPTS_DIR = ROOT / "scripts"

WATCH = {
    2049100: "Chaos Scroll 60%",
    2340000: "White Scroll",
    4001126: "Maple Leaves",
}


def files_containing(root: Path, needle: str) -> list[Path]:
    matches: list[Path] = []
    if not root.exists():
        return matches
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".java", ".js", ".sql", ".txt", ".xml"}:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        if needle in text:
            matches.append(path)
    return sorted(matches)


def parse_tier_items(text: str, method: str) -> list[int]:
    pattern = rf"{method}\s*\(\s*\)\s*\{{.*?return\s+new\s+int\[\]\s*\{{(.*?)\}};"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []
    body = re.sub(r"/\*.*?\*/", " ", match.group(1), flags=re.DOTALL)
    body = re.sub(r"//.*", " ", body)
    return [int(value) for value in re.findall(r"\b\d{7}\b", body)]


def audit_gacha() -> list[str]:
    failures: list[str] = []
    global_file = GACHA_DIR / "Global.java"
    if not global_file.is_file():
        return ["Missing src/main/java/server/gachapon/Global.java"]

    global_text = global_file.read_text(encoding="utf-8-sig", errors="replace")
    tiers = {
        "common": parse_tier_items(global_text, "getCommonItems"),
        "uncommon": parse_tier_items(global_text, "getUncommonItems"),
        "rare": parse_tier_items(global_text, "getRareItems"),
    }

    print("Gachapon global pool:")
    for tier, items in tiers.items():
        print(f"  {tier}: {len(items)} numeric item ids")

    for item_id in (2049100, 2340000):
        locations = [tier for tier, items in tiers.items() if item_id in items]
        if locations != ["rare"]:
            failures.append(
                f"{WATCH[item_id]} ({item_id}) must appear exactly in the global rare Gachapon tier; found {locations or 'none'}"
            )
        else:
            print(f"  [OK] {WATCH[item_id]} remains in global rare Gachapon pool")

    # Inventory every gacha pool and report duplicates within a tier. Duplicate
    # entries alter effective probability and are easy to introduce silently.
    duplicate_count = 0
    class_count = 0
    reward_slots = 0
    for path in sorted(GACHA_DIR.glob("*.java")):
        if path.name in {"Gachapon.java", "GachaponItems.java"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        class_count += 1
        for tier_name, method in (("common", "getCommonItems"), ("uncommon", "getUncommonItems"), ("rare", "getRareItems")):
            items = parse_tier_items(text, method)
            reward_slots += len(items)
            counts: dict[int, int] = defaultdict(int)
            for item in items:
                counts[item] += 1
            dupes = sorted(item for item, count in counts.items() if count > 1)
            if dupes:
                duplicate_count += len(dupes)
                print(f"  [REVIEW] {path.name} {tier_name} duplicate ids: {dupes}")

    print(f"Gachapon pool inventory: classes={class_count}, numeric reward slots={reward_slots}, duplicate ids for review={duplicate_count}")
    return failures


def audit_authored_sources() -> None:
    print("Authored high-impact reward sources:")
    for item_id, label in WATCH.items():
        gacha_matches = files_containing(GACHA_DIR, str(item_id))
        script_matches = files_containing(SCRIPTS_DIR, str(item_id))
        print(f"  {label} ({item_id})")
        print(f"    gachapon files: {len(gacha_matches)}")
        for path in gacha_matches:
            print(f"      - {path.relative_to(ROOT)}")
        print(f"    script files: {len(script_matches)}")
        for path in script_matches:
            print(f"      - {path.relative_to(ROOT)}")


def audit_gacha_tier_split() -> list[str]:
    path = GACHA_DIR / "Gachapon.java"
    if not path.is_file():
        return ["Missing Gachapon.java"]
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    # All normal machines currently use 90/8/2. This is an intentional audit
    # invariant while reward contents are being balanced.
    tuples = re.findall(r"\b[A-Z_]+\([^\n]*?,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*new\s+\w+\(\)\)", text)
    normal = [tuple(map(int, t)) for t in tuples if tuple(map(int, t)) != (-1, -1, -1)]
    bad = [t for t in normal if t != (90, 8, 2)]
    print(f"Gachapon tier split: machines={len(normal)}, expected=90/8/2")
    return [f"Unexpected Gachapon tier splits: {bad}"] if bad else []


def main() -> int:
    print("EverLeaf reward-source audit")
    failures: list[str] = []
    failures.extend(audit_gacha())
    failures.extend(audit_gacha_tier_split())
    audit_authored_sources()

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1

    print("Reward-source invariants: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
