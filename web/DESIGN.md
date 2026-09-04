# EverLeaf Web — DESIGN.md

> Midnight Maple terminal: edge-to-edge dark canvas, bone-white compressed typography, monospaced telemetry, thin technical rules, compact controls, and one dominant local Maple-world artifact per major surface.

## Intent

EverLeaf should feel like a modern operating surface for a living Maple world: immersive enough to belong beside the game, precise enough for rankings/account/wiki data, and unmistakably different from a generic fantasy landing page.

The visual direction is informed by the selected Refero style reference, especially its midnight canvas, compressed display type, sparse telemetry labels, viewport-edge composition, flat surfaces, and restrained single-accent treatment. The implementation must remain original to EverLeaf and use only local/versioned EverLeaf assets.

## Principles

1. **World signal first.** The site behaves like a live portal into Maple World, not a brochure about it.
2. **Full-bleed composition.** Default to viewport-edge layouts with 14–20px gutters instead of centered marketing containers.
3. **Typography is the main graphic.** Large compressed headlines carry identity; labels and metadata use compact monospaced text.
4. **Flat over floating.** Use thin rules, dark tonal shifts, and spacing instead of rounded paper cards and shadows.
5. **One visual artifact.** A page may have one strong Maple-world artwork/composition; secondary UI stays restrained.
6. **Dense but legible.** Status, rankings, Wiki, account, downloads, and CMS surfaces should feel intentional at high information density.
7. **Preserve the product.** Visual changes must not break authentication, rankings, local WZ avatars, launcher routes, CMS bindings, status polling, forms, or server data.

## Core tokens

- `--terminal-bg: #12130f` — Midnight Carbon, primary canvas
- `--terminal-bg-soft: #171814` — alternate dark band
- `--terminal-panel: #1b1c18` — restrained panel surface
- `--terminal-text: #e4dfda` — Bone Glow, primary text
- `--terminal-muted: #9f9b95` — secondary copy
- `--terminal-dim: #706f69` — telemetry / low-priority metadata
- `--terminal-line: #3c3c38` — structural border/rule
- `--terminal-glow: #f5c2c8` — Rose Quartz, rare accent only
- `--terminal-good: #c8e7bd` — online/success

Do not use pure black or pure white as the main canvas/text pair.

## Typography

Use system/local fonts only; do not import proprietary reference fonts.

- **Display:** `Arial Narrow`, `Roboto Condensed`, `Helvetica Neue`, Arial, sans-serif.
- **Body/UI:** Inter-like system stack.
- **Telemetry:** `SFMono-Regular`, Consolas, `Liberation Mono`, Menlo, monospace.

Display text is uppercase, narrow, tightly tracked, and can reach 80–190px in large desktop compositions. Telemetry generally sits at 8–11px. Body copy stays compact, typically 12–16px with short measures.

## Layout

- Base outer gutter: 20px desktop, 14px compact screens.
- Avoid a fixed centered max-width on public surfaces.
- Base spacing unit: 4px.
- Sections use 1px structural rules instead of card shadows.
- Prefer 12-column/asymmetrical desktop compositions.
- Mobile collapses to one readable column while retaining the terminal identity.

## Shape and elevation

- Primary content surfaces: square / 0px radius.
- Pills are reserved for interactive controls, navigation states, and compact status actions.
- Avoid rounded card grids.
- Avoid drop shadows as hierarchy.
- Sticky navigation may use light backdrop blur; content surfaces should remain flat.

## Navigation

- Thin world-status/utility ribbon above the primary navigation.
- Compact numbered navigation items.
- Active route becomes a bone-white pill on midnight canvas.
- Login/account and Play Free remain obvious but visually restrained.
- Mobile navigation preserves numbered labels and the same dark system.

## Homepage

1. Full-height terminal hero with giant EVER / LEAF word treatment.
2. One central Maple-world artifact using local character artwork, restrained into the dark system rather than presented as a bright poster.
3. Live server telemetry with the existing polling IDs preserved.
4. Numbered quick-signal strip for Download, Account, Rankings, Wiki, and Journal.
5. World dossier explaining EverLeaf principles without a repeated card grid.
6. Three-step entry sequence for account → launcher → world.
7. Adventurer matrix using local class/instructor art.
8. Live World Journal + ranking data modules.
9. Wiki knowledge signal.
10. Large final transmission/CTA.

## Inner pages

All public routes inherit the same design language:

- dark canvas
- edge-aligned page hero
- compressed uppercase headline
- monospaced eyebrow/status text
- square flat panels
- minimal borders
- compact responsive layout

Do not rebuild working route logic just to achieve the visual treatment. Shared CSS and partials should carry most of the makeover.

## Rankings

- Keep local WZ-rendered character appearances and all live ranking bindings intact.
- Treat the leaderboard as live world telemetry rather than a fantasy podium card collection.
- High data density is acceptable when row rhythm and contrast remain clear.
- Rank emphasis should use typography and restrained semantic color, not metallic gradients or shadows.

## Wiki

- Keep WZ + MySQL provenance/data features visible.
- Search remains the primary action.
- Categories, entity pages, tables, and navigation use flat dark surfaces with rules rather than pastel cards.
- Technical data should look intentional, not developer-debug output.

## Account / Auth

- Two-column desktop composition is preferred: world/identity field + focused form surface.
- Inputs are dark, square, bordered controls with clear focus states.
- Preserve password, Discord link, recovery, character, rewards, vote, and security behavior.
- Do not hide important security/status text behind decorative UI.

## Downloads / Help

- Present launcher/client information as operational steps and system modules.
- Keep the primary download action obvious.
- Repair/help procedures should remain highly scannable.

## News / Articles / Legal

- Editorial content uses the same dark canvas and strong headline system.
- Reading copy gets a sensible measure even though the overall site is full-bleed.
- Images may be desaturated/dimmed to coexist with the system.

## CMS / Admin

Admin tools share the dark terminal language but prioritize legibility and form/table usability over dramatic presentation. No backend behavior or authorization should change for visual work.

## Motion

- 120–200ms for controls.
- Ambient hero rings/artifact movement may be slow and subtle.
- No excessive parallax, glow, bouncing cards, or decorative scroll choreography.
- Respect `prefers-reduced-motion`.

## Accessibility

- Preserve semantic headings, labels, forms, announcements, and live regions.
- Maintain visible keyboard focus.
- Keep controls near a 42–44px target where practical.
- Do not encode server/status state only by color.
- Responsive layouts must not require horizontal page scrolling.

## Do

- Use EverLeaf-owned/local art and sprites.
- Use large type, thin rules, and information hierarchy as the visual language.
- Keep the Rose Quartz accent rare.
- Make every major route feel part of one system.
- Preserve account, rankings, Wiki, launcher, CMS, payment, and server integrations.

## Do not

- Copy reference-site source code, assets, logos, or proprietary fonts.
- Return to parchment/cream storybook pages, soft pastel card grids, or large warm shadows.
- Use generic neon-gaming effects.
- Use glassmorphism as the main surface style.
- Center every section inside a 1200px marketing container.
- Change game-server/database behavior as part of a website visual redesign.
