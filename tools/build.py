import json, os, pathlib, base64
ROOT = pathlib.Path(__file__).resolve().parent.parent
(ROOT/"previews").mkdir(parents=True, exist_ok=True)
(ROOT/"tokens").mkdir(exist_ok=True)
(ROOT/"guides").mkdir(exist_ok=True)

import glob,re as _re
def _load(path):
    d={}
    for line in open(path,errors="ignore"):
        m=_re.match(r'\s*([a-z_0-9]+)\s*=\s*"?(#[0-9A-Fa-f]{6})',line)
        if m: d[m.group(1)]=m.group(2)
        m2=_re.match(r'\s*mode\s*=\s*"(\w+)"',line)
        if m2: d["mode"]=m2.group(1)
    return d
THEMES={}
for f in sorted(glob.glob("/usr/share/omarchy/themes/*/colors.toml"))+sorted(glob.glob(os.path.expanduser("~/.config/omarchy/themes/*/colors.toml"))):
    slug=pathlib.Path(f).parent.name
    d=_load(f)
    if "foreground" not in d or "background" not in d: continue
    d.setdefault("accent",d.get("blue","#888888")); d.setdefault("muted",d.get("dark_foreground",d["foreground"])); d.setdefault("red","#cc5555")
    d["name"]=slug.replace("-"," ").title(); d.setdefault("mode","dark")
    THEMES[slug]=d
DEFAULT_THEME="lake-sunset" if "lake-sunset" in THEMES else next(iter(THEMES))
SPACING = {"xxs":2,"xs":3,"sm":4,"md":6,"lg":8,"xl":10,"xxl":12,"xxxl":14,"huge":18,
 "control-gap":8,"control-padding-x":10,"control-padding-y":6,"input-padding-y":7,"control-height":28,"popup-row-height":28,
 "row-gap":8,"row-padding-x":12,"label-gap":4,"panel-gap":14,"panel-padding":18,"popup-padding":14,
 "dropdown-width":240,"searchable-dropdown-width":260,"number-field-width":120,"searchable-popup-min-height":220}
FONT = {"caption":(0.833,10),"body-small":(0.917,11),"body":(1.0,12),"subtitle":(1.083,13),"title":(1.167,14),
 "heading":(1.333,16),"display":(2.0,24),"display-large":(2.333,28),"icon-small":(0.917,11),"icon":(1.167,14),"icon-large":(1.5,18)}
STATES = {"normal":dict(fill=0.04,border=0.4,width=1),"hover-cursor":dict(fill=0.08,border=0.25,width=1),
 "focus":dict(fill=0.08,border=0.25,width=1),"selected":dict(fill=0.18,border=1.0,width=0),
 "pressed":dict(fill=0.22),"selection":dict(fill=0.35)}
BAR = {"size-horizontal":26,"size-vertical":28,"icon-slot":27,"icon-canvas":16,"icon-font":13,"status-slot":21}
SURFACES = {
 "bar":{"background":"background","background-alpha":1.0,"text":"foreground","active":"red"},
 "popups":{"background":"background","background-alpha":1.0,"text":"foreground","border":"hyprland.active-border","border-alpha":1.0},
 "tooltip":{"background":"background","background-alpha":0.97,"text":"foreground","border":"hyprland.active-border-foreground"},
 "notifications":{"background":"background","text":"foreground","border":"hyprland.active-border","countdown":"accent"},
 "menu":{"background":"background","text":"foreground","border":"hyprland.active-border-foreground","scrim":"background","scrim-alpha":0.5,
   "selected-background":"foreground","selected-background-alpha":0.08,"selected-text":"accent","selected-border-alpha":0.25},
 "launcher":{"background-alpha":0.95,"inherits":"menu"},
 "polkit":{"background":"background","text":"foreground","text-error":"red","border":"hyprland.active-border","border-error":"red","scrim-alpha":0.5,"accent":"accent"},
 "lock":{"background-alpha":0.8,"placeholder":"mix(foreground, background, 34%)","border-active":"hyprland.active-border","border-error":"red","selection":"accent","selection-alpha":0.45},
 "image-picker":{"scrim-alpha":0.5,"selected-border":"accent","unselected-border":"foreground","unselected-border-alpha":0.28},
}

