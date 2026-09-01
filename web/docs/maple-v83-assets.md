# EverLeaf v83 Web Asset Workflow

EverLeaf's website should never depend on third-party sprite URLs at runtime. Maple assets used by the website are exported locally, selected intentionally, copied into `web/public/assets/maple-v83/`, and served by EverLeaf itself.

## Recommended source of truth

For assets that must match the actual EverLeaf client, export them from the same v83 client data used by the project. WzComparerR2 can inspect WZ archives, and its Lua console can be used with batch-export scripts such as `WzComparerR2-Scripts` to emit PNG/GIF files.

Useful WZ families:

- `Character.wz` — character bodies, hair, face, equipment
- `Skill.wz` — skill icons and effects
- `Mob.wz` — monster and boss sprites
- `Npc.wz` — NPC sprites
- `Item.wz` — non-equipment item assets
- `Map.wz` — maps, tiles, objects, backgrounds
- `UI.wz` — classic client UI assets
- `Effect.wz` — visual effects

BannedStory4, Maple Editors, Spriters Resource, MapleStory Studio, and Orange Mushroom are useful visual/reference resources, but the live EverLeaf site should not hotlink their images. Only import assets you are permitted to use.

## Target layout

```text
web/public/assets/maple-v83/
  jobs/
  skills/
  monsters/
  bosses/
  npcs/
  items/
  equipment/
  maps/
  ui/
  characters/
  manifest.json
```

## Selective import

Do not dump an entire WZ archive into the website repository. Create a small selection JSON describing only the assets needed by the site.

Example `selection.json`:

```json
{
  "sourceLabel": "EverLeaf v83 WZ export",
  "assets": [
    {
      "id": "warrior-job-icon",
      "source": "Skill/100.img/skill.1001003.icon.png",
      "target": "jobs/warrior.png"
    },
    {
      "id": "orange-mushroom",
      "source": "Mob/0100100.img/stand.0.png",
      "target": "monsters/orange-mushroom.png"
    }
  ]
}
```

The exact export paths depend on the WZ exporter and client data. Verify the files visually before committing them.

Run:

```bash
cd web
node scripts/import-maple-assets.js --source "C:/path/to/wz-export" --manifest "C:/path/to/selection.json"
```

Or after the npm shortcut is available:

```bash
npm run import-maple-assets -- --source "C:/path/to/wz-export" --manifest "C:/path/to/selection.json"
```

The importer:

1. refuses path traversal and unsupported output formats;
2. copies only explicitly selected assets;
3. writes them under EverLeaf's local public asset directory;
4. creates a SHA-256 asset manifest for review and reproducibility.

## Website usage

After import, reference only local paths:

```html
<img src="/assets/maple-v83/jobs/warrior.png" alt="Warrior">
```

Never reference the original third-party host from EJS/CSS.

## Review checklist

Before an imported asset is merged:

- verify it corresponds to EverLeaf's v83-era content;
- verify transparency/cropping at desktop and mobile sizes;
- confirm source/usage rights and keep attribution notes where required;
- ensure it is not a temporary hotlink or remote redirect;
- keep the file reasonably sized for the website;
- ensure `manifest.json` matches the committed asset bytes.
