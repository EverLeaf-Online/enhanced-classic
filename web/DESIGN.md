# EverLeaf Web — DESIGN.md

> Storybook field journal meets classic MMORPG portal: warm paper, evergreen ink, hand-drawn energy, generous breathing room, and Maple-world character art used as the emotional anchor.

## Intent

EverLeaf should feel like a handcrafted companion site for a living Maple world — playful and nostalgic without looking juvenile, polished without becoming a generic SaaS dashboard, and readable enough to support rankings, account management, downloads, wiki data, news, and help pages.

This system is informed by Refero Styles patterns such as playful warm-paper canvases, mascot-led illustration, botanical restraint, strong display hierarchy, soft cards, and intentionally limited accent color. It must be adapted to EverLeaf rather than copied from any source website.

## Principles

1. **Game world first.** Character/map art and server identity should carry the emotion; UI chrome supports it.
2. **Warm, not sterile.** Use parchment/cream surfaces instead of pure white for most backgrounds.
3. **One strong brand voice.** Evergreen is structural; leaf green is action; gold is reward/status. Avoid rainbow UI.
4. **Big editorial moments.** Each page gets one memorable headline/hero composition, then quieter utility content.
5. **Soft but deliberate shapes.** Large cards are rounded and tactile; controls are pill-like where appropriate.
6. **Useful after download.** Rankings, Wiki, account, support, and news must feel as designed as the homepage.
7. **No fake game UI.** Do not imitate MapleStory client windows pixel-for-pixel; this is a modern web portal with nostalgic cues.

## Color system

### Core
- `--el-ink: #173f38` — primary text, structural dark surfaces
- `--el-ink-2: #2f5b52` — secondary text
- `--el-paper: #fbf6e9` — main page canvas
- `--el-paper-2: #f2ead7` — alternate surface / bands
- `--el-card: #fffdf5` — cards and forms
- `--el-line: #d7cfb7` — default borders

### Brand
- `--el-leaf: #59ad62` — primary CTA / active accents
- `--el-leaf-deep: #347b49` — hover / pressed state
- `--el-mint: #cce8ce` — pale accent surface
- `--el-sky: #dcefed` — cool supporting surface
- `--el-gold: #e5bd5d` — reward / status / premium emphasis
- `--el-peach: #f2b18e` — rare warm illustration accent, never primary action

### Semantic
- success: `#3f9954`
- warning: `#b27b26`
- danger: `#b64f45`
- info: `#4b8f9d`

## Typography

Use locally available/system fonts only. Do not import proprietary reference fonts.

- **Display:** Georgia, `Times New Roman`, serif — large, high-contrast, slightly editorial.
- **Interface/body:** Inter-like system stack: `ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`.
- **Utility labels:** same sans stack, 700–800 weight, uppercase, 0.08–0.14em tracking.

### Scale
- Hero display: clamp(3.4rem, 7vw, 7rem), 0.90–0.98 line-height
- Page title: clamp(2.5rem, 5vw, 4.8rem), 0.96–1.05
- Section title: clamp(2rem, 3.5vw, 3.6rem)
- Card title: 1.1–1.45rem
- Body: 15–17px, 1.65–1.8 line-height
- Utility: 10–12px

## Layout

- Max content width: 1200px
- Narrow reading width: 760px
- Section vertical gap: 72–120px desktop, 48–72px mobile
- Card padding: 22–32px
- Base spacing unit: 4px
- Prefer asymmetrical editorial grids over repeated equal-width boxes when content allows.

## Shape

- tiny controls: 8px radius
- inputs: 14px
- buttons: 999px pill by default
- standard cards: 22–28px
- feature/hero panels: 32–44px
- image frames: 28–40px

## Elevation

Shadows are soft and warm, never glossy:
- subtle: `0 1px 0 rgba(255,255,255,.8) inset, 0 10px 26px rgba(39,75,58,.08)`
- card: `0 18px 50px rgba(39,75,58,.11)`
- hero float: `0 30px 90px rgba(23,63,56,.18)`

Avoid glassmorphism as a dominant motif. Backdrop blur is acceptable only for sticky navigation.

## Navigation

- Sticky, paper-toned nav on inner pages.
- Homepage may begin over the hero, but must become solid on scroll.
- Active section should use leaf-green ink/highlight, not an underline-only treatment.
- Primary account/play CTA is a filled leaf-green pill.

## Buttons

### Primary
Leaf-green fill, cream text, slightly lifted shadow. Hover darkens and moves up 1px.

### Secondary
Paper/card fill, evergreen text, hairline border.

### Ghost
Transparent or low-opacity surface used only on dark/illustrated backgrounds.

No square corporate buttons. No neon glow.

## Cards

- Cards should feel like pages, stickers, or field-guide panels, not admin dashboard widgets.
- Large cards can use pastel category surfaces (mint, sky, pale gold, peach) but keep text evergreen.
- Prefer one dominant illustration/number/status rather than many small icons.
- Tables may sit inside a large paper card with rounded outer clipping.

## Homepage

1. Full visual hero using EverLeaf forest/character art.
2. Strong editorial line: one large statement, restrained supporting copy.
3. Server status as a compact floating field-note panel.
4. Quick actions as large tactile tabs/tiles rather than a SaaS icon grid.
5. "How to start" as an illustrated journey strip.
6. Features / classes / news / rankings should each have distinct composition, not identical card grids.
7. End with a confident green CTA band and an editorial footer.

## Inner-page heroes

Every major public page gets a visual intro band with:
- eyebrow label
- large serif title
- 1–2 sentence purpose statement
- optional illustration or compact status panel

Do not use the exact same hero height/composition on every page.

## Rankings

- Treat as a Hall of Legends, not a spreadsheet.
- Podium characters are the visual focus.
- Keep live character rendering intact.
- Leaderboard table should remain highly readable and responsive.
- Gold is reserved for #1 / rank emphasis; silver/bronze are subdued neutrals.

## Wiki

- Treat as an explorer field guide / encyclopedia.
- Search is the primary action.
- Data categories can use distinct pale surfaces while sharing one typography system.
- WZ/MySQL trust/status must be visible without reading like developer telemetry.

## Account / Auth

- Warm two-column composition on desktop: story/identity side + focused form card.
- Forms use generous labels, 48–52px controls, large hit targets.
- Security/reward sections are grouped as readable cards, not dense admin rows.

## Downloads / Help

- Downloads should feel like a "ready your client" workshop.
- Help should feel like a guide desk / handbook.
- Strong single primary action per section.

## News / Articles / Legal

- Editorial reading experience with generous measure and clear metadata.
- News cards can use larger image crops and fewer borders.
- Long-form article/legal content should avoid dashboard card repetition.

## Motion

- 150–260ms for controls.
- 400–700ms for section reveals / illustration drift.
- Hero ambient motion must be subtle.
- Respect `prefers-reduced-motion` and remove decorative movement.

## Accessibility

- Maintain WCAG-readable contrast.
- Keep visible focus states.
- Minimum 44px interactive targets when practical.
- Do not encode status only by color.
- Keep semantic headings and forms intact.

## Do

- Use EverLeaf-owned/local art and icons.
- Let large type and illustration create personality.
- Keep green/gold brand accents disciplined.
- Make each route feel intentionally composed.
- Preserve working account, rankings, Wiki, launcher, CMS, and server integrations.

## Do not

- Copy source-site code, assets, logos, or proprietary fonts.
- Recreate Refero example sites verbatim.
- Use generic dark gaming-neon styling.
- Use glassmorphism as the primary surface language.
- Overfill pages with cards, badges, gradients, or shadows.
- Sacrifice data density/readability for decoration.
