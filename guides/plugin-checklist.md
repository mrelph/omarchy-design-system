# Plugin design checklist

Run before shipping any `~/.config/omarchy/plugins/<id>/` plugin or theme-aware app.

## Theme adaptability (blocking)
- [ ] `grep -nE '#[0-9a-fA-F]{3,8}|"white"|"black"|Qt\.rgba\(' *.qml` returns nothing outside comments.
- [ ] Every color is `Color.*`, `bar.foreground/background/urgent`, `Style.*Fill*`, `Style.*Border*`, or `Util.alpha(role, a)`.
- [ ] Renders correctly on **Catppuccin Latte, Flexoki Light, White** (light) and **Vantablack, Matte Black** (near-black). `omarchy theme set <name>` and look.
- [ ] Dim/secondary text uses `Qt.darker(fg, 1.4)` / `1.15`, not a hard alpha over black.
- [ ] Scrims/overlays use `Util.alpha(Color.background, 0.5–0.7)`.
- [ ] Nothing changes when `omarchy font set` runs except the glyphs (family bound to `Style.font.family`).
- [ ] Survives `[font] base-size = 16` in `~/.config/omarchy/shell.toml` (spacing via `Style.space`, sizes via `Style.font.*`).
- [ ] Corners follow `Style.cornerRadius`; switches auto-pill/square.

## Components
- [ ] Only `qs.Ui` primitives; no re-implemented buttons/toggles/fields.
- [ ] Destructive actions: `PanelActionButton { hoverColor: bar.urgent }` or `Button` with urgent foreground — plus `ConfirmDialog` if irreversible.
- [ ] Rows are `CursorSurface`; visuals derive from `hasCursor`/`current` only.

## Interaction
- [ ] j/k · h/l · Enter · Esc all work; Tab walks form controls.
- [ ] Mouse hover moves the keyboard cursor (single highlight).
- [ ] Bar pill: left/right/middle/scroll per the pattern; tooltip suppressed when a panel exists.
- [ ] Works in `top/bottom/left/right` bar positions; vertical falls back to icon-only.

## Data & state
- [ ] Stale data stays visible while refreshing; errors show inline, never blank.
- [ ] Settings via `manifest.json` `schema` + `setting(name, fallback)`, not a private file.
- [ ] No polling faster than needed; `Process` stdout collected with `waitForEnd`.

## Manifest
- [ ] `id` is `<author>.<name>`; `category`, `displayName`, `defaultSection` set.
- [ ] README with a screenshot in the *default* theme and one light theme.
