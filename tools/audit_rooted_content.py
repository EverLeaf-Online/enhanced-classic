#!/usr/bin/env python3
"""Release guardrails for EverLeaf's non-Empress Rooted endgame content."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

required = [
    "src/main/java/everleaf/progression/RootedForgeService.java",
    "src/main/java/everleaf/progression/RootedForgeFulfillmentService.java",
    "src/main/java/everleaf/progression/RootedForgeStatApplier.java",
    "src/main/java/everleaf/progression/RootedZakumLifecycleService.java",
    "src/main/java/everleaf/progression/RootedZakumMechanicPolicy.java",
    "src/main/java/everleaf/progression/JdbcRootedForgeRepository.java",
    "src/main/java/everleaf/progression/JdbcRootedMaterialRepository.java",
    "scripts/event/RootedZakumBattle.js",
    "scripts/npc/2030008.js",
    "database/sql/migration/everleaf_enhanced_encounters.sql",
    "database/sql/migration/everleaf_rooted_materials.sql",
    "database/sql/migration/everleaf_rooted_forge.sql",
]

missing = [path for path in required if not (ROOT / path).is_file()]
if missing:
    raise SystemExit("Missing Rooted release files:\n- " + "\n- ".join(missing))

runtime = (ROOT / "src/main/java/everleaf/progression/EverleafProgressionRuntime.java").read_text(encoding="utf-8")
for symbol in [
    "rootedZakumLifecycleService()",
    "rootedForgeService()",
    "rootedForgeFulfillmentService()",
    "rootedMaterialRepository()",
]:
    if symbol not in runtime:
        raise SystemExit(f"Rooted runtime service is not wired: {symbol}")

npc = (ROOT / "scripts/npc/2030008.js").read_text(encoding="utf-8")
for marker in ["RootedZakumBattle", "Rooted Forge", "rootedForgeService()"]:
    if marker not in npc:
        raise SystemExit(f"Adobis is missing Rooted integration marker: {marker}")

event = (ROOT / "scripts/event/RootedZakumBattle.js").read_text(encoding="utf-8")
for marker in [
    'everleafEncounterId", "rooted_zakum"',
    "rootedZakumLifecycleService().begin",
    "rootedZakumLifecycleService().complete",
    "mob.getId() == 8800002",
]:
    if marker not in event:
        raise SystemExit(f"Rooted Zakum safety marker missing: {marker}")

# Rooted rewards are fulfilled transactionally through the lifecycle service.
# Do not also populate the legacy event reward arrays or add direct Chaos/White grants here.
for forbidden in ["2049100", "2340000"]:
    if forbidden in event:
        raise SystemExit(f"Rooted Zakum event script must not directly grant rare scroll {forbidden}")

print("Rooted content audit passed: encounter, forge, migrations, runtime wiring, and reward guardrails are present.")
