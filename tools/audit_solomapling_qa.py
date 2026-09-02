#!/usr/bin/env python3
"""Fail closed when the staged SoloMapling QA integration loses a safety/runtime invariant."""
from pathlib import Path


def require(path: str, needle: str, label: str) -> None:
    text = Path(path).read_text(encoding="utf-8")
    if needle not in text:
        raise SystemExit(f"[FAIL] {label}: missing {needle!r} in {path}")
    print(f"[PASS] {label}")


def main() -> None:
    require("config.yaml", "    SPAWN_BOTS_ON_STARTUP: false", "automatic bot population disabled")
    require("src/main/java/client/BotClient.java", "class BotClient extends Client", "headless client present")
    require("src/main/java/soloMapling/ArtificialPlayer/BotClientHandler.java", "initHeadlessBotClient", "headless bootstrap handler present")
    require("src/main/java/soloMapling/ArtificialPlayer/BareBotFactory.java", "createBareBot", "single-bot factory present")
    require("src/main/java/soloMapling/ArtificialPlayer/BareBotMovement.java", "updatePositionBot", "headless movement executor present")
    require("src/main/java/soloMapling/ArtificialPlayer/BareBotCombat.java", "strikeNearest", "headless combat smoke path present")
    require("src/main/java/client/command/commands/gm4/QaBotCommand.java", "case \"strike\" -> strike(c, params);", "GM-only combat smoke command present")
    require("src/main/java/client/Character.java", "public void setID(int id)", "synthetic bot id hook applied")
    require("src/main/java/server/maps/MapleMap.java", "public void moveBot(Character player, Point newPosition)", "headless map movement hook applied")
    require("src/main/java/server/maps/MapleMap.java", "if (!isBot(chr))", "headless ranged-visibility exclusion applied")
    require("src/main/java/server/life/Monster.java", "!BotHelpers.isBot(chr)", "headless monster-controller exclusion applied")
    require("src/main/java/net/server/Server.java", "BotClientHandler.initHeadlessBotClient();", "server initializes only shared headless client")

    server = Path("src/main/java/net/server/Server.java").read_text(encoding="utf-8")
    if "EnvironmentManager::environmentLoadStartup" in server:
        raise SystemExit("[FAIL] automatic SoloMapling EnvironmentManager startup must stay disabled during smoke integration")
    print("[PASS] EnvironmentManager auto-start absent")
    print("EverLeaf SoloMapling QA integration guardrails: PASS")


if __name__ == "__main__":
    main()
