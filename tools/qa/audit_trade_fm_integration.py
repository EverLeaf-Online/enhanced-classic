#!/usr/bin/env python3
"""Static regression checks for EverLeaf's TRADE -> Free Market shortcut."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROCESSOR = ROOT / "src/main/java/net/PacketProcessor.java"
HANDLER = ROOT / "src/main/java/net/server/channel/handlers/EnterMTSHandler.java"
CONFIG = ROOT / "config.yaml"


def require(text: str, needle: str, source: Path, failures: list[str]) -> None:
    if needle not in text:
        failures.append(f"{source.relative_to(ROOT)} missing required invariant: {needle}")


def forbid(text: str, needle: str, source: Path, failures: list[str], detail: str) -> None:
    if needle in text:
        failures.append(f"{source.relative_to(ROOT)} {detail}: {needle}")


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
    require(handler, "if (chr.isChangingMaps())", HANDLER, failures)

    # Real player-commerce state must still block the shortcut.
    require(handler, "chr.getTrade() != null", HANDLER, failures)
    require(handler, "chr.getPlayerShop() != null", HANDLER, failures)
    require(handler, "chr.getHiredMerchant() != null", HANDLER, failures)

    # NPC shop/storage state can remain stale after the UI closes; the handler
    # should close normal interactions before warping instead of false-blocking.
    require(handler, "chr.closePlayerInteractions();", HANDLER, failures)
    forbid(handler, "chr.getStorage() != null", HANDLER, failures,
           "must not reject stale NPC storage state")
    forbid(handler, "chr.getShop() != null", HANDLER, failures,
           "must not reject stale NPC shop state")

    require(handler, "if (chr.getEventInstance() != null)", HANDLER, failures)
    require(handler, "MiniDungeonInfo.isDungeonMap(chr.getMapId())", HANDLER, failures)
    require(handler, "FieldLimit.CANNOTMIGRATE.check(chr.getMap().getFieldLimit())", HANDLER, failures)
    require(handler, 'chr.saveLocation("FREE_MARKET");', HANDLER, failures)
    require(handler, "chr.changeMap(target, targetPortal);", HANDLER, failures)
    require(config, "USE_MTS: false", CONFIG, failures)

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
