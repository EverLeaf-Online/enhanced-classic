# Evan XML donor builder

This tool reconstructs the intermediate donor WZ set consumed by EverLeaf's narrow Evan v83 WZ importer.

## Authorized source contract

The source is the extracted `Evan/` directory from the pinned archive:

- Archive: `Evan.zip`
- Size: `61,860,666` bytes
- SHA-256: `961e0cbf826aca48efa619afec51fd12c2472a82e654e6e73542b5bf65a0e5ce`
- XML files: `45`
- Canvas nodes: `8,400`
- Canvas nodes missing `basedata`: `0`

The archive uses only these XML property tags:

- `imgdir`
- `canvas`
- `int`
- `short`
- `string`
- `vector`
- `uol`

Unsupported tags, missing files, extra files, malformed XML, or missing canvas `basedata` are fatal. The production ZIP wrapper checks the exact source SHA and exact 45-file layout before donor generation.

Expected layout:

- Character root: 1 image (`00002000`)
- Character/Dragon: 20 images (`01942000`–`01942004`, `01952000`–`01952004`, `01962000`–`01962004`, `01972000`–`01972004`)
- Skill root: 11 images (`2001`, `2200`, `2210`–`2218`)
- Skill/Dragon: 10 images (`2200`, `2210`–`2218`)
- String root: 1 image (`Skill`)
- UI root: 2 images (`Basic`, `UIWindow`)

## Outputs

- `Skill.wz`
- `Character.wz`
- `UI.wz`
- `String.wz`

These generated WZs are intermediate donor inputs only. They do not replace the full v83 client WZs directly. The manifest-driven Evan patcher copies only approved Evan nodes from these donors into the verified EverLeaf v83 baseline.

## Safety model

The pipeline fails closed on source SHA mismatch, source-layout mismatch, malformed XML, unsupported property types, missing canvas data, WZ write errors, generated-donor reparse errors, or missing required donor images/directories. Production publication is separate and only runs after the donor set is verified.