# ---------- tokens json
tokens = {
 "$schema":"omarchy-design-tokens/1","name":"Omarchy Design System","version":"1.0.0",
 "source":{"colors":"~/.local/state/omarchy/current/theme/colors.toml","shell":"theme/shell.toml (from $OMARCHY_PATH/default/themed/shell.toml.tpl)",
           "qml":["qs.Commons.Color","qs.Commons.Style","qs.Commons.Border"],"hyprland":["decoration:rounding -> Style.cornerRadius","general:gaps_out / 2 -> Style.gapsOut"]},
 "palette":{"roles":["accent","selection","muted","background","dark_background","darker_background","lighter_background","foreground","dark_foreground","light_foreground","bright_foreground","red","yellow","orange","green","cyan","blue","magenta","brown","bright_*"],
            "shellRoles":{"foreground":"colors.foreground","background":"colors.background","accent":"colors.accent (fallback color4)","urgent":"colors.red (fallback color1)","muted":"colors.muted (fallback color8)"},
            "defaultTheme":DEFAULT_THEME,"themes":THEMES},
 "surfaces":SURFACES,
 "controls":{"states":STATES,"note":"fill = alpha(stateColor, fill); border = alpha(stateColor, border). State color defaults to foreground for every state. Priority: pressed > focus > hover-cursor > selected > active > normal."},
 "spacing":{"base":"Style.space(px) = px * spacingScale * fontScale, rounded, min 1","tokens":SPACING},
 "font":{"family":"monospace (fontconfig alias, resolved e.g. JetBrainsMono Nerd Font)","baseSize":12,
         "scale":{k:{"multiplier":m,"pxAt12":p} for k,(m,p) in FONT.items()},"letterSpacing":{"sectionHeader":1.0,"caps":1.2}},
 "bar":{"tokensAt12px":BAR,"scaleWithFont":True},
 "geometry":{"cornerRadius":"Hyprland decoration:rounding (0 on this machine)","gapsOut":"Hyprland general:gaps_out / 2 (10 -> 5 here)","surfaceBorderWidth":2,"controlBorderWidth":1,"separatorAlpha":0.12,"dimText":"Qt.darker(fg, 1.4)","bodyText":"Qt.darker(fg, 1.15)"},
}
(ROOT/"tokens/omarchy.tokens.json").write_text(json.dumps(tokens, indent=2))

# ---------- CSS
def css_theme(sel, t):
    lines=[f"{sel} {{"]
    for k,v in t.items():
        if k in("name","mode"): continue
        lines.append(f"  --om-{k.replace('_','-')}: {v};")
    lines.append("  --om-urgent: var(--om-red);")
    lines.append("}")
    return "\n".join(lines)
css = ["/* Omarchy Design System — CSS tokens. Mirrors qs.Commons.Color/Style. */",
 "/* THEMES ARE DATA. Components reference only role vars (--om-foreground/background/accent/urgent/muted, surface roles, alpha fills). Set data-om-theme=<slug> on <html> to swap; :root holds the active theme on this machine. */",
 css_theme(":root", THEMES[DEFAULT_THEME]),
 *[css_theme(f'[data-om-theme="{k}"]', t) for k,t in THEMES.items()],
 ":root {",
 "  /* typography (base 12, tracks `omarchy font set` via the monospace alias) */",
 '  /* local Nerd Font -> JetBrains Mono (Google Fonts) -> "Omarchy Glyphs" (tokens/omarchy-glyphs.woff2, Nerd Font icon subset) -> generic */',
 '  --om-font: "JetBrainsMono Nerd Font", "JetBrains Mono", "Omarchy Glyphs", ui-monospace, monospace;',
 "  --om-font-base: 12px;"]
