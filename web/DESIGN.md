# EverLeaf Web — DESIGN.md

> Max Yinger–informed midnight game terminal: near-black canvas, warm bone-white type, extreme edge alignment, compact telemetry, pill interactions, and a single Maple-world visual artifact carrying the emotional weight.

## Source of truth

This redesign is intentionally based on the Refero style supplied by the project owner:
`https://styles.refero.design/style/a7891223-a93e-4731-a1aa-4079f1ee928b`

The reference is **Max Yinger**. EverLeaf adapts its design grammar, not its proprietary assets, fonts, code, or 3D artwork.

## Core tokens

- Canvas: `#12130f`
- Primary text: `#e4dfda`
- Secondary rules / dividers: `#3c3c38`
- Art-only edge glow: `#f5c2c8`
- Base spacing unit: `4px`
- Section gap: `64px`
- Card/content padding: `12px`
- Buttons/tags: `9999px` pill radius
- Cards/content clusters: `0px` radius

## Typography

Use system substitutes only.

- Telemetry: `ui-monospace, SFMono-Regular, Consolas, Liberation Mono, monospace`
- Display: same monospace stack, compressed with very tight line-height
- Body: `Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif`

Target scale:
- display: `64–112px`, line-height `.70`
- subheading: `30–48px`, line-height `1.05`
- body: `16px`, line-height `1.25`
- telemetry: `12px`, line-height `1.25`, letter-spacing `-.05em`

## Rules

1. Public pages are one near-black plane. No parchment sections, green cards, or gold UI.
2. Bone-white is the only real UI color. Rose appears only as subtle illustration edge-light.
3. No box shadows, drop shadows, glassmorphism, or raised cards.
4. Navigation and actions are compact text pills.
5. Content clusters are separated by 4–12px gaps and occasional charcoal rules, not card chrome.
6. Brand is anchored top-left, primary navigation top-right, world telemetry lower-left, key actions/status lower-right.
7. Hero art is centered and singular. On EverLeaf, use one existing Maple-world asset rather than copying the reference 3D artifact.
8. Large compressed type carries the page identity.
9. Route layouts remain distinct, but all share the same dark terminal grammar.
10. Admin CMS styling is excluded from this public redesign.

## Homepage

- Full viewport carbon hero.
- EverLeaf wordmark top-left.
- Navigation pills top-right.
- One centered Maple visual, monochrome/bone-toned with a very restrained rose edge glow.
- Large hero statement bottom-left.
- Live server/channel/player status bottom-right as telemetry, not a card.
- Quick actions become compact pill clusters.
- Remaining sections stay on the same canvas with 64px vertical spacing and flat content groups.

## Rankings

- Preserve real local Character.wz renders.
- Podium characters are dominant visual artifacts.
- Rank/level/job/EXP are telemetry labels.
- Dense flat table with charcoal rules; no rounded ranking card.
- #1 is emphasized through scale and composition, not gold.

## Wiki

- Preserve live WZ + MySQL data.
- Search reads like a terminal command field.
- Catalog counts and source state use telemetry.
- Categories are flat data clusters, not pastel cards.

## Downloads / Help

- Operational checklist feel.
- Launcher/version/repair/support information presented like system instrumentation.
- One obvious primary action using a filled bone-white pill.

## Auth / Account

- No decorative form card.
- Inputs are flat and line-based on the carbon canvas.
- Labels are 12px telemetry.
- Account/security/reward data uses compact information clusters.

## News / Articles / Legal

- Sparse dark editorial reading experience.
- Large compressed headlines.
- Metadata in monospace telemetry.
- No surrounding article cards.

## Footer

- Same carbon canvas.
- No separate footer panel.
- Compact link clusters and small telemetry-style legal copy.

## Preserve

Do not break:
- Character.wz saved appearance rendering
- live rankings
- WZ/MySQL Wiki
- login/register/recovery/account security
- launcher/download flows
- server-status and 20-channel checks
- CMS content
- Discord integration
- all public URLs

## Do not

- copy Max Yinger/Refero source code, assets, 3D models, or proprietary fonts
- reintroduce parchment, soft green cards, gold reward UI, glassmorphism, or fantasy-panel chrome
- add shadows or card elevation
- add extra accent colors
- turn the site back into a centered SaaS card dashboard
