# EverLeaf Client

The canonical EverLeaf native client source lives under `client/native/`.

## Canonical native layout

- `client/native/proxy/` — minimal Windows DirectInput proxy/bootstrap that loads `EverLeafMS.dll`.
- `client/native/core/` — main EverLeaf v83 integration module built as `EverLeafMS.dll`.
- `client/native/discord/` — standalone Discord IPC/Rich Presence module built as `Discord.dll`.
- `client/native/EverLeaf Client.sln` — canonical Win32/x86 solution.
- `client/native/THIRD_PARTY_NOTICES.md` — provenance and redistribution notices.
- `client/native/third_party/` — retained upstream license/provenance material only.

The old `client/ezorsia/` product tree has been removed. Historical upstream names may remain only where required for source compatibility or attribution while those internals are progressively replaced; they are not EverLeaf branding or canonical paths.

A MapleStory client release is the entire runtime package: `EverLeaf.exe`, WZ files, DLLs, configuration, assets, and required runtime dependencies. The launcher/patcher may publish smaller overlays, but those overlays must be validated against the complete client baseline.

The managed native overlay now consists of the bootstrap `dinput8.dll`, `EverLeafMS.dll`, `Discord.dll`, `config.ini`, and `EverLeaf_UI.wz`. The launcher baseline still covers the complete client package.

Do not mutate the finished legacy `EverLeaf.exe` with resource editors. Native features belong in EverLeaf-owned DLLs and WZ/config changes belong in their respective managed files.
