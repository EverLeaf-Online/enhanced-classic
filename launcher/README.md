# EverLeaf Launcher

The launcher is the supported player entry point for EverLeaf.

## Player flow

1. Check server status and announcements.
2. Authenticate over HTTPS.
3. Download the signed patch manifest.
4. Verify and atomically repair changed EverLeaf-owned files.
5. Launch the clean v83 `MapleStory.exe`.

Passwords are never stored. Only the username may be remembered. The short-lived
launcher token is kept in memory and inherited by the game process without being
placed on the command line.

## Security boundary

- The launcher never connects directly to MySQL.
- Patch paths are constrained to the game directory.
- Every downloaded file is SHA-256 verified.
- The manifest must pass RSA-PSS verification before any file is changed.
- Nexon-owned client files are not published by this repository.
- Production authentication and manifest endpoints must use valid HTTPS.

The API endpoint and production manifest public key must be provisioned before
shipping the launcher to players.
