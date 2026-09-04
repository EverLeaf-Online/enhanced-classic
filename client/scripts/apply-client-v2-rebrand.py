from pathlib import Path

MAIN = Path("client/ezorsia/ezorsia/MainMain.cpp")
REPLACEMENTS = Path("client/ezorsia/ezorsia/ReplacementFuncs.h")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text and old not in text:
        return text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one {label} marker, found {count}:\n{old}")
    return text.replace(old, new, 1)


def replace_all_required(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        if new in text:
            return text
        raise SystemExit(f"Missing expected {label} marker: {old}")
    return text.replace(old, new)


main = MAIN.read_text(encoding="utf-8")

main = replace_once(
    main,
    "your config.ini file cannot be properly read, go to troubleshooting section of Ezorsia v2 setup guide at https://github.com/444Ro666/MapleEzorsia-v2 for more details, or delete your config.ini to have a new one generated with default settings",
    "EverLeaf could not read config.ini. Repair the client with EverLeafLauncher.exe, or delete config.ini so EverLeaf can recreate the default settings.",
    "config parse error",
)
main = replace_once(
    main,
    "your config.ini file doesn't exist, please re-download config.ini from Ezorsia v2 releases at https://github.com/444Ro666/MapleEzorsia-v2",
    "EverLeaf could not create config.ini. Repair the client with EverLeafLauncher.exe and try again.",
    "config creation error",
)
main = replace_once(
    main,
    "your EverLeaf_UI.wz file doesn't exist, please re-download EverLeaf_UI.wz from Ezorsia v2 releases at https://github.com/444Ro666/MapleEzorsia-v2",
    "EverLeaf could not create EverLeaf_UI.wz. Repair the client with EverLeafLauncher.exe and try again.",
    "UI WZ creation error",
)
main = replace_once(
    main,
    "Ezorsia V2 has detected you are loading from .img, but that your MapleEzorsiaV2wzfiles.img file doesn't exist in your Data folder, please re-download MapleEzorsiaV2wzfiles.img from Ezorsia v2 releases at https://github.com/444Ro666/MapleEzorsia-v2",
    "EverLeaf detected IMG-mode resources but EverLeaf_UI.img is unavailable. Repair the client with EverLeafLauncher.exe and try again.",
    "IMG fallback error",
)
main = replace_all_required(
    main,
    "MapleEzorsiaV2wzfiles.img",
    "EverLeaf_UI.img",
    "IMG runtime filename",
)
MAIN.write_text(main, encoding="utf-8", newline="\n")

replacements = REPLACEMENTS.read_text(encoding="utf-8")
replacements = replace_all_required(
    replacements,
    "MapleEzorsiaV2wzfiles.img/",
    "EverLeaf_UI.img/",
    "IMG namespace path",
)
REPLACEMENTS.write_text(replacements, encoding="utf-8", newline="\n")

print("EverLeaf Client v2 rebrand transform applied")