for k,(m,p) in FONT.items(): css.append(f"  --om-font-{k}: calc(var(--om-font-base) * {m});  /* {p}px */")
css.append("  /* spacing: Style.space(px) at scale 1.0 */")
for k,v in SPACING.items(): css.append(f"  --om-space-{k}: {v}px;")
css += ["  /* geometry */","  --om-radius: 0px;            /* Hyprland decoration:rounding */","  --om-gaps-out: 5px;          /* gaps_out / 2 */",
 "  --om-surface-border: 2px;","  --om-control-border: 1px;",
 "  /* control states: color-mix on foreground */",
 "  --om-fill-normal:   color-mix(in srgb, var(--om-foreground) 4%, transparent);",
 "  --om-fill-hover:    color-mix(in srgb, var(--om-foreground) 8%, transparent);",
 "  --om-fill-selected: color-mix(in srgb, var(--om-foreground) 18%, transparent);",
 "  --om-fill-pressed:  color-mix(in srgb, var(--om-foreground) 22%, transparent);",
 "  --om-fill-selection:color-mix(in srgb, var(--om-foreground) 35%, transparent);",
 "  --om-border-normal: color-mix(in srgb, var(--om-foreground) 40%, transparent);",
 "  --om-border-hover:  color-mix(in srgb, var(--om-foreground) 25%, transparent);",
 "  --om-border-selected: var(--om-foreground);",
 "  --om-separator:     color-mix(in srgb, var(--om-foreground) 12%, transparent);",
 "  --om-text-dim:      color-mix(in srgb, var(--om-foreground) 72%, black);   /* Qt.darker 1.4 */",
 "  --om-text-body:     color-mix(in srgb, var(--om-foreground) 87%, black);   /* Qt.darker 1.15 */",
 "  /* bar */","  --om-bar-size-h: 26px; --om-bar-size-v: 28px; --om-bar-icon-slot: 27px; --om-bar-status-slot: 21px;",
 "}",
 "body.om { background: var(--om-background); color: var(--om-foreground); font: var(--om-font-body)/1.45 var(--om-font); }"]
(ROOT/"tokens/omarchy.css").write_text("\n".join(css)+"\n")

# ---------- preview scaffolding
css_text=(ROOT/"tokens/omarchy.css").read_text()
GLYPHS_B64 = base64.b64encode((ROOT/"tokens/omarchy-glyphs.woff2").read_bytes()).decode() if (ROOT/"tokens/omarchy-glyphs.woff2").exists() else ""
FONT_HEAD = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
  '<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">'
  '<style>@font-face{font-family:"Omarchy Glyphs";src:url(data:font/woff2;base64,' + GLYPHS_B64 + ') format("woff2");font-display:block}</style>')
