from pathlib import Path


def read(path: str) -> tuple[Path, str]:
    target = Path(path)
    text = target.read_text(encoding="utf-8").replace("\r\n", "\n")
    return target, text


def write(target: Path, text: str) -> None:
    target.write_text(text, encoding="utf-8", newline="\n")


def replace_once(path: str, old: str, new: str) -> None:
    target, text = read(path)
    # The modernization transform is intentionally safe to run repeatedly in
    # CI and packaging. Most replacements retain the old marker as a prefix,
    # so check the complete replacement before counting the old marker.
    if new in text:
        return
    count = text.count(old)
    if count == 0:
        raise SystemExit(f"{path}: missing expected marker:\n{old}")
    if count != 1:
        raise SystemExit(f"{path}: expected one marker, found {count}:\n{old}")
    write(target, text.replace(old, new, 1))


replace_once(
    "client/ezorsia/ezorsia/Client.h",
    "\tstatic bool RemoveLogos;\n",
    "\tstatic bool RemoveLogos;\n"
    "\tstatic bool ModernLoginUI;\n"
    "\tstatic bool ShowFutureClassCards;\n",
)

replace_once(
    "client/ezorsia/ezorsia/Client.cpp",
    "bool Client::RemoveLogos = true;\n",
    "bool Client::RemoveLogos = true;\n"
    "bool Client::ModernLoginUI = true;\n"
    "bool Client::ShowFutureClassCards = true;\n",
)

replace_once(
    "client/ezorsia/ezorsia/MainMain.cpp",
    '\tClient::RemoveLogos = reader.GetBoolean("general", "RemoveLogos", true);\n',
    '\tClient::RemoveLogos = reader.GetBoolean("general", "RemoveLogos", true);\n'
    '\tClient::ModernLoginUI = reader.GetBoolean("general", "ModernLoginUI", true);\n'
    '\tClient::ShowFutureClassCards = reader.GetBoolean("general", "ShowFutureClassCards", true);\n',
)

replace_once(
    "client/ezorsia/ezorsia/dllmain.cpp",
    "\tClient::UpdateResolution();\n\n\tdinput8::CreateHook();",
    "\tClient::UpdateResolution();\n\n"
    "\tif (Client::ModernLoginUI) {\n"
    '\t\tstd::cout << "Applying EverLeaf modern login UI" << std::endl;\n'
    "\t\tClient::UpdateLogin();\n"
    "\t}\n\n"
    "\tdinput8::CreateHook();",
)

# v83's login state stores the race at CLogin+0x214 and already sends that value
# to the server, but its Update switch exposes only races 0..2. At 0x005F4F3C
# the original `jne 0x005F50E7` rejects every race >=3. Route that branch to the
# existing Explorer-compatible name/appearance arm at 0x005F4FD0 instead. The
# race member itself is not changed, so race 3 still reaches EverLeaf as Evan.
# The server capability allowlist independently rejects values >3.
replace_once(
    "client/ezorsia/ezorsia/Client.cpp",
    "\tMemory::FillBytes(0x00761714, 0x90, 21);\n",
    "\tMemory::FillBytes(0x00761714, 0x90, 21);\n"
    "\t// Expose the v84-compatible Evan race value on v83 without changing the wire format.\n"
    "\t// Original bytes at 0x005F4F3C: 0F 85 A5 01 00 00 (race >=3 -> default).\n"
    "\t// New target 0x005F4FD0 reuses the stable Explorer appearance/name dialog while\n"
    "\t// preserving CLogin+0x214, so SendNewCharPacket still transmits race 3.\n"
    "\tunsigned char EvanRace3CreationRoute[] = { 0x0F, 0x85, 0x8E, 0x00, 0x00, 0x00 };\n"
    "\tMemory::WriteByteArray(0x005F4F3C, EvanRace3CreationRoute, sizeof(EvanRace3CreationRoute));\n",
)

