# EverLeaf Client

The canonical EverLeaf native client source now lives under `client/everleaf/`.

## Canonical native layout

- `client/everleaf/bootstrap/dinput8.dll` — minimal Windows DirectInput proxy/bootstrap.
- `client/everleaf/core/EverLeafMS.dll` — main EverLeaf v83 client integration module.
- `client/everleaf/discord/Discord.dll` — optional Discord IPC/Rich Presence module.
- `client/everleaf/EverLeaf Client.sln` — canonical Win32 solution.
- `client/everleaf/THIRD_PARTY_NOTICES.md` — provenance and redistribution notices.

The historical source under `client/ezorsia/` is migration provenance only and is not the target architecture. New native client work must go under `client/everleaf/`.

A MapleStory client release is the entire runtime package: `EverLeaf.exe`, WZ files, DLLs, configuration, assets and required runtime dependencies. The launcher/patcher may publish smaller overlays, but those overlays must be validated against the complete client baseline.

Do not mutate the finished legacy `EverLeaf.exe` with resource editors. Native features belong in EverLeaf-owned DLLs and WZ/config changes belong in their respective managed files.
