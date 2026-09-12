from pathlib import Path

MAIN = Path("client/native/core/MainMain.cpp")
REPLACEMENTS = Path("client/native/core/ReplacementFuncs.h")
CLIENT = Path("client/native/core/Client.cpp")


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
main = replace_all_required(main, '"132.145.141.79"', '"129.159.114.146"', "relay bootstrap address")
MAIN.write_text(main, encoding="utf-8", newline="\n")

replacements = REPLACEMENTS.read_text(encoding="utf-8")
REPLACEMENTS.write_text(replacements, encoding="utf-8", newline="\n")

# Historical upstream code tried to change the EXE's embedded UAC manifest and
# PE LARGE_ADDRESS_AWARE characteristic after process creation. EverLeaf treats
# both as pre-launch packaging properties instead of runtime memory patches.
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
startup_marker = "\t// EverLeaf: PE/UAC process-creation policy is handled before launch; no runtime manifest/LAA writes.\n\n"

if startup_marker not in client:
    if client.count(runtime_uac_block) != 1:
        raise SystemExit("Expected exactly one inherited runtime UAC patch block")
    if client.count(runtime_laa_write) != 1:
        raise SystemExit("Expected exactly one inherited runtime LAA write")
    client = client.replace(runtime_uac_block, startup_marker, 1)
    client = client.replace(runtime_laa_write, "", 1)

for forbidden in ('Memory::WriteString(0x00C08459 + 1, "asInvoker")', "Memory::WriteByte(0x0040013E, 0x2F)"):
    if forbidden in client:
        raise SystemExit(f"Dead process-creation runtime patch survived EverLeaf transform: {forbidden}")

client = replace_all_required(client, '"132.145.141.79"', '"129.159.114.146"', "relay login address")
CLIENT.write_text(client, encoding="utf-8", newline="\n")

print("EverLeaf native rebrand/startup-policy/relay transform applied")
