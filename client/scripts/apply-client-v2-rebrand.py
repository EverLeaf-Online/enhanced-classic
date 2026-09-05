from pathlib import Path

MAIN = Path("client/ezorsia/ezorsia/MainMain.cpp")
REPLACEMENTS = Path("client/ezorsia/ezorsia/ReplacementFuncs.h")
CLIENT = Path("client/ezorsia/ezorsia/Client.cpp")


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

# The inherited Ezorsia source tries to change the EXE's embedded UAC manifest
# and PE LARGE_ADDRESS_AWARE characteristic after Windows has already created
# the process. Those writes cannot change process-creation policy at that point.
# The 2026-09-05 copycat audit independently confirmed its v83 executable is
# already LAA on disk (COFF Characteristics 0x012F), so Client v2 must treat
# these as pre-launch/packaging properties rather than runtime memory patches.
client = CLIENT.read_text(encoding="utf-8")

runtime_uac_block = """\tMemory::FillBytes(0x00C08459, 0x20, 0x00C0846E - 0x00C08459);//remove elevation requests
\tMemory::WriteByte(0x00C08459, 0x22);//remove elevation requests\t//thanks stelmo for showing me how to do this
\tMemory::WriteString(0x00C08459 + 1, \"asInvoker\");//remove elevation requests\t//not working from dll
\tMemory::WriteByte(0x00C08463, 0x22);//remove elevation requests\t//thanks stelmo for showing me how to do this
\tMemory::WriteByte(0x0049C2CD + 1, 0x01);//remove elevation requests\t//still not working unfortunately\t//still keeping this to checks for admin privilege
\tMemory::WriteByte(0x0049CFE8 + 1, 0x01);//likely requires affecting WINAPI CreateProcess, which requires a launcher\t\t//because a packed client cannot be directly edited for these offsets
\tMemory::WriteByte(0x0049D398 + 1, 0x01);//remove elevation requests\t//still not working unfortunately

"""
runtime_laa_write = "\tMemory::WriteByte(0x0040013E, 0x2F);  //4g edit, not sure if it still works after execution\n\n"
startup_marker = "\t// Client v2: PE/UAC process-creation policy is handled before launch; no runtime manifest/LAA writes.\n\n"

if startup_marker not in client:
    if client.count(runtime_uac_block) != 1:
        raise SystemExit("Expected exactly one inherited runtime UAC patch block")
    if client.count(runtime_laa_write) != 1:
        raise SystemExit("Expected exactly one inherited runtime LAA write")
    client = client.replace(runtime_uac_block, startup_marker, 1)
    client = client.replace(runtime_laa_write, "", 1)

for forbidden in (
    'Memory::WriteString(0x00C08459 + 1, "asInvoker")',
    "Memory::WriteByte(0x0040013E, 0x2F)",
):
    if forbidden in client:
        raise SystemExit(f"Dead process-creation runtime patch survived Client v2 transform: {forbidden}")

CLIENT.write_text(client, encoding="utf-8", newline="\n")

print("EverLeaf Client v2 rebrand/startup-policy transform applied")