BASE = FONT_HEAD + """<style>
%s
*{box-sizing:border-box}html,body{margin:0}
body{padding:24px;min-height:100vh}
.om-h{font-size:var(--om-font-caption);letter-spacing:1px;text-transform:uppercase;color:var(--om-text-dim);margin:0 0 10px}
.row{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.card{background:var(--om-background);border:var(--om-surface-border) solid var(--om-accent);border-radius:var(--om-radius);padding:var(--om-space-panel-padding)}
.btn{display:inline-flex;align-items:center;gap:6px;height:var(--om-space-control-height);padding:0 var(--om-space-control-padding-x);border-radius:var(--om-radius);font:inherit;color:var(--om-foreground);background:transparent;border:1px solid transparent;cursor:pointer}
.btn.bordered{background:var(--om-fill-normal);border-color:var(--om-border-normal)}
.btn.hover{background:var(--om-fill-hover);border-color:var(--om-border-hover)}
.btn.selected{background:var(--om-fill-selected)}
.btn.pressed{background:var(--om-fill-pressed)}
.btn.focus{background:var(--om-fill-hover);border-color:var(--om-border-hover);outline:0}
.btn:disabled{opacity:.4}
.sep{height:1px;background:var(--om-separator);margin:var(--om-space-panel-gap) 0}
.sw{width:56px;height:30px;border-radius:15px;background:var(--om-fill-selected);position:relative}
.sw i{position:absolute;top:4px;left:4px;width:22px;height:22px;border-radius:50%%;background:var(--om-foreground);opacity:.5}
.sw.on{background:var(--om-accent)}.sw.on i{left:30px;opacity:1}
.sq,.sq i{border-radius:0}
.field{height:30px;padding:0 var(--om-space-control-padding-x);border:1px solid var(--om-border-normal);background:var(--om-fill-normal);color:var(--om-foreground);font:inherit;border-radius:var(--om-radius);min-width:220px}
.field.focus{border-color:var(--om-border-hover);background:var(--om-fill-hover)}
.field::placeholder{color:var(--om-text-dim)}
.label{font-size:var(--om-font-caption);color:var(--om-text-dim);margin-bottom:var(--om-space-label-gap)}
.pill{display:inline-flex;align-items:center;gap:6px;height:var(--om-bar-size-h);padding:0 8px;font-size:var(--om-font-body)}
.pill .g{font-size:13px}
.bar{display:flex;justify-content:space-between;align-items:center;height:var(--om-bar-size-h);background:var(--om-background);color:var(--om-foreground);padding:0 6px}
.dot{width:4px;height:4px;border-radius:2px;background:var(--om-foreground)}
.cursor-row{display:flex;align-items:center;justify-content:space-between;padding:0 var(--om-space-row-padding-x);height:var(--om-space-control-height);border:1px solid transparent;border-radius:var(--om-radius)}
.cursor-row.cur{background:var(--om-fill-hover);border-color:var(--om-border-hover)}
.cursor-row.current{background:var(--om-fill-selected)}
.swatch{width:96px;border-radius:var(--om-radius);overflow:hidden;border:1px solid var(--om-separator)}
.swatch b{display:block;height:56px}
.swatch span{display:block;padding:6px;font-size:var(--om-font-caption)}
.swatch span small{display:block;color:var(--om-text-dim)}
.themes{position:fixed;top:8px;right:8px;display:flex;gap:4px}
.themes select{font:inherit;font-size:10px;padding:3px 6px;background:var(--om-fill-normal);color:var(--om-foreground);border:1px solid var(--om-border-normal);cursor:pointer}
</style>
<div class="themes"><select onchange="document.documentElement.setAttribute('data-om-theme',this.value)" style="font:inherit;font-size:10px;background:var(--om-background);color:var(--om-foreground);border:1px solid var(--om-border-normal)">%s</select></div>
""" % (css_text, "".join(f'<option value="{k}"{" selected" if k==DEFAULT_THEME else ""}>{t["name"]}</option>' for k,t in THEMES.items()))

def page(fname, group, title, body):
    (ROOT/"previews"/fname).write_text(f'<!-- @dsCard group="{group}" -->\n<meta charset="utf-8">\n<title>{title}</title>\n{BASE}<body class="om">\n{body}\n</body>\n')

# Colors
def swatches(keys):
    return '<div class="row">'+"".join(f'<div class="swatch"><b style="background:var(--om-{k})"></b><span>{k}<small>&lt;colors.toml&gt;</small></span></div>' for k in keys)+'</div>'
page("colors.html","Colors","Palette roles",
 '<p class="om-h">Shell roles (what Color.* resolves to)</p>'+swatches(["foreground","background","accent","urgent","muted"])+
 '<p class="om-h" style="margin-top:20px">Background ramp</p>'+swatches(["darker-background","dark-background","background","lighter-background","selection"])+
 '<p class="om-h" style="margin-top:20px">Foreground ramp</p>'+swatches(["dark-foreground","foreground","light-foreground","bright-foreground"])+
 '<p class="om-h" style="margin-top:20px">Semantic hues (terminal ANSI, rarely for chrome)</p>'+swatches(["red","orange","yellow","green","cyan","blue","magenta","brown"])+
 '<p style="color:var(--om-text-dim);font-size:var(--om-font-caption);margin-top:18px">Rule: chrome uses only foreground / background / accent / urgent. Hues are for data (charts, status glyphs), never for borders or fills.</p>')