# Replace the old experimental login routine with a bounded, reversible first pass.
target, text = read("client/ezorsia/ezorsia/Client.cpp")
start_marker = "void Client::UpdateLogin() {"
start = text.find(start_marker)
if start < 0:
    raise SystemExit("Client.cpp: UpdateLogin start marker missing")
end = text.find("\n}", start)
if end < 0:
    raise SystemExit("Client.cpp: UpdateLogin end marker missing")
end += 2
modern_login = """void Client::UpdateLogin() {
\t// EverLeaf modern-classic login pass. Keep MapleStory's native controls and
\t// event flow; only reposition the stable login dialog/input controls and
\t// restyle their text fields. This makes the change reversible and keeps
\t// world/character-select protocol behavior untouched while the broader UI
\t// backport is screenshot-tested.
\tMemory::CodeCave(PositionLoginDlg, dwLoginCreateDlg, 14);
\tMemory::CodeCave(PositionLoginUsername, dwLoginUsername, 11);
\tMemory::CodeCave(PositionLoginPassword, dwLoginPassword, 8);
\tMemory::WriteInt(dwLoginInputBackgroundColor + 3, 0xFFF4F8F1);
\tMemory::WriteByte(dwLoginInputFontColor + 3, 1);
}
"""
if "EverLeaf modern-classic login pass" not in text:
    text = text[:start] + modern_login + text[end:]
    write(target, text)

# UI choices are safe client presentation settings, not gameplay/security controls.
target, text = read("client/ezorsia/ezorsia/config.ini")
if "ModernLoginUI=" not in text:
    marker = "RemoveLogos=true\n"
    if marker not in text:
        raise SystemExit("config.ini: RemoveLogos marker missing")
    text = text.replace(
        marker,
        "RemoveLogos=true\n\n"
        ";Use EverLeaf's refreshed classic login/world/character-selection layout.\n"
        "ModernLoginUI=true\n\n"
        ";Show future class-family cards as locked previews. The server independently\n"
        ";rejects unsupported creation types, so this never enables unfinished classes.\n"
        "ShowFutureClassCards=true\n",
        1,
    )
    write(target, text)

Path("docs/CLIENT_UI_MODERNIZATION.md").write_text(
    """# EverLeaf client UI modernization

## Compatibility model

EverLeaf keeps the v83 network/client contract and backports later classic UI behavior where it is safe.

### Character-family selector

| Family | Preview | Creation | Wire identity |
| --- | --- | --- | --- |
| Cygnus Knights | visible | enabled | v83 race 0 |
| Explorer | visible | enabled | v83 race 1 |
| Aran | visible | enabled | v83 race 2 |
| Evan | visible | enabled after client selector backport | v84-style race 3, mapped by EverLeaf server type 3 |
| Dual Blade | visible/locked | disabled | not sent; v95 requires Explorer sub-job 1 |
| Resistance | visible/locked | disabled | not sent; requires later runtime/protocol support |

The server capability gate remains authoritative even if a modified client bypasses a visual lock.

## Evan compatibility

The v83 packet already transports a single race integer. EverLeaf routes race 3 through the stable Explorer appearance/name dialog while preserving the race field, allowing the existing server Evan creator to receive type 3 without changing the v83 wire format. Types above 3 remain server-rejected.

## UI surfaces

1. Login layout and input styling — active on the modernization branch.
2. World selection and channel presentation — preserve 20-channel support, modernize compatible art/layout.
3. Character selection — refresh panels/buttons while preserving PIC/character-handoff behavior.
4. Character-family selector — backport Evan slot; show future families locked.
5. Character creation — reuse native family-specific v83/v84-compatible dialogs where possible.
6. Common gameplay UI — selectively backport compatible Basic/UIWindow/StatusBar/Guild/CashShop assets after visual/runtime validation.

No UI package is published until the exact Windows client candidate boots and the affected login/creation flow passes validation.
""",
    encoding="utf-8",
    newline="\n",
)

print("EverLeaf UI modernization transform applied")
