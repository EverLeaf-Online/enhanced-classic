# Everleaf v83 client

Everleaf uses a source-built, pinned fork of MapleEzorsia v2 rather than an
unexplained pre-patched executable.

## Closed-alpha package

The CI artifact contains:

- `dinput8.dll` — Everleaf's source-built v83 client compatibility layer
- `config.ini` — defaults to the Everleaf staging server
- `EverLeaf_UI.wz` — HD UI support for standard WZ installations
- licenses, source provenance, checksums, and setup instructions

It does not contain Nexon's MapleStory executable or game assets. Testers must
supply a clean, compatible Global MapleStory v83 installation.

## Installation

1. Make a backup copy of the clean v83 game directory.
2. Extract the Everleaf artifact into that directory.
3. Confirm `config.ini` contains `ServerIP_Address=132.145.141.79`.
4. Scan the directory with Windows Security.
5. Launch the clean v83 MapleStory executable normally.

Do not add unrelated DLL files to the game directory. Everleaf's fork disables
MapleEzorsia's configurable third-party DLL loader.

## Development

- Upstream snapshot and license: `client/ezorsia`
- Upstream provenance: `client/UPSTREAM.md`
- Everleaf integration branch: `client-dev`
- Build: Release / Win32 using Visual Studio 2022 (`v143`)
- Output: `client/ezorsia/out/Release/dinput8.dll`

The GitHub Actions build is the canonical reproducible build.
