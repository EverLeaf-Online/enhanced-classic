#!/usr/bin/env python3
"""Audit high-impact EverLeaf reward sources.

This static/read-only audit enforces source decisions that are already part of
EverLeaf's pre-alpha reward policy while still reporting softer balance issues
(such as duplicate Gachapon entries) for human review.
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GACHA_DIR = ROOT / "src/main/java/server/gachapon"
SCRIPTS_DIR = ROOT / "scripts"
FISHING = ROOT / "src/main/java/tools/packets/Fishing.java"
BOSS_RUSH = SCRIPTS_DIR / "event/BossRushPQ.js"
BOSS_RUSH_ANNOUNCER = SCRIPTS_DIR / "npc/9000038.js"
LEGACY_EXCHANGE = SCRIPTS_DIR / "npc/9120010.js"
BOSS_DROP_MIGRATION = ROOT / "database/sql/migration/everleaf_boss_rare_scroll_drops.sql"

CHAOS = 2049100
WHITE = 2340000
LEAF = 4001126
WATCH = {
    CHAOS: "Chaos Scroll 60%",
    WHITE: "White Scroll",
    LEAF: "Maple Leaves",
}

NORMAL_BOSS_TARGETS = {
    8500001: "Papulatus Clock",
    8510000: "Pianus",
    9420549: "Furious Scarlion",
    9420544: "Furious Targa",
    8800002: "Zakum",
    8810018: "Horntail",
    8820001: "Pink Bean",
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


def array_values(text: str, variable: str) -> list[int]:
    match = re.search(rf"\b{re.escape(variable)}\s*=\s*\[(.*?)\];", text, re.DOTALL)
    if not match:
        return []
    return [int(value) for value in re.findall(r"\b\d{7}\b", match.group(1))]


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

    for item_id in (CHAOS, WHITE):
        locations = [tier for tier, items in tiers.items() if item_id in items]
        if locations != ["rare"]:
            failures.append(
                f"{WATCH[item_id]} ({item_id}) must appear exactly in the global rare Gachapon tier; found {locations or 'none'}"
            )
        else:
            print(f"  [OK] {WATCH[item_id]} remains in global rare Gachapon pool")

    duplicate_count = 0
    class_count = 0
    reward_slots = 0
    local_rare_scroll_sources: list[str] = []
    for path in sorted(GACHA_DIR.glob("*.java")):
        if path.name in {"Gachapon.java", "GachaponItems.java"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        class_count += 1
        for tier_name, method in (("common", "getCommonItems"), ("uncommon", "getUncommonItems"), ("rare", "getRareItems")):
            items = parse_tier_items(text, method)
            reward_slots += len(items)
            if path.name != "Global.java":
                for item_id in (CHAOS, WHITE):
                    if item_id in items:
                        local_rare_scroll_sources.append(f"{path.name}:{tier_name}:{item_id}")

            counts: dict[int, int] = defaultdict(int)
            for item in items:
                counts[item] += 1
            dupes = sorted(item for item, count in counts.items() if count > 1)
            if dupes:
                duplicate_count += len(dupes)
                print(f"  [REVIEW] {path.name} {tier_name} duplicate ids: {dupes}")

    if local_rare_scroll_sources:
        failures.append(
            "Chaos/White Scroll must use the shared global rare Gachapon pool only; local copies found: "
            + ", ".join(local_rare_scroll_sources)
        )
    else:
        print("  [OK] no local Gachapon pool has an extra Chaos/White Scroll roll")

    print(f"Gachapon pool inventory: classes={class_count}, numeric reward slots={reward_slots}, duplicate ids for review={duplicate_count}")
    return failures


def audit_normal_boss_drops() -> list[str]:
    failures: list[str] = []
    if not BOSS_DROP_MIGRATION.is_file():
        return ["Missing EverLeaf normal-boss rare-scroll migration"]

    text = BOSS_DROP_MIGRATION.read_text(encoding="utf-8-sig", errors="replace")
    if str(CHAOS) not in text or str(WHITE) not in text:
        failures.append("Normal-boss migration must contain both Chaos and White Scroll item IDs")

    missing = [f"{name} ({mob_id})" for mob_id, name in NORMAL_BOSS_TARGETS.items() if str(mob_id) not in text]
    if missing:
        failures.append("Normal-boss rare-scroll migration is missing: " + ", ".join(missing))
    else:
        print("  [OK] normal bosses have tiered Chaos/White Scroll drop targets")

    # Guard against accidentally rewarding multipart/transitional Zakum/Horntail
    # bodies and therefore rolling the rare scroll several times per clear.
    forbidden = [8800000, 8800001, 8810000, 8810001]
    for mob_id in forbidden:
        # Ignore explanatory comments by checking for a VALUES-like tuple.
        if re.search(rf"\(\s*{mob_id}\s*,", text):
            failures.append(f"Transitional/multipart boss {mob_id} must not receive direct rare-scroll rows")

    return failures


def audit_controlled_sources() -> list[str]:
    failures: list[str] = []

    if not FISHING.is_file():
        failures.append("Missing Fishing.java")
    else:
        text = FISHING.read_text(encoding="utf-8-sig", errors="replace")
        for item_id in (CHAOS, WHITE):
            if re.search(rf"\b{item_id}\b", text):
                failures.append(f"{WATCH[item_id]} ({item_id}) is still present in Fishing.java")
        if not any(re.search(rf"\b{item_id}\b", text) for item_id in (CHAOS, WHITE)):
            print("  [OK] fishing has no Chaos/White Scroll faucet")

    if not LEGACY_EXCHANGE.is_file():
        failures.append("Missing scripts/npc/9120010.js")
    else:
        text = LEGACY_EXCHANGE.read_text(encoding="utf-8-sig", errors="replace")
        if re.search(rf"\b{WHITE}\b", text):
            failures.append("White Scroll is still present in the legacy Boss Pomade exchange")
        else:
            print("  [OK] legacy Boss Pomade exchange has no White Scroll")

    if not BOSS_RUSH.is_file():
        failures.append("Missing BossRushPQ.js")
    else:
        text = BOSS_RUSH.read_text(encoding="utf-8-sig", errors="replace")
        level6_match = re.search(r"evLevel\s*=\s*6;.*?itemSet\s*=\s*\[(.*?)\];", text, re.DOTALL)
        level5_match = re.search(r"evLevel\s*=\s*5;.*?itemSet\s*=\s*\[(.*?)\];", text, re.DOTALL)
        level6 = [int(x) for x in re.findall(r"\b\d{7}\b", level6_match.group(1))] if level6_match else []
        level5 = [int(x) for x in re.findall(r"\b\d{7}\b", level5_match.group(1))] if level5_match else []
        if CHAOS not in level6 or WHITE not in level6:
            failures.append("Boss Rush final reward tier must contain both Chaos and White Scroll")
        if CHAOS not in level5:
            failures.append("Boss Rush Rest Spot V must retain Chaos Scroll")
        if WHITE in level5:
            failures.append("White Scroll must remain final-tier-only in Boss Rush")
        if CHAOS in level6 and WHITE in level6 and CHAOS in level5 and WHITE not in level5:
            print("  [OK] Boss Rush: Chaos at Rest V/final; White final-only")

    if not BOSS_RUSH_ANNOUNCER.is_file():
        failures.append("Missing Boss Rush reward announcer 9000038.js")
    else:
        text = BOSS_RUSH_ANNOUNCER.read_text(encoding="utf-8-sig", errors="replace")
        lv6 = array_values(text, "itemSet_lv6")
        lv5 = array_values(text, "itemSet_lv5")
        if CHAOS not in lv6 or WHITE not in lv6 or CHAOS not in lv5 or WHITE in lv5:
            failures.append("Boss Rush reward announcer is out of sync with the rare-scroll reward policy")
        else:
            print("  [OK] Boss Rush reward announcer matches actual rare-scroll tiers")

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
    failures.extend(audit_normal_boss_drops())
    failures.extend(audit_controlled_sources())
    audit_authored_sources()

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1

    print("Reward-source invariants: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
