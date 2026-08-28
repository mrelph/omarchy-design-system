# Floating app design

An Omarchy app is a Hyprland client. The compositor owns the frame; the app
owns only its content. Truth comes from `$OMARCHY_PATH/default/hypr/looknfeel.lua`
and `windows.lua`:

| Property | Value | Consequence for the app |
|---|---|---|
| border | 2 px, **accent** (or theme gradient) when active, `rgba(595959aa)` inactive | draw no border of your own |
| gaps | out 10 / in 5 | no outer margin; content starts at the window edge + panel padding 18 |
| rounding | 0 (theme may set > 0 → read it) | corners follow `Style.cornerRadius`; switches auto-pill |
| opacity | .985 active / .96 inactive (`default-opacity` tag) | never composite your own translucency on top |
| shadow / blur | off | no drop shadows, no glass |
| title bar | none; maximize suppressed | no title text, no ×, no traffic lights; app name goes in the toolbar as text |
| move / resize / close | Super+drag · Super+W | don't re-implement |

## Float rule (`~/.config/hypr/windows.lua`)

```lua
o.window({ class = "^(your-app)$" }, { float = true, size = "1200 800", center = true })
o.window({ class = "^(your-app)$", title = "^(Preferences)$" }, { float = true, size = "640 480", center = true })
```
Tile-friendly by default; float utility/dialog windows. Sizes: dialog 480×auto ·
utility 640×480 · app 1200×800 or `60% 70%` · palette 640×420.

## Anatomy (`previews/app-window.html`, `app-shell.html`)

```
┌ toolbar 36 ── app name · tabs · [search /] · primary action ─────┐
│ nav 200   │ content (flex)                        │ inspector 220│
│ rows 26   │ section header · CursorSurface rows   │ (optional)   │
├ status 22 ── counts · freshness · kbd hints ─────────────────────┤
```
- Every list row is a `CursorSurface`; `j/k` walk, `h/l` cross columns,
  `Enter` act, `Esc` back, `/` search, `?` help. Mouse hover moves the cursor.
- Section headers = caption + letter-spacing 1. Separators = fg@.12.
- Primary action = bordered/selected Button; destructive = urgent text, then
  `ConfirmDialog`.
- Command palette = the `[menu]` surface (scrim .5, fg-border, selected row
  fg@.08 + accent text) so it matches `omarchy-menu`.
- States: empty (display glyph + one line + one action), loading (stale data at
  .6 opacity; skeleton on first load only), error (inline urgent row + Retry).
- Badges/chips/kbd use chrome colors only: accent = highlighted, urgent =
  attention.

## Motion (`previews/motion.html`)

Lifted from Hyprland's default animation table (speed × 100 ms):
enter 400 ms easeOutQuint popin 87 % · exit 150 ms linear · fade 300 ms quick ·
micro 150 ms almostLinear · emphasis 540 ms easeOutQuint.
`prefers-reduced-motion` / `animations.enabled = false` → durations 0.

## Toolkit mapping

| Role | Web (`tokens/omarchy.css`) | QML (`qs.Commons`) | GTK4 / libadwaita | Qt Widgets |
|---|---|---|---|---|
| background | `--om-background` | `Color.background` | `@window_bg_color` | `QPalette::Window` |
| foreground | `--om-foreground` | `Color.foreground` | `@window_fg_color` | `QPalette::WindowText` |
| accent | `--om-accent` | `Color.accent` | `@accent_bg_color` | `QPalette::Highlight` |
| urgent | `--om-urgent` | `Color.urgent` | `@error_color` | — |
| hover fill | `--om-fill-hover` | `Style.hoverFill` | `alpha(fg,.08)` | — |
| font | `--om-font` | `Style.font.family` | `monospace` alias | `QFont("monospace")` |

Web apps: load `tokens/omarchy.css`, generate the `:root` block from the live
`colors.toml` at start (or serve it from the shell), and set `data-om-theme`
on theme change.
