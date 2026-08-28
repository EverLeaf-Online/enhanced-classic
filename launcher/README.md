# EverLeaf Portable Launcher

The EverLeaf Launcher is a portable patcher. It is not an installer and does not
choose or create a game directory.

## Player flow

1. Download and extract the complete `Everleaf MS.rar` client.
2. Extract the portable launcher into that same folder, beside `MapleStory.exe`.
3. Open `EverLeafLauncher.exe`.
4. Press **Play EverLeaf** or **Check / Repair Files**.
5. The launcher authenticates EverLeaf's signed HTTPS manifest.
6. It checks every required game file by size and streaming SHA-256.
7. It downloads only missing or outdated files and verifies each download before replacement.
8. After all 36 required files match production, Play starts `MapleStory.exe`.

The complete managed set is declared in `client/managed-client-baseline.json`.
It includes all WZ files, MapleStory.exe, required DLL/ACM runtime files, and
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

- `Everleaf MS.rar` is the authorized complete bootstrap client.
- `EverLeafLauncher-portable.zip` is the small portable launcher download.
- `/patches/<file>` holds repair copies of every file in the managed baseline.
- `/v1/launcher/manifest` returns the signed production file identities.

Repository-built client overlays (`dinput8.dll`, `config.ini`, and
`EverLeaf_UI.wz`) update their corresponding files without deleting the static
bootstrap files already present on the production patch server.
