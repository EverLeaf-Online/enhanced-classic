from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: verify-client-v2-branding.py <dinput8.dll>")

path = Path(sys.argv[1])
if not path.is_file():
    raise SystemExit(f"missing client DLL: {path}")

data = path.read_bytes()
forbidden = [
    "Yuna",
    "YunaMS",
    "yuna.ms",
    "MapleEzorsia",
    "Ezorsia v2",
    "Ezorsia V2",
    "444Ro666",
]

hits = []
for token in forbidden:
    if token.encode("ascii") in data or token.encode("utf-16le") in data:
        hits.append(token)

if hits:
    raise SystemExit("donor branding leaked into compiled Client v2 DLL: " + ", ".join(hits))

required = [
    "EverLeaf Client v2",
    "EverLeafLauncher.exe",
    "EverLeaf_UI.img",
]
for token in required:
    if token.encode("ascii") not in data and token.encode("utf-16le") not in data:
        raise SystemExit(f"missing expected EverLeaf branding marker: {token}")

print("Client v2 compiled branding guard passed")
