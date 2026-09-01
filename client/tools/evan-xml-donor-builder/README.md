# Evan XML donor builder

This tool reconstructs the minimal donor WZ set consumed by EverLeaf's narrow Evan WZ importer.

## Authorized source contract

The source directory is the extracted `Evan/` directory from the authorized Evan archive used for the backport.

The current archive has 52 XML files and only uses these XML property tags:

- `imgdir`
- `canvas`
- `int`
- `short`
- `string`
- `vector`
- `uol`

Unsupported property tags are intentionally fatal rather than silently discarded.

Expected source layout/counts:

- Skill root images: 11 (`2001`, `2200`, `2210` through `2218`)
- Skill/Dragon images: 10 (`2200`, `2210` through `2218`)
- Character root images: 1 (`00002000`)
- Character/Dragon images: 20 (`01942000`-series through `01972004`)
- UI root images: 2 (`Basic`, `UIWindow`)
- String root images: 1 (`Skill`)

The XML contains embedded PNG canvas `basedata`; the builder decodes that data and writes real WZ canvas properties.

## Outputs

- `Skill.wz`
- `Character.wz`
- `UI.wz`
- `String.wz`

Generated donors are intermediate build inputs. They are not intended to replace the full v83 client WZs directly. The existing manifest-driven Evan patcher copies only approved Evan nodes into the verified EverLeaf baseline.

## Safety model

The builder fails closed on malformed XML, missing `basedata`, unsupported property types, WZ write errors, or reparse failures. CI exercises an XML -> WZ -> reparse round trip before merge.

The pull-request gate is intentionally rerun against the final branch head whenever the builder or its validation contract changes. A green final-head round trip is required before merge.
