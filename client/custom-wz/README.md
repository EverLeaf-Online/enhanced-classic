# EverLeaf Custom WZ

`EverLeaf_Custom.wz` is generated from source-controlled EverLeaf-owned content.
It is not a renamed donor WZ and must not be populated by copying wholesale WZ
content from Community, Ezorsia, Kaentake, or another server/client distribution.

## Canonical source

`manifest.tsv` is the canonical source list for the first builder phase. Each
non-comment row has four tab-separated columns:

1. image name (`*.img`)
2. property path within the image
3. type (`string` or `int` in phase 14)
4. value

The phase-14 metadata image is intentionally harmless: it proves that the build
pipeline can create, save, reopen, and verify a real v83 GMS WZ without changing
an existing MapleStory asset path.

## Builder dependency

The build script pins `toyobayashi/libwz` to commit
`98e69cd50504a55feecc4277cc041c52c1cc538d` (MIT). Only libwz's native build
dependencies (`tiny-aes` and `zlib`) are initialized. Its HaRepacker reference/test
submodule is not used or checked out by the EverLeaf build path.

Run from PowerShell:

```powershell
./client/scripts/build-everleaf-custom-wz.ps1
```

Default output is `client/generated/EverLeaf_Custom.wz`. Generated WZ binaries are
build artifacts; source content belongs in this directory/repository instead of
being edited directly in the binary.

## Migration rule

Do not remove the existing `EverLeaf_UI.wz` compatibility path until equivalent
EverLeaf-owned assets have been migrated into this source tree, the generated
`EverLeaf_Custom.wz` has been runtime-tested in the client, and the launcher/patch
manifest has been updated in a separate reviewed phase.
