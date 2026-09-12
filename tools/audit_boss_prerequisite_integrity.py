#!/usr/bin/env python3
"""Static cross-check for retained major-boss prerequisite gates.

The goal is to prove existing source/WZ gates without inventing new retail
requirements. Pink Bean is intentionally reported as review-only because the
current EverLeaf recruiter gates by expedition level/size but has no explicit
quest/item prerequisite of its own.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="ignore")


def require(data: str, fragment: str, label: str) -> None:
    if fragment not in data:
        raise SystemExit(f"FAIL: {label}")


def main() -> int:
    zakum_campaign = read("scripts/npc/2030008.js")
    zakum_recruiter = read("scripts/npc/2030013.js")
    horntail_gate = read("scripts/npc/2081005.js")
    horntail_badge = read("scripts/npc/2083000.js")
    pap_reactor = read("wz/Reactor.wz/2201004.img.xml")
    pap_quest = read("wz/Quest.wz/Act.img.xml")
    pink_recruiter = read("scripts/npc/2141001.js")
    pink_event = read("scripts/event/PinkBeanBattle.js")
    empress_recruiter = read("scripts/npc/2143004.js")
    stronghold = read("scripts/npc/2143000.js")

    require(zakum_campaign, "cm.completeQuest(100201);", "Zakum campaign completion marker missing")
    require(zakum_campaign, "cm.gainItem(4001017, 5);", "Zakum Eye of Fire award missing")
    require(zakum_recruiter, "var expedItem = 4001017;", "Zakum expedition item gate missing")

    require(horntail_gate, "isTransformed(cm.getPlayer()) || cm.haveItem(4001086)",
            "Horntail cave worthiness gate missing")
    require(horntail_badge, "cm.haveItem(4001086)", "Horntail badge/certificate path missing")

    require(pap_reactor, '<int name="type" value="100"/>', "Papulatus summon reactor is not item-triggered")
    require(pap_reactor, '<int name="0" value="4031179"/>', "Papulatus summon Piece of Cracked Dimension requirement missing")
    require(pap_quest, '<int name="id" value="4031179"/>', "Papulatus quest chain does not award/handle the summon piece")

    require(pink_recruiter, "player.getLevel() < exped.getMinLevel()", "Pink Bean recruiter level gate missing")
    require(pink_event, "var minLevel = 120", "Pink Bean event level floor missing")

    require(stronghold, "EmpressStrongholdProgressService.isComplete", "Stronghold prerequisite tracking missing")
    require(empress_recruiter, "EmpressStrongholdProgressService.isComplete(player.getId())",
            "Empress recruiter does not enforce Stronghold completion")
    require(empress_recruiter, "EmpressWeeklyLockoutService.canEnter", "Empress weekly lockout gate missing")

    print("EverLeaf boss prerequisite integrity audit: PASS")
    print("  Zakum: campaign completion -> Eye of Fire -> expedition item gate")
    print("  Horntail: transformation/Badge of the Squad gate before battle access")
    print("  Papulatus: WZ item-triggered summon requires item 4031179 from the retained quest path")
    print("  Empress: Stronghold completion + account weekly lockout enforced at recruiter")
    print("[REVIEW] Pink Bean currently uses the level-120 expedition/map progression gate only;")
    print("         no additional explicit quest/item prerequisite is enforced by the recruiter.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