# Surfaces
surf = ""
for s,d in SURFACES.items():
    rows="".join(f'<div style="display:flex;justify-content:space-between;gap:16px;font-size:var(--om-font-caption)"><span>{k}</span><span style="color:var(--om-text-dim)">{v}</span></div>' for k,v in d.items())
    surf+=f'<div class="card" style="width:260px"><div style="font-size:var(--om-font-title);margin-bottom:8px">[{s}]</div>{rows}</div>'
page("surfaces.html","Colors","Surface roles (shell.toml)",'<p class="om-h">Per-surface roles — every one falls back to the foundational palette</p><div class="row" style="align-items:flex-start">'+surf+'</div>')

# Typography
ty="".join(f'<div style="display:flex;align-items:baseline;gap:16px;margin:8px 0"><span style="width:120px;font-size:var(--om-font-caption);color:var(--om-text-dim)">{k} · {p}px · ×{m}</span><span style="font-size:var(--om-font-{k})">Omarchy shell — Style.font.{k.replace("-s","S").replace("-l","L")}</span></div>' for k,(m,p) in FONT.items() if not k.startswith("icon"))
page("typography.html","Type","Type scale",
 '<p class="om-h">One family (fontconfig <code>monospace</code> alias), base 12px, ratio-derived scale</p>'+ty+
 '<div class="sep"></div><p class="om-h">Section header · caption + letter-spacing 1</p><div class="om-h" style="color:var(--om-foreground)">Wi-Fi networks</div>'
 '<p class="om-h" style="margin-top:16px">Icons are glyphs: Nerd Font, icon-small 11 / icon 14 / icon-large 18</p><div class="row" style="font-size:18px">󰤨 󰂯 󰕾 󰁹 󰖙  󰚰 󰃭</div>'
 '<p style="color:var(--om-text-dim);font-size:var(--om-font-caption);margin-top:18px">Bind font.family to Style.font.family, never a literal. Bold is emphasis; never a second family, never italics for chrome.</p>')

# Spacing
sp="".join(f'<div style="display:flex;align-items:center;gap:12px;margin:4px 0"><span style="width:180px;font-size:var(--om-font-caption);color:var(--om-text-dim)">{k} · {v}px</span><i style="display:block;height:12px;width:{min(v,300)}px;background:var(--om-accent)"></i></div>' for k,v in SPACING.items())
page("spacing.html","Spacing","Spacing scale",'<p class="om-h">Style.space(px) — every token multiplies by [spacing] scale and font scale</p>'+sp)

# States
st='<div class="row">'+"".join(f'<button class="btn bordered {c}">{l}</button>' for c,l in [("","normal"),("hover","hover-cursor"),("focus","focus"),("selected","selected"),("pressed","pressed")])+'<button class="btn bordered" disabled>disabled</button></div>'
page("states.html","Foundations","Interaction states",
 '<p class="om-h">One vocabulary for every control: normal · hover-cursor · focus · selected · pressed</p>'+st+
 '<div class="sep"></div><p class="om-h">Alpha-on-foreground recipe</p><table style="font-size:var(--om-font-caption);border-collapse:collapse">'+
 "".join(f'<tr><td style="padding:3px 16px 3px 0">{k}</td><td style="padding:3px 16px 3px 0;color:var(--om-text-dim)">fill α {d.get("fill","—")}</td><td style="padding:3px 16px 3px 0;color:var(--om-text-dim)">border α {d.get("border","—")} · width {d.get("width","—")}</td></tr>' for k,d in STATES.items())+
 '</table><p style="color:var(--om-text-dim);font-size:var(--om-font-caption);margin-top:18px">Mouse hover and the keyboard cursor are the SAME state (hasCursor). Exactly one highlight on screen at any time. Focus mirrors hover unless a theme overrides.</p>')

