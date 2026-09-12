#!/usr/bin/env python3
"""Static audit for quest completion replay/disconnect safety.

Normal quest completion is serialized by the client lock, requires STARTED
state, checks every completion action first, and records COMPLETED before reward
actions run. That ordering prevents reconnect/packet replay from minting the
same normal quest reward twice. It does leave a crash-consistency window where
a process failure after completion is persisted but before all actions finish
can cause a partial/lost reward; that is a reliability issue, not a dupe path.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDLER = ROOT / "src/main/java/net/server/channel/handlers/QuestActionHandler.java"
QUEST = ROOT / "src/main/java/server/quest/Quest.java"
ITEM_ACTION = ROOT / "src/main/java/server/quest/actions/ItemAction.java"


def require(data: str, fragment: str, label: str) -> None:
    if fragment not in data:
        raise SystemExit(f"FAIL: {label}")


def main() -> int:
    handler = HANDLER.read_text(encoding="utf-8")
    quest = QUEST.read_text(encoding="utf-8")
    item_action = ITEM_ACTION.read_text(encoding="utf-8")

    require(handler, "if (!c.tryacquireClient())", "quest packet path is not serialized")
    require(handler, "if (quest.canComplete(player, npc))", "quest completion gate missing")
    require(quest, "if (!mqs.getStatus().equals(Status.STARTED))", "quest completion does not require STARTED state")
    require(quest, "for (AbstractQuestAction a : acts)", "quest action preflight/run loop missing")
    require(quest, "if (!a.check(chr, selection))", "quest action preflight missing")
    require(quest, "forceComplete(chr, npc);", "quest completion persistence marker missing")
    require(item_action, "announceInventoryLimit", "quest item reward inventory preflight missing")
    require(item_action, "InventoryManipulator.removeById", "quest item requirement consumption missing")
    require(item_action, "InventoryManipulator.addById", "quest item reward delivery missing")

    force_index = quest.find("forceComplete(chr, npc);")
    run_index = quest.find("a.run(chr, selection);", force_index)
    if force_index < 0 or run_index < 0 or force_index > run_index:
        raise SystemExit("FAIL: normal quest completion must be recorded before reward actions run")

    print("EverLeaf quest reward replay/disconnect audit: PASS")
    print("  completion packets are serialized and require a STARTED quest")
    print("  all reward/action checks run before settlement")
    print("  COMPLETED state is recorded before reward actions, preventing reconnect/packet replay duplication")
    print("  item rewards preflight inventory capacity")
    print("[REVIEW] A server/process failure after forceComplete but before every reward action finishes can cause")
    print("         a partial/lost reward. Retrying the packet will not duplicate it because the quest is no longer STARTED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
