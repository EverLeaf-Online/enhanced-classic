# EverLeaf Web — DESIGN.md

> EverLeaf now uses a dark, full-bleed, edge-anchored operating-system aesthetic adapted from the Max Yinger Refero style reference: near-black canvas, warm bone-white type, compact telemetry, pill interactions, flat surfaces, and a single central game artifact carrying the visual depth.

## Intent

The website and CMS should feel like a live EverLeaf world terminal rather than a themed marketing site. Every page should read as a running system: current world state, real player data, launcher state, Wiki data, CMS queues, publishing controls, and account security all belong to the same visual language.

This is an EverLeaf adaptation of the chosen reference system. Do not copy reference code, proprietary fonts, assets, names, or 3D objects.

## Core principles

1. **Full-bleed first.** Avoid centered card stacks and conventional 1200px marketing containers.
2. **The interface is the layout.** Information is distributed to edges, corners, rails, split panes, and large empty fields.
3. **Two-color system.** Warm bone-white on midnight carbon does nearly all UI work.
4. **One visual artifact.** EverLeaf game art/character art may carry subtle rose edge light. UI chrome stays monochrome.
5. **Flat by design.** No decorative card shadows, glass panels, gradients, or elevation stacks.
6. **Compact telemetry.** Meta labels, counts, timestamps, status, IDs, and system state use 12px monospace treatment.
7. **Large compressed displays.** Page titles and primary live values are oversized and tight, creating cockpit-like density.
8. **Function survives the redesign.** Rankings, WZ avatars, Wiki, account forms, launcher downloads, CMS publishing, recovery, supporter tools, audit log, settings, and status checks remain intact.

## Color tokens

- `--terminal-bg: #12130f` — page canvas and primary surface
- `--terminal-ink: #e4dfda` — all primary text, headings, button text, form text
- `--terminal-line: #3c3c38` — separators, input outlines, subdued chrome
- `--terminal-dim: #9d9993` — secondary copy and noncritical telemetry
- `--terminal-rose: #f5c2c8` — visual-art edge light only; not normal UI chrome
- `--terminal-danger: #d79b92` — errors only
- `--terminal-success: #cfd7bd` — success text only; keep subdued

Do not introduce green/gold/blue CTA systems. The prior EverLeaf palette is retired for this layout.

## Typography

Use system/local substitutes only.

### Display
`"Arial Narrow", "Roboto Condensed", "DIN Condensed", Impact, sans-serif`

Use for:
- 64–104px hero statements
- 48–80px page titles
- giant player counts / level values / CMS totals

Weight: 400–500. Tight line height: 0.72–0.9.

### Interface / readable copy
`Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`

Use for body copy, forms, article text, Wiki descriptions, player names.

### Telemetry
`"IBM Plex Mono", "JetBrains Mono", "SFMono-Regular", Consolas, monospace`

Use at 11–12px for:
- labels
- route names
- status
- IDs
- timestamps
- counts
- table metadata
- CMS navigation

Letter spacing: approximately -0.04em to 0.04em depending on readability.

## Spacing

Base unit: 4px.

- inline gap: 4px
- compact control gap: 8px
- cluster gap: 12px
- content block gap: 24–32px
- section gap: 64px
- viewport edge padding: clamp(12px, 2vw, 28px)

Do not use large padded cards everywhere. Empty space should appear between clusters rather than inside containers.

## Shape

- cards / content blocks: 0px radius
- tables: 0px radius
- forms: 0px or 2px radius
- inline text links: 2px radius
- pills / tags / buttons: 9999px radius

## Elevation

None for UI.

No box-shadow. No drop-shadow. No blur-based panels. The only allowed depth effect is subtle glow/edge-light on the central EverLeaf visual artifact.

## Global shell

### Desktop
- brand stamp anchored top-left
- route / environment telemetry near brand
- primary navigation as pill links anchored top-right
- page content may extend edge-to-edge
- footer behaves like a bottom telemetry strip, not a marketing sitemap block

### Mobile
- preserve top-left brand
- navigation becomes a compact disclosure panel
- full-bleed rows collapse into stacked terminal clusters
- no horizontal overflow for forms/tables; tables may scroll within their own region

## Homepage

