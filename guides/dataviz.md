# Data visualization

Charts are theme-adaptable the same way chrome is: a component references
**viz roles**, and `tools/viz.py` derives the role values from whatever
theme is active. No chart ever contains a hex.

## Roles (`tokens/omarchy-viz.css`, `tokens/viz.tokens.json`)

| Role | Job | Derivation |
|---|---|---|
| `--om-viz-cat-1…8` | identity (which series) | theme hues (red/orange/yellow/green/cyan/blue/magenta/brown), snapped into the OKLCH band for the mode, chroma ≥ 0.125, near-duplicate hues dropped, **order chosen by validator** (max worst-adjacent CVD ΔE). Slots past `--om-viz-series-count` alias to `other`. |
| `--om-viz-seq-1…7` | magnitude | one hue = `accent`; L walks from near-surface to accent to ink |
| `--om-viz-ord-1…4` | ordered categories | same hue, light end ≥ 2:1 on surface, ΔL ≥ 0.07 |
| `--om-viz-div-neg/mid/pos` | polarity | pos = accent, neg = the categorical hue farthest from accent in hue angle, mid = neutral |
| `--om-viz-status-good/warning/serious/critical` | state | green / yellow / orange / red (= urgent), snapped; **always glyph + label** |
| `--om-viz-surface / ink / ink-2 / muted / grid / baseline / other / emphasis` | chrome | background, foreground, fg→bg mixes (13 / 30 %), fg@.12, fg@.25, fg@.32, accent |

Every theme's derived palette was run through the reference validator
(`validate_palette.js` from the dataviz method): all 24 pass the hard gates
except **White** and **Vantablack**, whose ramps are exact grays by design
(the single-hue check is undefined on neutrals). Some themes carry fewer
series than eight — the **series cap** — because their hues collide under
CVD: Everforest and Gruvbox drop cyan + red, Hackerman drops cyan, Miasma and
Matte Black fall back to an ordinal ramp. `viz-palette.html` shows the
per-theme report; `tokens/viz.tokens.json` carries the validator output.

## Rules (from the dataviz method, unchanged)

1. **Pick the form before color.** One number → stat tile / hero; ratio vs
   limit → meter; magnitude → bars / heatmap (sequential); identity → grouped /
   stacked / lines (categorical); "this one matters" → emphasis; above/below →
   diverging. Never a dual axis. Never a 2-slice pie.
2. **Assign categorical slots in order, never cycled.** Beyond
   `--om-viz-series-count`, fold into "Other" (`--om-viz-other`) or facet.
   Color follows the entity, not its rank — filtering never repaints survivors.
3. **Marks:** bars ≤ 24 px, square at baseline; lines 2 px round; markers ≥ 8 px
   with a 2 px surface ring; area fills at ~8–10 %; 2 px surface gaps between
   touching fills; hairline solid grid in `--om-viz-grid`.
4. **Text wears text tokens, never the series color.** Identity comes from a
   swatch/line-key beside the text.
5. **Legend for ≥ 2 series; direct-label selectively** (extreme, endpoint, the
   story). Single series: no legend, the title names it.
6. **Hover layer by default:** crosshair + all-series tooltip on lines; per-mark
   tooltip on bars/cells. Tooltip is the popups surface. Values are also
   reachable via labels or the table view (`<details class="tv">`).
7. **Status colors are reserved.** A series that *means* good/bad wears status;
   "series 4" never does.
8. **Monochrome themes** (`--om-viz-monochrome: 1`): identity by lightness +
   direct labels + optional 45° texture; ≤ 4 series.

## In QML

The same derivation can run at shell start: read
`~/.local/state/omarchy/current/theme/colors.toml`, apply `tools/viz.py`'s
rules (port is ~150 lines), expose as a `Viz` singleton beside `Color`. Until
then, hard-derive per theme from `viz.tokens.json` and select by
`Color.currentThemePath`.

## Re-derive after adding a theme

```bash
OMARCHY_DS_VALIDATOR=/path/to/dataviz/scripts/validate_palette.js python3 tools/build.py
```
