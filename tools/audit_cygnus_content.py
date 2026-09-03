#!/usr/bin/env python3
"""Hard release gate for EverLeaf's Fallen Cygnus / Empress encounter."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENT = ROOT / "scripts/event/CygnusBattle.js"
NPC = ROOT / "scripts/npc/2143004.js"
PORTALS = [ROOT / "scripts/portal/out_cygnusBackGarden.js", ROOT / "scripts/portal/back_cygnus.js"]
EXPED = ROOT / "src/main/java/server/expeditions/ExpeditionType.java"
POLICY = ROOT / "src/main/java/everleaf/progression/CygnusRewardPolicy.java"
LIFECYCLE = ROOT / "src/main/java/everleaf/progression/CygnusEncounterLifecycleService.java"
RUNTIME = ROOT / "src/main/java/everleaf/progression/EverleafProgressionRuntime.java"
MAP_AUDIT = ROOT / "tools/audit_script_map_references.py"

failures=[]
def need(cond,msg):
    if not cond: failures.append(msg)
def text(p):
    need(p.is_file(), f"missing {p.relative_to(ROOT)}")
    return p.read_text(encoding="utf-8",errors="replace") if p.is_file() else ""

e=text(EVENT); n=text(NPC); ex=text(EXPED); pol=text(POLICY); life=text(LIFECYCLE); rt=text(RUNTIME); ma=text(MAP_AUDIT)
for p in PORTALS: text(p)
need("CYGNUS(3, 12, 180, 255, 5)" in ex, "Cygnus expedition gate is not 3-12 / level 180-255")
need('ENCOUNTER_ID = "fallen_cygnus"' in life, "durable Fallen Cygnus encounter id missing")
need("cygnusEncounterLifecycleService" in rt, "Cygnus lifecycle is not wired into runtime")
need('getEventManager("CygnusBattle")' in n, "Another Informant does not launch CygnusBattle")
need("ExpeditionType.CYGNUS" in n, "Another Informant is not bound to CYGNUS expedition")
need("var eventTime = 60" in e, "Cygnus timer is not 60 minutes")
need("8850010" in e and "8850011" in e, "Shinsoo/final Cygnus phases missing")
# The ten Chief Knight bodies are deliberately spawned/handled as two contiguous five-ID ranges.
need("8850000+i" in e and "i<5" in e, "phase-1 Chief Knight spawn range 8850000-8850004 missing")
need("8850005+i" in e and "i<5" in e, "phase-2 Chief Knight spawn range 8850005-8850009 missing")
need("id >= 8850000 && id <= 8850004" in e, "phase-1 Chief Knight kill coverage 8850000-8850004 missing")
need("id >= 8850005 && id <= 8850009" in e, "phase-2 Chief Knight kill coverage 8850005-8850009 missing")
need("mob.disableDrops()" in e, "encounter mobs are not drop-suppressed")
need("id == 8850011" in e, "final clear is not explicitly tied to 8850011")
need("finishPlayer" in e and "CygnusRewardPolicy" in e, "final-body reward finalization missing")
need("WHITE_SCROLL_CHANCE = 5_000" in pol, "White Scroll policy changed from 0.5%")
need("CHAOS_SCROLL_CHANCE = 50_000" in pol, "Chaos Scroll policy changed from 5%")
need("WHITE_SCROLL = 2_340_000" in pol and "CHAOS_SCROLL = 2_049_100" in pol, "rare reward ids changed")
need("LIVE_IMPORTED_MAPS" in ma and "271040100" in ma, "live Future Henesys map package missing from map audit")
need("out_cygnusBackGarden" in PORTALS[0].name and "back_cygnus" in PORTALS[1].name, "required portal names missing")
# Rare scrolls must not be authored directly in the encounter as loose item grants.
need("2049100" not in e and "2340000" not in e, "event script directly embeds rare scroll IDs; policy boundary bypassed")

if failures:
    for f in failures: print("[FAIL]",f)
    raise SystemExit(1)
print("EverLeaf Fallen Cygnus release audit: PASS")
print("  expedition=3-12 players, level 180-255")
print("  phases=10 Chief Knight bodies -> Shinsoo -> final Cygnus")
print("  donor drops=suppressed; rare roll=final body only")
print("  weekly reward=account durable encounter ledger")
print("  rare policy=Chaos 5.0%, White 0.5% (White 10x rarer)")