# Buttons
page("buttons.html","Components","Button & ButtonGroup",
 '<p class="om-h">Button — text, icon, or both; bordered opt-in</p><div class="row"><button class="btn">Ghost</button><button class="btn bordered">Bordered</button><button class="btn bordered"><span>󰑐</span> Refresh</button><button class="btn bordered selected">Selected</button><button class="btn" style="color:var(--om-urgent)">󰆴 Forget</button></div>'
 '<div class="sep"></div><p class="om-h">ButtonGroup — pick one of N, single Tab stop, h/l walks</p><div class="row" style="gap:0"><button class="btn bordered selected">Top</button><button class="btn bordered">Right</button><button class="btn bordered">Bottom</button><button class="btn bordered hover">Left</button></div>'
 '<div class="sep"></div><p class="om-h">PanelActionButton — 22px icon at a row\'s right edge</p><div class="cursor-row cur" style="width:320px"><span>Home Wi-Fi 󰤨</span><span style="display:flex;gap:4px"><span class="btn" style="height:22px;padding:0 4px">󰌆</span><span class="btn" style="height:22px;padding:0 4px;color:var(--om-urgent)">󰆴</span></span></div>')

# Toggles
page("toggles.html","Components","Toggle & ToggleSwitch",
 '<p class="om-h">ToggleSwitch — pill when Hyprland rounding &gt; 0, square when 0 (this machine: 0)</p><div class="row"><div class="sw on sq"><i></i></div><div class="sw sq"><i></i></div><div class="sw on"><i></i></div><div class="sw"><i></i></div></div>'
 '<div class="sep"></div><p class="om-h">Toggle — labeled row, click anywhere</p><div class="card" style="width:380px;padding:8px"><div class="cursor-row cur" style="height:auto;padding:8px 12px"><div><div style="font-size:var(--om-font-subtitle)">Night light</div><div style="font-size:var(--om-font-caption);color:var(--om-text-dim)">Warm the display after sunset</div></div><div class="sw on sq" style="transform:scale(.8)"><i></i></div></div><div class="cursor-row" style="height:auto;padding:8px 12px"><div><div style="font-size:var(--om-font-subtitle)">Stay awake</div><div style="font-size:var(--om-font-caption);color:var(--om-text-dim)">Inhibit idle and lock</div></div><div class="sw sq" style="transform:scale(.8)"><i></i></div></div></div>')

# Inputs
page("inputs.html","Components","TextField, NumberField, Dropdown",
 '<p class="om-h">TextField — 30px, inline variant drops to 22–26px</p><div class="row"><input class="field" placeholder="Search…"><input class="field focus" value="Focused"><input class="field" type="password" value="hunter2"></div>'
 '<div class="sep"></div><p class="om-h">Dropdown — trigger uses control chrome; popup uses [popups] surface</p><div class="row" style="align-items:flex-start"><div><div class="label">Output device</div><div class="field" style="display:flex;justify-content:space-between;align-items:center;width:240px"><span>Speakers</span><span>󰅀</span></div></div>'
 '<div class="card" style="width:240px;padding:var(--om-space-popup-padding);border-width:1px"><div class="cursor-row current">Speakers</div><div class="cursor-row cur">Headphones</div><div class="cursor-row">HDMI</div></div></div>'
 '<div class="sep"></div><p class="om-h">NumberField — 120px</p><div class="row"><div class="field" style="min-width:120px;width:120px;display:flex;justify-content:space-between;align-items:center"><span>15</span><span style="color:var(--om-text-dim)">min</span></div></div>')

