#!/usr/bin/env python3
"""Apply Enhanced Classic / Everleaf source changes deterministically.

This is an interim build transform while the fork is being separated from
upstream Cosmic. It is intentionally idempotent and fails loudly when the
expected upstream source shape changes.
"""
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"Expected source pattern not found in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


character = Path("src/main/java/client/Character.java")
replace_once(
    character,
    "return isCygnus() ? 120 : 200;",
    "return service.enhanced.LevelCapPolicy.maxLevel(job);",
)

# Add a Character-owned permanent MaxHP floor mutation. Keeping the raw
# protected setMaxHp call inside Character avoids touching hpMpApUsed and also
# makes login migration safe before the normal stat listener/update flow exists.
replace_once(
    character,
    "    public int getMaxClassLevel() {",
    """    public int applyEnhancedPermanentMaxHpFloor(int targetMaxHp) {\n        int clampedTarget = Math.min(30000, Math.max(getMaxHp(), targetMaxHp));\n        int increase = clampedTarget - getMaxHp();\n        if (increase > 0) {\n            setMaxHp(clampedTarget);\n        }\n        return increase;\n    }\n\n    public int getMaxClassLevel() {""",
)

replace_once(
    character,
    "        levelUpGainSp();",
    """        new service.enhanced.SurvivabilityService().applyCurrentFloor(this);\n\n        levelUpGainSp();""",
)

replace_once(
    character,
    "            ret.autoban = new AutobanManager(ret);",
    """            ret.autoban = new AutobanManager(ret);\n            new service.enhanced.SurvivabilityService().applyCurrentFloor(ret);""",
)

exp_table = Path("src/main/java/constants/game/ExpTable.java")
replace_once(
    exp_table,
    "return level > 200 ? 2000000000 : exp[level];",
    """if (level <= 200) {\n            return exp[level];\n        }\n        if (level < 250) {\n            // Smooth post-200 curve: 1.70b at 201, approaching 2.0b at 249.\n            return Math.min(2_000_000_000, 1_700_000_000 + ((level - 201) * 6_250_000));\n        }\n        return Integer.MAX_VALUE;""",
)

server = Path("src/main/java/net/server/Server.java")
replace_once(
    server,
    'log.info("Cosmic v{} starting up.", ServerConstants.VERSION);',
    'log.info("{} starting up (protocol v{}).", service.enhanced.EverleafIdentity.displayName(), ServerConstants.VERSION);\n        service.enhanced.DeploymentSafetyPolicy.warnings(YamlConfig.config.server)\n                .forEach(warning -> log.warn("Everleaf deployment warning: {}", warning));',
)
replace_once(
    server,
    'log.info("Cosmic is now online after {} ms.", initDuration.toMillis());',
    'log.info("{} is now online after {} ms.", service.enhanced.EverleafIdentity.NAME, initDuration.toMillis());',
)

# EverLeaf QoL: storage is account utility and should be available from level 1.
# Keep all existing GM restrictions, item checks, fees, and concurrency guards;
# remove only Cosmic's legacy level-15 gate.
storage_processor = Path("src/main/java/client/processor/npc/StorageProcessor.java")
replace_once(
    storage_processor,
    """        if (chr.getLevel() < 15) {\n            chr.dropMessage(1, \"You may only use the storage once you have reached level 15.\");\n            c.sendPacket(PacketCreator.enableActions());\n            return;\n        }\n\n""",
    """        // EverLeaf: storage is available at every character level.\n""",
)

# Register player-facing Everleaf progression/economy commands without
# permanently rewriting the large upstream command registry yet. Some branches
# use explicit gm0 imports while the current EverLeaf registry uses a wildcard;
# support both source shapes so CI remains deterministic as the registry evolves.
commands = Path("src/main/java/client/command/CommandsExecutor.java")
commands_text = commands.read_text(encoding="utf-8")
everleaf_imports = (
    "import client.command.commands.gm0.LeafShopCommand;\n"
    "import client.command.commands.gm0.MarksCommand;\n"
    "import client.command.commands.gm0.ProgressCommand;\n"
    "import client.command.commands.gm0.WeekliesCommand;"
)

if "import client.command.commands.gm0.*;" not in commands_text and everleaf_imports not in commands_text:
    import_anchor = "import client.command.commands.gm0.OnlineCommand;"
    if import_anchor not in commands_text:
        raise SystemExit(
            "Expected either gm0 wildcard import or OnlineCommand import in CommandsExecutor.java"
        )
    commands_text = commands_text.replace(
        import_anchor,
        import_anchor + "\n" + everleaf_imports,
        1,
    )

progression_registration = (
    '        addCommand(new String[]{"marks", "verdant"}, MarksCommand.class);\n'
    '        addCommand("progress", ProgressCommand.class);\n'
    '        addCommand(new String[]{"weeklies", "weekly"}, WeekliesCommand.class);'
)
if progression_registration not in commands_text:
    online_anchor = '        addCommand("online", OnlineCommand.class);'
    if online_anchor not in commands_text:
        raise SystemExit("Could not find 'online' player command registration.")
    commands_text = commands_text.replace(
        online_anchor,
        online_anchor + "\n" + progression_registration,
        1,
    )

leafshop_registration = '        addCommand(new String[]{"leafshop", "leaves"}, LeafShopCommand.class);'
if leafshop_registration not in commands_text:
    progression_anchor = '        addCommand(new String[]{"weeklies", "weekly"}, WeekliesCommand.class);'
    if progression_anchor not in commands_text:
        raise SystemExit("Could not find EverLeaf weekly command registration anchor.")
    commands_text = commands_text.replace(
        progression_anchor,
        progression_anchor + "\n" + leafshop_registration,
        1,
    )

commands.write_text(commands_text, encoding="utf-8")

print("Everleaf Enhanced Classic source transform applied (level cap 250 + survivability + identity + safety diagnostics + level-1 storage + progression/marks/leafshop commands).")
