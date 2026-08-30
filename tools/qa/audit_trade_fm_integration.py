#!/usr/bin/env python3
"""Static regression checks for EverLeaf's TRADE -> Free Market shortcut.

The v83 status-bar TRADE button emits ENTER_MTS. EverLeaf intentionally keeps
MTS disabled and repurposes that opcode as a guarded server-authoritative warp
to the Free Market entrance. These checks prevent a future upstream merge from
silently unregistering the handler or restoring legacy MTS behavior.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PROCESSOR = ROOT / "src/main/java/net/PacketProcessor.java"
HANDLER = ROOT / "src/main/java/net/server/channel/handlers/EnterMTSHandler.java"
CONFIG = ROOT / "config.yaml"


def require(text: str, needle: str, source: Path, failures: list[str]) -> None:
    if needle not in text:
        failures.append(f"{source.relative_to(ROOT)} missing required invariant: {needle}")


def main() -> int:
    failures: list[str] = []
    for path in (PROCESSOR, HANDLER, CONFIG):
        if not path.is_file():
            failures.append(f"missing required file: {path.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1

    processor = PROCESSOR.read_text(encoding="utf-8")
    handler = HANDLER.read_text(encoding="utf-8")
    config = CONFIG.read_text(encoding="utf-8-sig")

    require(processor, "registerHandler(RecvOpcode.ENTER_MTS, new EnterMTSHandler());", PROCESSOR, failures)
    require(handler, "private static final int FREE_MARKET_ENTRANCE = 910000000;", HANDLER, failures)
    require(handler, "if (!chr.isAlive())", HANDLER, failures)
    require(handler, "if (chr.getEventInstance() != null)", HANDLER, failures)
    require(handler, "MiniDungeonInfo.isDungeonMap(chr.getMapId())", HANDLER, failures)
    require(handler, "FieldLimit.CANNOTMIGRATE.check(chr.getMap().getFieldLimit())", HANDLER, failures)
    require(handler, 'chr.saveLocation("FREE_MARKET");', HANDLER, failures)
    require(handler, "chr.changeMap(target, targetPortal);", HANDLER, failures)
    require(config, "USE_MTS: false", CONFIG, failures)

    # The handler must not instantiate or delegate to the legacy MTS handler.
    if "new MTSHandler" in handler or "MTSHandler(" in handler:
        failures.append("EnterMTSHandler delegates to legacy MTS behavior")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1

    print("EverLeaf TRADE -> Free Market integration: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
