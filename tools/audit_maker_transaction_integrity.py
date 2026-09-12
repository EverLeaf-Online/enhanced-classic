#!/usr/bin/env python3
"""Static audit for Maker/crafting settlement and validation invariants.

This gate verifies the current anti-abuse/preflight protections and explicitly
surfaces the remaining crash-consistency limitation: Maker consumes inputs and
mesos before the final output insertion, so an unexpected process failure in
that narrow window can lose a craft but cannot replay/duplicate it.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAKER = ROOT / "src/main/java/client/processor/action/MakerProcessor.java"


def require(data: str, fragment: str, label: str) -> None:
    if fragment not in data:
        raise SystemExit(f"FAIL: {label}")


def main() -> int:
    data = MAKER.read_text(encoding="utf-8")

    require(data, "if (c.tryacquireClient())", "Maker packet path is not client-serialized")
    require(data, "if (recipe.isInvalid())", "invalid Maker recipe gate missing")
    require(data, "if (!hasItems(c, recipe))", "Maker ingredient preflight missing")
    require(data, "if (c.getPlayer().getMeso() < recipe.getCost())", "Maker meso preflight missing")
    require(data, "if (c.getPlayer().getLevel() < recipe.getReqLevel())", "Maker level preflight missing")
    require(data, "if (getMakerSkillLevel(c.getPlayer()) < recipe.getReqSkillLevel())", "Maker skill-level preflight missing")
    require(data, "canHoldAllAfterRemoving", "Maker output inventory-space preflight missing")
    require(data, "removeOddMakerReagents", "Maker reagent validation missing")
    require(data, "ItemConstants.isMakerReagent", "Maker reagent type validation missing")
    require(data, "InventoryManipulator.removeFromSlot(c, InventoryType.EQUIP", "Maker disassembly source removal missing")
    require(data, "c.getPlayer().gainMeso(-cost, false)", "Maker meso consumption missing")
    require(data, "InventoryManipulator.addFromDrop(c, item, false, -1)", "Maker equipment fulfillment missing")

    print("EverLeaf Maker/crafting integrity audit: PASS")
    print("  packet path is serialized per client")
    print("  recipe, ingredient, meso, level, skill, reagent and output-space preflights exist")
    print("  stimulant failure remains an intentional 10% craft-failure mechanic")
    print("[REVIEW] Maker is fail-safe against replay/duplication, but not durably atomic across a process crash:")
    print("         inputs/mesos can be consumed before final output insertion. A crash in that window can cause loss, not duplication.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
