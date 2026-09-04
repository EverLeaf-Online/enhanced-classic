from pathlib import Path

TARGET = Path("client/ezorsia/ezorsia/AutoTypes.h")

old = 'HMODULE mod = LoadLibraryA(lpModule); //ty alias! for sharing their version\t//ps i made some changes'
new = (
    'HMODULE mod = GetModuleHandleA(lpModule); // Client v2: never LoadLibrary during global initialization; '
    'modules required later are resolved explicitly on the bootstrap worker'
)

text = TARGET.read_text(encoding="utf-8")
if new in text and old not in text:
    print("Client v2 loader cleanup already applied")
elif text.count(old) != 1:
    raise SystemExit(f"Expected exactly one legacy GetFuncAddress LoadLibrary marker, found {text.count(old)}")
else:
    TARGET.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
    print("Client v2 loader cleanup applied")
