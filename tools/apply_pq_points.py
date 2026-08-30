#!/usr/bin/env python3
"""Inject EverLeaf PQ Point awarding into the legacy event clear hook.

Kept as a deterministic build transform while large upstream event classes are
still shared with Cosmic. The transform is idempotent and fails loudly if the
upstream method shape changes.
"""

from pathlib import Path

PATH = Path("src/main/java/scripting/event/EventInstanceManager.java")
OLD = """    public final void setEventCleared() {
        eventCleared = true;

        for (Character chr : getPlayers()) {
            chr.awardQuestPoint(YamlConfig.config.server.QUEST_POINT_PER_EVENT_CLEAR);
        }

        scriptLock.lock();
"""
NEW = """    public final void setEventCleared() {
        eventCleared = true;

        for (Character chr : getPlayers()) {
            chr.awardQuestPoint(YamlConfig.config.server.QUEST_POINT_PER_EVENT_CLEAR);
        }

        everleaf.progression.PqPointClearHook.onEventCleared(em.getName(), name, getPlayers());

        scriptLock.lock();
"""

text = PATH.read_text(encoding="utf-8")
if NEW in text:
    print("EverLeaf PQ Point event-clear hook already applied.")
elif OLD in text:
    PATH.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print("EverLeaf PQ Point event-clear hook applied.")
else:
    raise SystemExit("Expected EventInstanceManager.setEventCleared source shape not found")
