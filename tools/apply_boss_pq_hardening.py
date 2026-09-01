#!/usr/bin/env python3
"""Apply EverLeaf boss/PQ lifecycle hardening directly to shared event sources.

This transform is intentionally non-Evan and only touches the shared event,
expedition, and Ariant lobby paths. It is strict and idempotent: every source
replacement must match exactly once on the first pass and zero times on later
passes.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENT_MANAGER = ROOT / "src/main/java/scripting/event/EventManager.java"
EVENT_INSTANCE = ROOT / "src/main/java/scripting/event/EventInstanceManager.java"
EXPEDITION = ROOT / "src/main/java/server/expeditions/Expedition.java"
ARIANT_NPC = ROOT / "scripts/npc/2101014.js"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one source match, found {count}")
    return text.replace(old, new, 1)


def apply_event_manager() -> None:
    text = EVENT_MANAGER.read_text(encoding="utf-8")

    text = replace_once(
        text,
        """    public boolean startInstance(int lobbyId, Expedition exped) {\n        return startInstance(lobbyId, exped, exped.getLeader());\n    }\n""",
        """    public boolean startInstance(int lobbyId, Expedition exped) {\n        if (exped == null || exped.getLeader() == null) {\n            return false;\n        }\n        return startInstance(lobbyId, exped, exped.getLeader());\n    }\n""",
        "expedition wrapper null guard",
    )

    text = replace_once(
        text,
        """    public boolean startInstance(int lobbyId, Expedition exped, Character leader) {\n        if (this.isDisposed()) {\n            return false;\n        }\n""",
        """    public boolean startInstance(int lobbyId, Expedition exped, Character leader) {\n        if (this.isDisposed() || exped == null || leader == null || exped.getLeader() == null\n                || exped.getLeader().getId() != leader.getId() || !exped.contains(leader)\n                || leader.getMap() != exped.getRecruitingMap()\n                || exped.getActiveMembers().size() < exped.getMinSize()) {\n            return false;\n        }\n""",
        "expedition leader/min-size validation",
    )

    text = replace_once(
        text,
        """    public boolean startInstance(int lobbyId, Character leader) {\n        return startInstance(lobbyId, leader, leader, 1);\n    }\n""",
        """    public boolean startInstance(int lobbyId, Character leader) {\n        if (leader == null) {\n            return false;\n        }\n        return startInstance(lobbyId, leader, leader, 1);\n    }\n""",
        "single-player wrapper null guard",
    )

    text = replace_once(
        text,
        """    public boolean startInstance(int lobbyId, Character chr, Character leader, int difficulty) {\n        if (this.isDisposed()) {\n            return false;\n        }\n""",
        """    public boolean startInstance(int lobbyId, Character chr, Character leader, int difficulty) {\n        if (this.isDisposed() || leader == null || !leader.isLoggedinWorld()) {\n            return false;\n        }\n""",
        "single-player leader validation",
    )

    text = replace_once(
        text,
        """    public boolean startInstance(int lobbyId, Party party, MapleMap map) {\n        return startInstance(lobbyId, party, map, party.getLeader().getPlayer());\n    }\n""",
        """    public boolean startInstance(int lobbyId, Party party, MapleMap map) {\n        if (party == null || party.getLeader() == null || party.getLeader().getPlayer() == null) {\n            return false;\n        }\n        return startInstance(lobbyId, party, map, party.getLeader().getPlayer());\n    }\n""",
        "PQ wrapper null guard",
    )

    text = replace_once(
        text,
        """    public boolean startInstance(int lobbyId, Party party, MapleMap map, Character leader) {\n        if (this.isDisposed()) {\n            return false;\n        }\n""",
        """    public boolean startInstance(int lobbyId, Party party, MapleMap map, Character leader) {\n        if (this.isDisposed() || party == null || map == null || leader == null\n                || party.getLeader() == null || party.getLeaderId() != leader.getId()\n                || leader.getParty() != party || party.getEligibleMembers() == null\n                || party.getEligibleMembers().isEmpty() || map.getCharacterById(leader.getId()) == null) {\n            return false;\n        }\n""",
        "PQ leader/eligibility validation",
    )

    text = replace_once(
        text,
        """    public boolean startInstance(int lobbyId, Party party, MapleMap map, int difficulty) {\n        return startInstance(lobbyId, party, map, difficulty, party.getLeader().getPlayer());\n    }\n""",
        """    public boolean startInstance(int lobbyId, Party party, MapleMap map, int difficulty) {\n        if (party == null || party.getLeader() == null || party.getLeader().getPlayer() == null) {\n            return false;\n        }\n        return startInstance(lobbyId, party, map, difficulty, party.getLeader().getPlayer());\n    }\n""",
        "difficulty PQ wrapper null guard",
    )

    text = replace_once(
        text,
        """    public boolean startInstance(int lobbyId, Party party, MapleMap map, int difficulty, Character leader) {\n        if (this.isDisposed()) {\n            return false;\n        }\n""",
        """    public boolean startInstance(int lobbyId, Party party, MapleMap map, int difficulty, Character leader) {\n        if (this.isDisposed() || party == null || map == null || leader == null\n                || party.getLeader() == null || party.getLeaderId() != leader.getId()\n                || leader.getParty() != party || party.getEligibleMembers() == null\n                || party.getEligibleMembers().isEmpty() || map.getCharacterById(leader.getId()) == null) {\n            return false;\n        }\n""",
        "difficulty PQ leader/eligibility validation",
    )

    text = replace_once(
        text,
        """    public boolean startInstance(int lobbyId, EventInstanceManager eim, String ldr) {\n        return startInstance(-1, eim, ldr, eim.getEm().getChannelServer().getPlayerStorage().getCharacterByName(ldr));  // things they make me do...\n    }\n""",
        """    public boolean startInstance(int lobbyId, EventInstanceManager eim, String ldr) {\n        if (eim == null || eim.getEm() == null || ldr == null) {\n            return false;\n        }\n        return startInstance(lobbyId, eim, ldr, eim.getEm().getChannelServer().getPlayerStorage().getCharacterByName(ldr));  // things they make me do...\n    }\n""",
        "existing-instance wrapper null/lobby fix",
    )

    text = replace_once(
        text,
        """    public boolean startInstance(int lobbyId, EventInstanceManager eim, String ldr, Character leader) {\n        if (this.isDisposed()) {\n            return false;\n        }\n""",
        """    public boolean startInstance(int lobbyId, EventInstanceManager eim, String ldr, Character leader) {\n        if (this.isDisposed() || eim == null || leader == null || ldr == null || !leader.isLoggedinWorld()) {\n            return false;\n        }\n""",
        "existing-instance leader validation",
    )

    # The four setup-created start paths shared the same false-success catch.
    old_catch = """                    } catch (ScriptException | NoSuchMethodException ex) {\n                        log.error(\"Event script startInstance\", ex);\n                    }\n\n                    return true;\n"""
    new_catch = """                    } catch (ScriptException | NoSuchMethodException ex) {\n                        log.error(\"Event script startInstance\", ex);\n                        if (lobbyId > -1) {\n                            setLockLobby(lobbyId, false);\n                        }\n                        return false;\n                    }\n\n                    return true;\n"""
    if new_catch not in text:
        count = text.count(old_catch)
        if count != 4:
            raise SystemExit(f"shared start failure handling: expected 4 source matches, found {count}")
        text = text.replace(old_catch, new_catch, 4)

    # Existing-EIM setup can fail after the instance was registered, so dispose it too.
    old_existing = """                        iv.invokeFunction(\"setup\", eim);\n                        eim.setProperty(\"leader\", ldr);\n\n                        eim.startEvent();\n                    } catch (ScriptException | NoSuchMethodException ex) {\n                        log.error(\"Event script startInstance\", ex);\n                    }\n\n                    return true;\n"""
    new_existing = """                        iv.invokeFunction(\"setup\", eim);\n                        eim.setProperty(\"leader\", ldr);\n\n                        eim.startEvent();\n                    } catch (ScriptException | NoSuchMethodException ex) {\n                        log.error(\"Event script startInstance\", ex);\n                        freeLobbyInstance(eim.getName());\n                        eim.dispose(true);\n                        return false;\n                    }\n\n                    return true;\n"""
    text = replace_once(text, old_existing, new_existing, "existing-EIM rollback")

    # Do not leave a previous eligibility snapshot available after a failed eligibility script.
    old_eligible = """    public List<PartyCharacter> getEligibleParty(Party party) {\n        if (party == null) {\n            return new ArrayList<>();\n        }\n        try {\n"""
    new_eligible = """    public List<PartyCharacter> getEligibleParty(Party party) {\n        if (party == null) {\n            return new ArrayList<>();\n        }\n        party.setEligibleMembers(null);\n        try {\n"""
    text = replace_once(text, old_eligible, new_eligible, "clear stale eligibility")

    old_interrupt = """        } catch (InterruptedException ie) {\n            playerPermit.remove(leader.getId());\n        }\n"""
    new_interrupt = """        } catch (InterruptedException ie) {\n            Thread.currentThread().interrupt();\n            playerPermit.remove(leader.getId());\n        }\n"""
    if new_interrupt not in text:
        count = text.count(old_interrupt)
        if count != 5:
            raise SystemExit(f"interrupt handling: expected 5 source matches, found {count}")
        text = text.replace(old_interrupt, new_interrupt, 5)

    EVENT_MANAGER.write_text(text, encoding="utf-8")


def apply_event_instance() -> None:
    text = EVENT_INSTANCE.read_text(encoding="utf-8")

    text = replace_once(
        text,
        """    public void startEventTimer(long time) {\n        timeStarted = System.currentTimeMillis();\n        eventTime = time;\n""",
        """    public void startEventTimer(long time) {\n        if (event_schedule != null) {\n            event_schedule.cancel(false);\n            event_schedule = null;\n        }\n        time = Math.max(1L, time);\n        timeStarted = System.currentTimeMillis();\n        eventTime = time;\n""",
        "cancel stale event timer before restart",
    )

    text = replace_once(
        text,
        """                long nextTime = getTimeLeft() + time;\n                eventTime += time;\n\n                event_schedule = TimerManager.getInstance().schedule(() -> {\n""",
        """                long nextTime = Math.max(1L, getTimeLeft() + time);\n                eventTime = nextTime;\n                timeStarted = System.currentTimeMillis();\n\n                event_schedule = TimerManager.getInstance().schedule(() -> {\n""",
        "safe addEventTimer scheduling",
    )

    text = replace_once(
        text,
        """    public long getTimeLeft() {\n        return eventTime - (System.currentTimeMillis() - timeStarted);\n    }\n""",
        """    public long getTimeLeft() {\n        if (!isTimerStarted()) {\n            return 0L;\n        }\n        return Math.max(0L, eventTime - (System.currentTimeMillis() - timeStarted));\n    }\n""",
        "clamp event timer time-left",
    )

    EVENT_INSTANCE.write_text(text, encoding="utf-8")


def apply_expedition() -> None:
    text = EXPEDITION.read_text(encoding="utf-8")

    text = replace_once(
        text,
        """    public void finishRegistration() {\n        registering = false;\n    }\n""",
        """    public void finishRegistration() {\n        registering = false;\n        if (schedule != null) {\n            schedule.cancel(false);\n            schedule = null;\n        }\n    }\n""",
        "cancel expedition registration timer",
    )

    old_add_int = """        if (members.size() >= this.getMaxSize()) { //Would be a miracle if anybody ever saw this\n            return 3; //\"Sorry, this expedition is full!\";\n        }\n\n        members.put(player.getId(), player.getName());\n"""
    new_add_int = """        if (members.size() >= this.getMaxSize()) { //Would be a miracle if anybody ever saw this\n            return 3; //\"Sorry, this expedition is full!\";\n        }\n\n        int channel = this.getRecruitingMap().getChannelServer().getId();\n        if (!ExpeditionBossLog.attemptBoss(player.getId(), channel, this, false)) {\n            return 4; // Entry-attempt quota reached.\n        }\n\n        members.put(player.getId(), player.getName());\n"""
    text = replace_once(text, old_add_int, new_add_int, "addMemberInt attempt quota")

    EXPEDITION.write_text(text, encoding="utf-8")


def apply_ariant_npc() -> None:
    text = ARIANT_NPC.read_text(encoding="utf-8")
    text = replace_once(
        text,
        """    } else if (playerAdd == 2) {\n        cm.sendOk(\"The arena leader is not accepting your entry.\");\n    } else {\n""",
        """    } else if (playerAdd == 2) {\n        cm.sendOk(\"The arena leader is not accepting your entry.\");\n    } else if (playerAdd == 4) {\n        cm.sendOk(\"You have reached the entry-attempt limit for Ariant Coliseum. Try again after the limit resets.\");\n    } else {\n""",
        "Ariant quota response",
    )
    ARIANT_NPC.write_text(text, encoding="utf-8")


def main() -> int:
    apply_event_manager()
    apply_event_instance()
    apply_expedition()
    apply_ariant_npc()
    print("Applied EverLeaf boss/PQ hardening.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
