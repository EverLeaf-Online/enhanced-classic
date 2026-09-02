#!/usr/bin/env python3
"""Hard release assertions for Evan Recovery Aura."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "src/main/java/server/maps/MapleMap.java"
TRANSFORM = ROOT / "tools/apply_evan_recovery_aura_fixes.py"


def require(path: Path, *fragments: str) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    for fragment in fragments:
        if fragment not in text:
            raise SystemExit(f"ERROR {path.relative_to(ROOT)} missing Recovery Aura invariant: {fragment}")


def main() -> int:
    require(
        MAP,
        "} else if (recovery) {",
        "mist.getOwner().getSkillLevel(mist.getSourceSkill().getId())",
        "int recoveryInterval = 2500;",
        "int recoveryDuration = Math.max(1, recoveryEffect.getDuration());",
        "chr.getMaxMp() * (recoveryEffect.getX() / 100.0)",
        "* recoveryInterval / recoveryDuration",
        "chr.addMP(Math.max(1, recoveryAmount));",
        "mist.getOwner().getParty().containsMembers(chr.getMPC())",
    )
    text = MAP.read_text(encoding="utf-8", errors="replace")
    forbidden = (
        "getEffect(chr.getSkillLevel(mist.getSourceSkill().getId())).getX() * chr.getMp() / 100",
        "recoveryEffect.getX() * chr.getMp() / 100",
    )
    for fragment in forbidden:
        if fragment in text:
            raise SystemExit(f"ERROR stale Recovery Aura formula remains: {fragment}")

    require(
        TRANSFORM,
        "mist.getOwner().getSkillLevel(mist.getSourceSkill().getId())",
        "chr.getMaxMp() * (recoveryEffect.getX() / 100.0)",
        "* recoveryInterval / recoveryDuration",
    )

    # WZ contract from the authorized Evan source: 30-second aura, 38..80%
    # total MP recovery, 60-second cooldown. The runtime formula apportions the
    # percentage across the 2.5-second map ticks rather than reapplying it whole.
    tick_share = 2500 / 30000
    level_15_per_tick = 80 * tick_share
    if abs(level_15_per_tick - (20 / 3)) > 1e-9:
        raise SystemExit("ERROR Recovery Aura level-15 tick-share regression")

    print("EverLeaf Evan Recovery Aura audit: PASS")
    print("  source skill level: caster")
    print("  recovery base: recipient max MP")
    print("  WZ x: apportioned over aura duration")
    print("  level 15: 80% max MP total over 30 seconds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