### First viewport
Use a full-height terminal composition:
- EverLeaf brand at top-left via global shell
- central floating Maple-world artifact made from local EverLeaf art
- large world-state readout at bottom-left
- server telemetry directly beside/below it
- vertical action pills bottom-right
- minimal descriptive copy; no traditional hero card

### Following sections
Use flat indexed rows, split strips, and dense logs:
- `01 / START` installation and account flow
- `02 / WORLD DATA` Wiki entry points
- `03 / JOB INDEX` classes as horizontal/stacked data rows
- `04 / WORLD LOG` news posts as journal/log lines
- `05 / HALL` live ranking preview with real character avatars

No repeating rounded feature-card grid.

## News

Treat news as a world log:
- giant `WORLD LOG` title
- left rail for category/count/current date context
- posts as bordered horizontal rows with timestamp, type, title, excerpt, arrow
- imagery optional and secondary

## Downloads

Treat downloads as a client deployment console:
- current launcher version / required state as giant telemetry
- recommended launcher as primary command block
- secondary files as compact manifest rows
- setup/repair instructions in a right-side diagnostic rail

## Rankings

Treat rankings as a live process monitor / Hall of Legends:
- live world status and query timestamp at edges
- top three character renders isolated in negative space rather than enclosed cards
- table becomes a flat ledger with strong row dividers
- search/filter controls resemble command inputs/pills
- keep `/character-avatar/:id.png` live WZ rendering and fallback logic intact

## Wiki

Treat Wiki as a database explorer:
- giant data query input
- category namespaces as compact command pills / index rows
- count totals rendered as telemetry
- results as flat database rows with type, ID, name, metadata
- WZ + MySQL status remains visible

## Auth

Treat login/register/recovery as secure terminal sessions:
- split viewport
- left side contains identity/system context and minimal giant title
- right side contains a compact form stack
- no warm cards or decorative marketing metrics
- fields use dark surface, bone text, line borders

## Account

Treat account as a player control surface:
- top telemetry: account, character count, NX, Discord state
- character roster as rows rather than cards
- reward/security/community tools as independent flat panes separated by rules
- preserve all forms and actions

## CMS

The CMS must be redesigned as an operations terminal, not merely reskinned.

### Shell
- fixed left navigation rail on desktop
- compact `STAFF://CMS` identity and environment state
- active module visually identified by bone-white text and a simple marker
- main pane fills the rest of the viewport

### Overview
- giant live world/player/account readouts across the top
- publishing queue and runtime state in asymmetric split panes
- audit activity as a log stream
- no rounded dashboard-card mosaic

### Manager pages
- shared left rail remains fixed
- list/edit screens become split views where practical
- list rows use compact telemetry columns
- forms use full-width flat editors with label rails
- tables and queues use separators, not elevated cards

### Editors
- metadata controls in a narrow side column
- main title/body editor takes remaining width
- publish state and save actions stay visible

## Interactions

Buttons:
- pill shape
- transparent by default
- bone text
- 1px `--terminal-line` border only when separation is needed
- hover may invert to bone background + dark text

Inline links:
- underline or minimal pill treatment

Inputs:
- dark background
- bone text
- 1px charcoal border
- square/2px corners
- visible focus outline in bone-white

## Motion

- 120–220ms UI transitions
- subtle central-artifact drift only
- no parallax-heavy section animation
- respect `prefers-reduced-motion`

## Accessibility

- retain skip link
- maintain semantic heading order
- preserve visible labels on forms
- keep focus indicators high contrast
- keep status text alongside any status color
- preserve minimum practical hit areas for navigation/buttons
- data tables remain keyboard/scroll accessible

## Hard rules

### Do
- restructure markup when the old layout fights this system
- keep the canvas near-black and typography warm off-white
- use dense telemetry labels to clarify live/system information
- use large display text as the primary hierarchy tool
- keep EverLeaf local art as the single visual depth source
- redesign CMS workflows and public pages under one coherent system

### Do not
- simply change fonts/colors on the old card layouts
- keep the previous rounded green/gold portal aesthetic
- use generic SaaS cards, glassmorphism, shadows, glossy gradients, or neon gamer chrome
- import Refero example code/assets/fonts
- remove or weaken live integrations for visual reasons
