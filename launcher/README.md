# EverLeaf Launcher

The EverLeaf Launcher is the supported player entry point for EverLeaf.

## Player flow

1. Install the launcher into the supported MapleStory v83 / EverLeaf game folder.
2. Open `EverLeafLauncher.exe`.
3. The launcher checks EverLeaf server status and announcements.
4. Press **Play EverLeaf**.
5. The launcher downloads the RSA-signed patch manifest over HTTPS.
6. Local files are checked by size and SHA-256.
7. Only missing or outdated files are downloaded.
8. Every downloaded file is verified before it replaces the local copy.
9. `MapleStory.exe` launches from the synchronized game folder.
10. Account login happens normally inside MapleStory.

**Check / Repair Files** performs the same verification without launching the game.

## Why this matters

EverLeaf server maps and client maps must stay synchronized. A mismatched `Map.wz`
can show old objects, incorrect terrain, or NPCs in apparently missing/wrong
locations even when the server spawn records are correct. The launcher manifest is
the client source of truth and is how EverLeaf distributes approved client updates.

## Security boundary

- The launcher never connects directly to MySQL.
- The launcher does not store MapleStory account passwords.
- Patch paths are constrained to the selected game directory.
- Absolute paths and path traversal are rejected.
- Every downloaded file is SHA-256 verified.
- The manifest must pass RSA-PSS verification before any file is changed.
- The running launcher executable cannot be replaced through the game-file manifest.
- Patch downloads must use HTTPS.
- The manifest signing **private key is server-only** and must never be committed or distributed.
- The repository and launcher installer do not contain the base MapleStory client.

## Patch server layout

Production expects the website/patch service to expose:

- `GET /v1/launcher/status`
- `GET /v1/launcher/manifest`
- `GET /patches/<file>`

The server signs the exact UTF-8 bytes of `manifest.json` with RSA-PSS/SHA-256.
The launcher embeds only the corresponding public key.

A manifest looks like:

```json
{
  "version": "2026.08.27.1",
  "files": [
    {
      "path": "dinput8.dll",
      "url": "/patches/dinput8.dll",
      "sha256": "...64 hex characters...",
      "size": 123456
    }
  ]
}
```

Only files deliberately placed into the production patch directory are included.
This lets EverLeaf ship its own DLL/config/UI updates and any other client updates
that the project is authorized to distribute without bundling a base game client.
