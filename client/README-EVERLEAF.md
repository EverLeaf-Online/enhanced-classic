# Everleaf v83 client

Everleaf uses a source-built, pinned fork of MapleEzorsia v2 rather than an
unexplained pre-patched executable.

## Closed-alpha package

The CI artifact contains:

- `dinput8.dll` — Everleaf's source-built v83 client compatibility layer
- `config.ini` — defaults to the Everleaf staging server
- `EverLeaf_UI.wz` — HD UI support for standard WZ installations
- licenses, source provenance, checksums, and setup instructions

The source-built CI artifact does not contain the MapleStory executable or base
game assets. The separately published production baseline combines the
owner-authorized Global MapleStory v83 files with the official Cosmic WZ v0.14.0
data set pinned in `client/cosmic-wz-baseline.json`. A generic clean-v83
`Map.wz` or `Npc.wz` is not sufficient because EverLeaf's server-side map XML is
pinned to the matching Cosmic map/NPC data. Mixing these data sets makes NPCs
appear missing, floating, buried, or otherwise misplaced.

## Installation

1. Make a backup copy of the v83 game directory.
2. Install the EverLeaf-supported Cosmic WZ data into that directory.
3. Extract the EverLeaf artifact into the same directory.
4. Keep `config.ini` beside `dinput8.dll`; it only contains player-facing display and compatibility settings.
5. Use the EverLeaf launcher. Its Repair/Play flow verifies every file against the signed managed baseline before launching; the production build independently pins the official Cosmic `Map.wz` and `Npc.wz` identities.
6. Scan the directory with Windows Security.

The launcher validates the supported WZ files by SHA-256 and repairs mismatches
from EverLeaf's authorized production payload. It refuses to launch until the
client's map/NPC data agrees with the signed release baseline.

The EverLeaf server endpoint is compiled into the official DLL and is intentionally not treated as a secret. Do not add unrelated DLL files to the game directory. Everleaf's fork disables
MapleEzorsia's configurable third-party DLL loader.

## Development

- Upstream snapshot and license: `client/ezorsia`
- Upstream provenance: `client/UPSTREAM.md`
- Everleaf integration branch: `client-dev`
- Build: Release / Win32 using Visual Studio 2022 (`v143`)
- Output: `client/ezorsia/out/Release/dinput8.dll`

The GitHub Actions build is the canonical reproducible build.
