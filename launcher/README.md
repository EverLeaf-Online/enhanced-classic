# EverLeaf Portable Launcher

The EverLeaf Launcher is a portable installer and patcher. The folder containing
the launcher becomes the game directory.

## Player flow

1. Create an empty folder you control.
2. Extract the portable launcher into that folder.
3. Open `EverLeafLauncher.exe` and press **Install EverLeaf**.
4. The launcher authenticates EverLeaf's signed HTTPS manifest and checks available disk space.
5. It downloads all 36 required files and verifies each one before replacement.
6. Existing installations automatically check every file by size and streaming SHA-256.
7. After all required files match production, Play starts `EverLeaf.exe`.

The complete managed set is declared in `client/managed-client-baseline.json`.
It includes all WZ files, EverLeaf.exe, required DLL/ACM runtime files, and
EverLeaf's client configuration. The running launcher and its README are excluded
so the game-file patcher never attempts to replace itself.

## Security boundary

- The launcher never connects directly to MySQL or stores game-account passwords.
- Manifest paths are constrained to the folder containing the launcher.
- Absolute paths, traversal, duplicate paths, and external download URLs are rejected.
- Every local and downloaded file is checked with streaming SHA-256.
- The manifest must pass RSA-PSS verification before any file is changed.
- Downloads must use EverLeaf's production HTTPS origin.
- The manifest signing private key stays only on the production server.

## Release model

- `EverLeafLauncher-portable.zip` is the single player-facing bootstrap download.
- `/patches/<file>` holds repair copies of every file in the managed baseline.
- `/v1/launcher/manifest` returns the signed production file identities.

Repository-built client overlays (`dinput8.dll`, `config.ini`, and
`EverLeaf_UI.wz`) update their corresponding files without deleting the static
bootstrap files already present on the production patch server.

Existing legacy folders may contain `MapleStory.exe`. On their first successful
repair, the launcher verifies the production client as `EverLeaf.exe` and removes
only that legacy executable.