# Panel anatomy
page("panel.html","Patterns","Panel anatomy",
 '<p class="om-h">Bar popout panel — PanelHero · PanelSeparator · PanelSectionHeader · CursorSurface rows · PanelSlider</p>'
 '<div class="card" style="width:380px"><div style="display:flex;gap:14px;align-items:center"><span style="font-size:var(--om-font-display)">󰖙</span><div style="flex:1"><div style="font-size:var(--om-font-title)">Kirkland · 17°</div><div style="font-size:var(--om-font-caption);color:var(--om-text-dim)">Partly cloudy · updated 2m ago</div></div><span class="btn" style="height:22px;padding:0 4px">󰑐</span></div>'
 '<div class="sep"></div><div class="om-h">Forecast</div>'
 '<div class="cursor-row cur"><span>Thu</span><span style="color:var(--om-text-dim)">19° / 12°</span></div><div class="cursor-row"><span>Fri</span><span style="color:var(--om-text-dim)">21° / 13°</span></div><div class="cursor-row"><span>Sat</span><span style="color:var(--om-text-dim)">18° / 11°</span></div>'
 '<div class="sep"></div><div class="om-h">Volume</div><div style="display:flex;align-items:center;gap:10px;padding:0 12px"><span>󰕾</span><div style="flex:1;height:4px;background:var(--om-fill-selected);position:relative"><i style="position:absolute;left:0;top:0;height:4px;width:62%;background:var(--om-foreground)"></i><i style="position:absolute;left:62%;top:-5px;width:14px;height:14px;margin-left:-7px;border-radius:7px;background:var(--om-foreground)"></i></div><span style="font-size:var(--om-font-caption);color:var(--om-text-dim)">62%</span></div>'
 '<div class="sep"></div><div style="font-size:var(--om-font-caption);color:var(--om-text-dim)">j/k move · h/l adjust · Enter act · Esc close</div></div>'
 '<p style="color:var(--om-text-dim);font-size:var(--om-font-caption);margin-top:18px">Border = [popups] border (Hyprland active-border gradient), 2px. Padding 18. Gap between sections 14. Anchored on the side opposite the bar, offset gapsOut (5px).</p>')

# Bar widget
page("bar-widget.html","Patterns","Bar widget & pill",
 '<p class="om-h">Top bar at 26px — left / center (anchored on clock) / right</p>'
 '<div class="bar"><div class="row" style="gap:0"><span class="pill"><span class="g"></span></span><span class="pill">1 <b style="opacity:.5">2 3</b></span></div><div class="row" style="gap:0"><span class="pill" style="font-weight:600">Thursday 14:32</span><span class="pill"><span class="g">󰖙</span>17°</span></div><div class="row" style="gap:0"><span class="pill"><span class="g">󰤨</span></span><span class="pill" style="position:relative"><span class="g">󰕾</span><i class="dot" style="position:absolute;bottom:2px;left:50%;margin-left:-2px"></i></span><span class="pill"><span class="g">󰁹</span></span><span class="pill" style="color:var(--om-urgent)"><span class="g">󰑐</span></span></div></div>'
 '<div class="sep"></div><p class="om-h">Pill rules</p><ul style="font-size:var(--om-font-caption);color:var(--om-text-dim);line-height:1.8;padding-left:16px"><li>Icon slot 27px, glyph canvas 16px, glyph font 13px — use BarIconButton, it optically centres the glyph.</li><li>Status widgets (text + glyph) use Style.bar.statusSlot (21px).</li><li>Attention colour is <code>bar.active</code> (= red) — reserve it for recording / updates / alerts.</li><li>Open-panel dot sits under the pill; the bar draws it, not the widget.</li><li>Left = open panel · right = secondary action · middle = refresh · scroll = adjust. Tooltip off when a panel exists.</li><li>Vertical bars: fall back to icon-only.</li></ul>')

