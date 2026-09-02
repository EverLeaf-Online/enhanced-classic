#!/usr/bin/env python3
"""Fail closed when the staged SoloMapling QA integration loses a safety/runtime invariant."""
from pathlib import Path


def require(path: str, needle: str, label: str) -> None:
    text = Path(path).read_text(encoding="utf-8")
    if needle not in text:
        raise SystemExit(f"[FAIL] {label}: missing {needle!r} in {path}")
    print(f"[PASS] {label}")


def require_count(path: str, needle: str, count: int, label: str) -> None:
    text = Path(path).read_text(encoding="utf-8")
    actual = text.count(needle)
    if actual < count:
        raise SystemExit(f"[FAIL] {label}: expected >= {count}, found {actual} in {path}")
    print(f"[PASS] {label} ({actual})")


def main() -> None:
    require("config.yaml", "    SPAWN_BOTS_ON_STARTUP: false", "automatic bot population disabled")
    require("src/main/java/client/BotClient.java", "class BotClient extends Client", "headless client present")
    require("src/main/java/soloMapling/ArtificialPlayer/BotClientHandler.java", "initHeadlessBotClient", "headless bootstrap handler present")
    require("src/main/java/soloMapling/ArtificialPlayer/BareBotFactory.java", "createBareBot", "single-bot factory present")
    require("src/main/java/soloMapling/ArtificialPlayer/BareBotFactory.java", "bot.setGMLevel(0);", "template clone loses GM privileges")
    require("src/main/java/soloMapling/ArtificialPlayer/BareBotFactory.java", "bot.setWorldRates();", "bot uses EverLeaf world rates")
    require("src/main/java/soloMapling/ArtificialPlayer/BareBotMovement.java", "updatePositionBot", "headless movement executor present")
    require("src/main/java/soloMapling/ArtificialPlayer/BareBotAutopilot.java", "startPatrol", "bounded autonomous movement smoke present")
    require("src/main/java/soloMapling/ArtificialPlayer/BareBotAutopilot.java", "BareBotMovement.moveTo", "autopilot uses validated packet movement path")
    require("src/main/java/soloMapling/ArtificialPlayer/BareBotCombat.java", "strikeNearest", "headless combat smoke path present")
    require("src/main/java/soloMapling/ArtificialPlayer/BareBotPortal.java", "bot.changeMap(to, targetPortal);", "client-free portal traversal present")
    require("src/main/java/soloMapling/ArtificialPlayer/GCMoveSystem/GCMovement.java", "public final class GCMovement", "full GCMove runtime vendored")
    require("src/main/java/soloMapling/ArtificialPlayer/GCMoveSystem/GCPortals.java", "static boolean enter", "SoloMapling GCMove portal core vendored")
    require("src/main/java/soloMapling/ArtificialPlayer/GCMoveSystem/BotMovementProfile.java", "record BotMovementProfile", "GCMove movement profile model present")
    require("src/main/java/soloMapling/ArtificialPlayer/GCMoveSystem/BotNavigationGraph.java", "final class BotNavigationGraph", "GCMove navigation graph model present")
    require("src/main/java/soloMapling/ArtificialPlayer/GCMoveSystem/BotNavigationGraph.java", "map.getFootholds().findBelow", "staged graph uses EverLeaf foothold lookup")
    require("src/main/java/soloMapling/ArtificialPlayer/GCMoveSystem/BotNavigationMapLoader.java", "loadMapGeometry", "GCMove WZ geometry loader present")
    require("src/main/java/soloMapling/ArtificialPlayer/GCMoveSystem/BotNavigationMapLoader.java", "map.addRope(new Rope", "GCMove loader imports rope geometry")
    require("src/main/java/soloMapling/ArtificialPlayer/GCMoveSystem/MovementPlan.java", "final class MovementPlan", "GCMove analytic movement plan present")
    require("src/main/java/soloMapling/ArtificialPlayer/GCMoveSystem/MovementPlan.java", "Point positionAt", "GCMove coarse-plan interpolation present")
    require("src/main/java/soloMapling/ArtificialPlayer/GCMoveSystem/BotMovementState.java", "class BotMovementState", "GCMove per-bot state contract present")
    require("src/main/java/soloMapling/ArtificialPlayer/GCMoveSystem/BotMovementState.java", "BotNavigationGraph.Edge navEdge", "GCMove navigation state wired to graph model")
    require("src/main/java/soloMapling/DebugUtilities.java", "public static void debugprint", "GCMove debug compatibility helper present")
    require("src/main/java/soloMapling/ArtificialPlayer/BotMovementSystem/MovementCommands.java", "tryAcquireMovementLock", "GCMove movement lock compatibility present")
    require("src/main/java/soloMapling/server/MapleVersionManager.java", "return true;", "EverLeaf-safe version policy present")
    require("src/main/java/soloMapling/BotLogger.java", "LoggerFactory.getLogger", "SoloMapling logging routed through EverLeaf")
    require("src/main/java/soloMapling/ArtificialPlayer/BotTravelSystem/BotScriptedWarp.java", "record WarpEdge", "GCMove scripted-warp helper present")
    require("src/main/java/soloMapling/ArtificialPlayer/GCMoveSystem/BotPlayerReaction.java", "Deliberately disabled for deterministic QA bots", "ambient GCMove social reactions disabled")
    require("src/main/java/soloMapling/server/BotPerfStats.java", "MOVEMENT_TICKS", "GCMove movement performance counter present")
    require("src/main/java/soloMapling/ArtificialPlayer/BotMapEntryResponder.java", "onBotArrivedObserved", "GCMove map-entry compatibility responder present")
    require("tools/apply_solomapling_nav_hooks.py", "public Collection<Portal> getPortals()", "GCMove portal enumeration hook present")
    require(".github/workflows/solomapling-compatibility.yml", "permissions:\n  contents: read", "GCMove compatibility workflow remains read-only")
    require(".github/workflows/solomapling-compatibility.yml", "Overlay pinned GCMove sources with EverLeaf QA policy", "full GCMove compatibility compile enabled")
    require(".github/workflows/solomapling-compatibility.yml", "git checkout HEAD -- \"$target/BotPlayerReaction.java\"", "deterministic reaction policy restored after upstream overlay")
    require(".github/workflows/solomapling-compatibility.yml", "Compile full GCMove system against EverLeaf", "full GCMove compatibility checkpoint named")
    require("src/main/java/client/command/commands/gm4/QaBotCommand.java", "case \"gcmove\" -> gcMove(c, params);", "GM-only GCMove smoke command present")
    require("src/main/java/client/command/commands/gm4/QaBotCommand.java", "case \"gcstop\" -> gcStop(c, params);", "GM-only GCMove stop command present")
    require("src/main/java/client/command/commands/gm4/QaBotCommand.java", "GCMovement.disable(bot);", "QA command explicitly tears down GCMove sessions")
    require("src/main/java/client/command/commands/gm4/QaBotCommand.java", "case \"strike\" -> strike(c, params);", "GM-only combat smoke command present")
    require("src/main/java/client/command/commands/gm4/QaBotCommand.java", "case \"patrol\" -> patrol(c, params);", "GM-only autonomous patrol control present")
    require("src/main/java/client/command/commands/gm4/QaBotCommand.java", "case \"portal\" -> portal(c, params);", "GM-only portal smoke control present")
    require("src/main/java/client/command/commands/gm4/QaBotCommand.java", "QA_CHANNEL = 1", "smoke bot constrained to headless client channel")
    require("src/main/java/client/Character.java", "public void setID(int id)", "synthetic bot id hook applied")
    require("src/main/java/server/maps/MapleMap.java", "public void moveBot(Character player, Point newPosition)", "headless map movement hook applied")
    require_count("src/main/java/server/maps/MapleMap.java", "// Headless bots do not maintain client-side ranged visibility state.", 2, "both ranged visibility paths exclude headless bots")
    require("src/main/java/server/life/Monster.java", "!BotHelpers.isBot(chr)", "headless monster-controller exclusion applied")
    require("src/main/java/net/server/Server.java", "BotClientHandler.initHeadlessBotClient();", "server initializes only shared headless client")

    server = Path("src/main/java/net/server/Server.java").read_text(encoding="utf-8")
    if "EnvironmentManager::environmentLoadStartup" in server:
        raise SystemExit("[FAIL] automatic SoloMapling EnvironmentManager startup must stay disabled during smoke integration")
    print("[PASS] EnvironmentManager auto-start absent")
    print("EverLeaf SoloMapling QA integration guardrails: PASS")


if __name__ == "__main__":
    main()
