# EverLeaf Web — DESIGN.md

> Max Yinger–informed midnight game terminal: near-black canvas, warm bone-white typography, extreme edge alignment, compact telemetry, pill interactions, and a single Maple-world visual artifact carrying the emotional weight.

## Source of truth

This redesign is intentionally based on the Refero style supplied by the project owner:
`https://styles.refero.design/style/a7891223-a93e-4731-a1aa-4079f1ee928b`

The reference is **Max Yinger**. EverLeaf adapts its design grammar, not its proprietary assets, fonts, code, or 3D artwork.

## Core idea

EverLeaf should feel like a live game terminal rather than a conventional fantasy portal. The page is one continuous dark plane. UI chrome is almost absent. Typography, edge positioning, tiny technical labels, live server data, and one strong Maple visual do the work.

## Non-negotiable visual rules

1. **Near-black canvas everywhere.** Public pages use `#12130f` as the dominant surface.
2. **Warm bone-white does almost all visual work.** `#e4dfda` is the primary text and UI color.
3. **Almost no accent color.** `#f5c2c8` may appear only as a soft illustration/art glow, never as CTA chrome.
4. **Flat surfaces.** No box shadows, no drop shadows, no glass cards, no raised panels.
5. **Compact spacing.** Base rhythm is 4px; standard content padding is 12px; section rhythm is 64px.
6. **No rounded cards.** Content clusters are defined by position and spacing, not containers.
7. **Pill interactions only.** Buttons, tags, and compact nav actions use `9999px` radius.
8. **Edge-anchored composition.** Brand top-left; primary navigation top-right; key data/status toward the lower corners; hero art in the visual center.
9. **Monospace telemetry.** Status, labels, timestamps, rankings metadata, server data, and small annotations should read like live instrumentation.
10. **Typography over decoration.** Large compressed display text replaces decorative panel chrome.

## Color tokens

- `--el-carbon: #12130f` — full canvas / page background
- `--el-bone: #e4dfda` — primary text, headings, button text
- `--el-vein: #3c3c38` — subdued rules, secondary metadata, quiet separators
- `--el-rose: #f5c2c8` — art-only ambient edge glow

No pure white. No pure black. No green/gold UI palette in this design system.

## Typography

Do not import the proprietary Refero/reference fonts. Use local/system substitutes.

- **Telemetry / labels:** `ui-monospace, "SFMono-Regular", Consolas, "Liberation Mono", monospace`
- **Hero display / wordmark substitute:** same monospace stack, uppercase, compressed line-height
- **Readable prose:** `Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`

### Scale

- display: `clamp(64px, 8vw, 112px)` with `line-height: .70`
- section heading: `clamp(28px, 3vw, 42px)` with `line-height: 1.05`
- body: `16px / 1.25`
- telemetry: `12px / 1.25`, letter-spacing `-.05em`

Use regular/medium visual weight wherever possible. Contrast comes from scale and family, not heavy bolding.

## Spacing

- base unit: 4px
- tiny gap: 4px
- control gap: 8px
- content padding: 12px
- larger cluster gap: 24px
- section gap: 64px
- viewport edge inset: 12px desktop, 10px mobile

## Layout

- Full bleed. Do not constrain public pages to a centered 1200px card layout.
- `.wrap` becomes an edge inset helper, not a max-width container.
- Homepage uses a corner-anchored z-pattern:
  - top-left: EverLeaf wordmark
  - top-right: navigation pills
  - center: one dominant Maple visual
  - bottom-left: hero statement + live world telemetry
  - bottom-right: server/account/action cluster
- Inner pages keep the same edge language while allowing readable content flow.
- Long-form text may use a readable measure, but the page itself remains full bleed.

## Navigation

- No conventional boxed navbar.
- EverLeaf appears as a compact wordmark stamp at top-left.
- Primary links are transparent bone-white pills at top-right.
- Active state uses an underline / bone-white fill inversion, not a new color.
- World/ribbon metadata becomes small telemetry, not a colored banner.

## Buttons and links

### Pill button
- transparent or bone-white fill
- 9999px radius
- 12px telemetry typography
- no shadow
- hover: invert bone/carbon or underline

### Inline link
- bone-white text
- 2px underline
- 2px radius maximum
- no color-changing hover gimmick

## Homepage

- One viewport-scale dark hero.
- Suppress the busy forest-as-background treatment.
- Use one existing EverLeaf character/world asset as the centered visual artifact, with only a restrained rose edge glow.
- Large hero statement sits low and left.
- Live server data reads like telemetry, not a card.
- Quick actions become compact pill/label clusters.
- Subsequent sections remain on the same carbon plane with 64px spacing and no card chrome.

## Rankings

- Preserve real local Character.wz renders.
- Podium characters become the dominant visual objects on the dark canvas.
- Rank, level, job, and EXP become telemetry labels.
- Leaderboard rows are flat, dense, and line-separated; no rounded table card.
- #1 is emphasized by scale/placement, not gold color.

## Wiki

- Preserve the live WZ + MySQL catalog.
- Search becomes a terminal-like command field.
- Record counts and data source state use telemetry.
- Category tiles lose colored cards; they become flat text/data clusters with subtle rules.

## Downloads / Help

- Present as operational checklists and compact action clusters.
- Launcher status, version, repair, and support steps should read like system instrumentation.
- Keep one obvious primary action, expressed as a filled bone-white pill.

## Auth / Account

- Remove decorative auth cards.
- Forms sit directly on the carbon canvas with restrained rules and 12px labels.
- Inputs are dark, flat, line-based controls with bone-white text.
- Account data becomes compact clusters with clear telemetry labels.

## News / Articles / Legal

- Editorial, sparse, dark reading experience.
- Metadata is monospace telemetry.
- Headlines are large and compressed.
- No decorative cards around article bodies.

## Footer

- Same carbon canvas.
- No separate footer panel.
- Wordmark / legal bottom-left, navigation pills bottom-right.
- Minimal 12px telemetry.

## Motion

- No floating cards, parallax panels, glossy hover lifts, or blur-heavy motion.
- Illustration may have one very subtle breathing/edge-light animation.
- Interactions: 120–180ms.
- Respect `prefers-reduced-motion`.

## Accessibility

- Bone/carbon contrast must remain readable.
- Keep visible focus rings using bone-white outlines.
- Maintain semantic headings, form labels, table semantics, and existing server/account integrations.
- Mobile controls remain at least 44px tall even if visual spacing is compact.

## Preserve

The redesign must not break:

- local Character.wz avatar rendering and saved equipment
- live rankings data
- WZ/MySQL Wiki catalogs
- account login/register/recovery/security workflows
- launcher/download paths
- live server status / 20-channel checks
- CMS content
- Discord integration
- existing public route URLs

## Do not

- copy Max Yinger/Refero source code, assets, 3D models, or proprietary fonts
- reintroduce parchment, soft green cards, gold reward UI, rounded fantasy panels, or glassmorphism
- add shadows or card elevation
- add new accent colors
- use centered SaaS containers for the main composition
- make every route look like the same boxed dashboard