# Notification
page("notification.html","Patterns","Notification card",
 '<p class="om-h">NotificationCard — 380px, urgency drives the accent stripe colour</p>'
 '<div class="card" style="width:380px;padding:10px 12px;display:flex;gap:12px;align-items:center"><span style="font-size:var(--om-font-display-large);width:40px;text-align:center">󰂚</span><div style="flex:1"><div style="display:flex;justify-content:space-between"><span style="font-size:var(--om-font-subtitle);font-weight:600">Reminder</span><span style="font-size:var(--om-font-caption);color:var(--om-text-dim)">now</span></div><div style="font-size:var(--om-font-body-small);color:var(--om-text-body)">Pickup Jack at the rink</div></div></div>'
 '<div style="height:10px"></div><div class="card" style="width:380px;padding:7px 12px;border-color:var(--om-urgent)"><span style="color:var(--om-urgent)">󰀦</span> Battery critically low</div>'
 '<div style="height:10px"></div><div class="card" style="width:380px;padding:7px 12px;border-color:var(--om-text-dim)"><span>󰋼</span> Silenced notifications</div>'
 '<p style="color:var(--om-text-dim);font-size:var(--om-font-caption);margin-top:18px">Critical = urgent, Low = dim, Normal = notifications.countdown (accent). Left click opens, right click dismisses. Send via <code>omarchy-notification-send -g "󰂚" "…"</code> to get the glyph slot.</p>')

# Cursor surface
page("cursor-rows.html","Components","CursorSurface rows",
 '<p class="om-h">Keyboard+mouse navigable rows — one highlight, ever</p><div class="card" style="width:380px;padding:8px"><div class="cursor-row current"><span>󰤨 Home</span><span style="font-size:var(--om-font-caption);color:var(--om-text-dim)">connected</span></div><div class="cursor-row cur"><span>󰤥 Neighbour-5G</span><span style="font-size:var(--om-font-caption);color:var(--om-text-dim)">-62 dBm</span></div><div class="cursor-row"><span>󰤟 CoffeeShop</span><span style="font-size:var(--om-font-caption);color:var(--om-text-dim)">open</span></div></div>'
 '<p style="color:var(--om-text-dim);font-size:var(--om-font-caption);margin-top:18px"><code>current</code> = selected fill (persistent). <code>hasCursor</code> = hover-cursor fill + border. Rows never read containsMouse for colour; hover updates the panel\'s cursor at the root.</p>')

def mini(slug):
    t=THEMES[slug]
    return f'''<div data-om-theme="{slug}" style="width:250px;padding:12px;background:var(--om-background);color:var(--om-foreground);border:2px solid var(--om-accent);font-size:var(--om-font-caption)">
<div style="display:flex;justify-content:space-between;margin-bottom:8px"><b>{t["name"]}</b><span style="color:var(--om-text-dim)">{t["mode"]}</span></div>
<div class="row" style="gap:4px"><span class="btn bordered" style="height:24px;font-size:10px">Normal</span><span class="btn bordered hover" style="height:24px;font-size:10px">Hover</span><span class="btn bordered selected" style="height:24px;font-size:10px">Selected</span></div>
<div class="sep" style="margin:8px 0"></div>
<div class="cursor-row cur" style="height:24px;font-size:10px;padding:0 8px"><span>󰤨 Home</span><span style="color:var(--om-text-dim)">connected</span></div>
<div class="cursor-row" style="height:24px;font-size:10px;padding:0 8px"><span>󰤥 Cafe</span><span style="color:var(--om-urgent)">weak</span></div>
<div style="margin-top:8px;display:flex;gap:6px;align-items:center"><div class="sw on sq" style="transform:scale(.6);transform-origin:left"><i></i></div><span style="color:var(--om-text-dim)">accent = {t["accent"]}</span></div></div>'''
page("theme-contract.html","Foundations","Theme contract",
 '<p class="om-h">Same components, zero per-theme code — only the role values change</p><div class="row" style="align-items:flex-start">'+"".join(mini(k) for k in THEMES)+'</div>'
 '<p style="color:var(--om-text-dim);font-size:var(--om-font-caption);margin-top:18px">A component passes the contract if it renders correctly under every theme above without a single theme-specific branch. Light themes (Catppuccin Latte, Flexoki Light, White) are the usual failure: hard-coded dark alphas or "#fff" text.</p>')
import sys; sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from build_ext import run as _ext
_ext(ROOT, THEMES, DEFAULT_THEME, page, BASE, None, None)
print("ok", len(THEMES), "themes")
