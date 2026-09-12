# EverLeaf Custom WZ

`EverLeaf_Custom.wz` is generated from source-controlled EverLeaf-owned content.
It is not a renamed donor WZ and must not be populated by copying wholesale WZ
content from Community, Ezorsia, Kaentake, or another server/client distribution.

## Canonical source

`manifest.tsv` is the canonical source list. Each non-comment row has four
tab-separated columns:

1. WZ image path (`EverLeafMeta.img`, `UI/Login.img`, `Map/Obj/login.img`, etc.)
2. property path within the image
3. property type
4. value/source

Supported phase-15 types:

- `string` — UTF-8 text value
- `int` — signed integer value
- `vector` — `x,y`
- `canvas` — PNG path, resolved relative to the manifest file unless absolute

Intermediate property nodes are created as subproperties. Existing canvas nodes
can also contain child metadata such as an `origin` vector. Image paths may
contain WZ directory components so custom content can mirror stock paths without
mounting a whole donor WZ.

The canonical manifest still contains only the harmless `EverLeafMeta.img` while
canvas support is validated separately in CI. A stock path is added only when the
corresponding EverLeaf-owned asset and current client path have both been reviewed.

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

The builder always reopens the generated WZ as v83 GMS and verifies every
manifest entry. CI additionally builds a nested-directory canvas/vector smoke WZ
from a deterministic PNG before publishing the canonical candidate artifact.

## Migration rule

Do not remove the existing `EverLeaf_UI.wz` compatibility path until equivalent
EverLeaf-owned assets have been migrated into this source tree, the generated
`EverLeaf_Custom.wz` has been runtime-tested in the client, and the launcher/patch
manifest has been updated in a separate reviewed phase.
