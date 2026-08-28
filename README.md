# Omarchy Design System

A theme-adaptable design system for Omarchy shell plugins, panels, and apps.
It is **derived from the shell's real token sources**, not invented alongside them:

| Layer | Source of truth | Read via |
|---|---|---|
| Palette | `~/.local/state/omarchy/current/theme/colors.toml` | `qs.Commons.Color.{foreground,background,accent,urgent,muted}` |
| Surface roles | theme `shell.toml` (generated from `$OMARCHY_PATH/default/themed/shell.toml.tpl`) | `Color.{bar,popups,tooltip,notifications,menu,polkit,lock,imagePicker}.*` |
| Control states, spacing, type, bar size | `[controls] [spacing] [font] [bar]` in `shell.toml` | `qs.Commons.Style.*` |
| Geometry | Hyprland `decoration:rounding`, `general:gaps_out` | `Style.cornerRadius`, `Style.gapsOut` |
| Borders | any of the above | `qs.Commons.Border.{controlSpec,surfaceSpec,flat}` |

## The one rule: themes are data, the system is roles

A component never knows which theme is active. It references **roles** —
`foreground`, `background`, `accent`, `urgent`, `muted`, a surface role, or an
alpha-on-foreground state fill — and the theme supplies the values. Twenty-four
themes are on this machine (22 stock + `aether`, `kraken-depths`, `lake-sunset`);
a component passes the contract when it renders correctly under all of them,
including the light ones, with zero theme-specific branches.

Concretely:

- **Never** write a hex color, `"#fff"`, `"white"`, `Qt.rgba(0,0,0,…)` in a plugin.
- **Never** assume dark mode. Overlays use `Util.alpha(Color.background, …)`, text dims use `Qt.darker(fg, 1.4)` — both invert correctly on light themes.
- Semantic hues (`red`, `green`, `blue`…) are for *data* (chart series, status glyphs) — never for chrome. Chrome is foreground/background/accent/urgent only.
- `accent` is the theme's voice (borders, selected text, countdown). `urgent` (= theme `red`) is reserved for attention: recording, critical battery, destructive hover.
- Fills are alphas over `foreground`, so they read as "a touch of ink" on every palette: normal 0.04 · hover-cursor 0.08 · selected 0.18 · pressed 0.22 · text-selection 0.35.
- Shape follows the compositor: `Style.cornerRadius` (0 here → sharp, square switches), `Style.gapsOut` for edge offsets.
- Font follows `omarchy font set`: bind `font.family: Style.font.family`; never a literal family.

## Tokens

- `tokens/omarchy.tokens.json` — machine-readable: roles, all theme palettes, surfaces, states, spacing, type scale, bar dimensions.
- `tokens/omarchy.css` — the same as CSS custom properties (`--om-*`) for web-based Omarchy tooling (dashboards, docs, Claude Design pages). `:root` is the active theme; `[data-om-theme="<slug>"]` swaps it.

### Type scale (base 12, mono)
caption 10 · body-small 11 · body 12 · subtitle 13 · title 14 · heading 16 · display 24 · display-large 28 · icon-small 11 · icon 14 · icon-large 18.
Section headers are caption + letter-spacing 1. Bold = emphasis. No second family, no italics in chrome.

### Spacing (`Style.space(px)`, scales with font)
xxs 2 · xs 3 · sm 4 · md 6 · lg 8 · xl 10 · xxl 12 · xxxl 14 · huge 18 ·
control-height 28 · control-padding 10×6 · row-padding-x 12 · row-gap 8 · panel-padding 18 · panel-gap 14 · popup-padding 14 · dropdown-width 240.

### Bar (at 12px, scales with font)
horizontal 26 · vertical 28 · icon-slot 27 · icon-canvas 16 · icon-font 13 · status-slot 21.

## Components (all in `qs.Ui`, previewed in `previews/`)

| Use | Component | Never |
|---|---|---|
| Any clickable thing | `Button` (text / icon / `bordered` / `selected`) | a bare `MouseArea` + `Rectangle` |
| Pick one of N | `ButtonGroup` | N unrelated Buttons |
| On/off with label | `Toggle` (row) / `ToggleSwitch` (bare) | a checkbox |
| Text / number / choice | `TextField`, `NumberField`, `Dropdown`, `SearchableDropdown`, `MultiSelect` | QtQuick.Controls defaults |
| Row-edge action | `PanelActionButton` (`hoverColor: urgent` for destructive) | |
| Navigable list row | `CursorSurface` (`hasCursor` / `current`) | reading `containsMouse` for color |
| Value | `PanelSlider` | |
| Panel scaffold | `Panel` + `PanelHero` + `PanelSeparator` + `PanelSectionHeader` | |
| Bar entry | `BarWidget` + `BarIconButton` | hand-centred glyphs |
| Floating card | `PopupCard`, `BorderSurface` | `Rectangle.border` with a hex |
| Confirm | `ConfirmDialog` | |
| Tooltip | `PanelToolTip` | |

Live reference: `omarchy dev ui-preview` opens the shell's own gallery, rendered with the real components under the active theme.

## Patterns

- **Panel anatomy**: hero (icon display-size + title + meta + trailing control) → separator → section header → rows → separator → footer hint. Border = `[popups]` (Hyprland active-border gradient) at 2px; padding 18; anchored opposite the bar, offset `gapsOut`.
- **Keyboard = mouse**: one `focusSection` + `selectedIndex` at the panel root; `j/k` walk, `h/l` local, `Enter` act, `Esc` close. Hover writes into the same state. One highlight on screen, ever.
- **Bar pill**: left = open panel · right = secondary action · middle = refresh · scroll = adjust. Tooltip off when a panel exists. Icon-only in vertical bars. Attention colour is `bar.active`.
- **Notification**: 380 wide; urgency → accent stripe (critical = urgent, low = dim, normal = countdown/accent).
- **Loading / stale**: keep stale data visible; show a spinner in place, never blank the panel.

## Additive layers (v1.1)

- **Data viz** — `tokens/omarchy-viz.css`, `tokens/viz.tokens.json`, derived per theme by `tools/viz.py` and checked with the dataviz validator; cards `viz-*.html`. See `guides/dataviz.md`.
- **Floating app** — window anatomy from Hyprland defaults, app shell, command palette, dialogs, states, table; cards `app-*.html`, `command-palette.html`. See `guides/floating-app.md`.
- **Motion** — tokens lifted from Hyprland's animation table (`motion.html`).
- **Iconography, density, feedback, contrast matrix** — `iconography.html`, `density.html`, `feedback.html`, `a11y-contrast.html`.

Rebuild everything: `python3 tools/build.py` (set `OMARCHY_DS_VALIDATOR` to the dataviz `validate_palette.js` to record validator results).

See `guides/plugin-checklist.md`, `guides/qml-recipes.md`, `guides/dataviz.md`, `guides/floating-app.md`.
