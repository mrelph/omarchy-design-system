"""Additive layers: data-viz, floating app, motion/icons/density/feedback/a11y.
Called from build.py with the shared theme table and page() helper."""
import json, math, pathlib, subprocess, os
import viz

# ---------------------------------------------------------------- motion (Hyprland defaults, speed is deciseconds)
CURVES={"easeOutQuint":"cubic-bezier(0.23,1,0.32,1)","easeInOutCubic":"cubic-bezier(0.65,0.05,0.36,1)",
        "linear":"linear","almostLinear":"cubic-bezier(0.5,0.5,0.75,1)","quick":"cubic-bezier(0.15,0,0.1,1)"}
HYPR_ANIM=[("windows",379,"easeOutQuint",""),("windowsIn",410,"easeOutQuint","popin 87%"),("windowsOut",149,"linear","popin 87%"),
 ("fade",303,"quick",""),("fadeIn",173,"almostLinear",""),("fadeOut",146,"almostLinear",""),
 ("layersIn",400,"easeOutQuint","fade"),("layersOut",150,"linear","fade"),("border",539,"easeOutQuint",""),("specialWorkspace",300,"easeOutQuint","slidevert")]
MOTION={"enter":{"ms":400,"curve":"easeOutQuint","style":"scale 0.87→1 + fade","from":"windowsIn / layersIn"},
        "exit":{"ms":150,"curve":"linear","style":"scale 1→0.87 + fade","from":"windowsOut / layersOut"},
        "fade":{"ms":300,"curve":"quick","style":"opacity only","from":"fade"},
        "micro":{"ms":150,"curve":"almostLinear","style":"hover / focus / toggle knob","from":"fadeOut"},
        "emphasis":{"ms":540,"curve":"easeOutQuint","style":"border colour, selection sweep","from":"border"},
        "reducedMotion":"Hyprland animations disabled or prefers-reduced-motion → all durations 0, keep end state"}
FLOAT={"gapsOut":10,"gapsIn":5,"borderSize":2,"activeBorder":"theme accent (or hyprland.active-border gradient)","inactiveBorder":"rgba(595959aa)",
       "rounding":0,"opacityActive":0.985,"opacityInactive":0.96,"shadow":False,"blur":False,"titlebar":"none (compositor-owned; app draws no chrome)",
       "sizes":{"dialog":"480×auto","utility":"640×480","app":"1200×800 or 60% 70%","palette":"640×420 (menu surface)"},
       "rule":'o.window({ class = "^(your-app)$" }, { float = true, size = "1200 800", center = true })'}

def run(ROOT, THEMES, DEFAULT_THEME, page, BASE, tokens_json, css_path):
    VIZ={}
    validator=os.environ.get("OMARCHY_DS_VALIDATOR")
    for slug,t in THEMES.items():
        r=viz.derive(t); r["name"]=t["name"]
        if validator and os.path.exists(validator):
            cat=",".join(c["hex"] for c in r["categorical"])
            out=subprocess.run(["node",validator,cat,"--mode",r["mode"],"--surface",r["surface"]]+(["--ordinal"] if r["monochrome"] else []),capture_output=True,text=True)
            r["validator"]={"exit":out.returncode,"lines":[l.strip() for l in out.stdout.splitlines() if l.strip().startswith("[")]}
        VIZ[slug]=r
    (ROOT/"tokens/viz.tokens.json").write_text(json.dumps({"$schema":"omarchy-viz-tokens/1","method":"dataviz snap-to-passing over theme roles; see guides/dataviz.md","defaultTheme":DEFAULT_THEME,"themes":VIZ},indent=2))

    # ---- viz CSS
    def vcss(sel,r):
        L=[f"{sel} {{"]
        for i,c in enumerate(r["categorical"]): L.append(f"  --om-viz-cat-{i+1}: {c['hex']};")
        for i in range(len(r["categorical"]),8): L.append(f"  --om-viz-cat-{i+1}: var(--om-viz-other);")
        for i,h in enumerate(r["sequential"]): L.append(f"  --om-viz-seq-{i+1}: {h};")
        for i,h in enumerate(r["ordinal"]): L.append(f"  --om-viz-ord-{i+1}: {h};")
        d=r["diverging"]; L+= [f"  --om-viz-div-neg: {d['negative']};",f"  --om-viz-div-mid: {d['midpoint']};",f"  --om-viz-div-pos: {d['positive']};"]
        for k,v in r["status"].items(): L.append(f"  --om-viz-status-{k}: {v};")
        c=r["chrome"]; L+= [f"  --om-viz-surface: {c['surface']};",f"  --om-viz-ink: {c['ink']};",f"  --om-viz-ink-2: {c['secondary']};",f"  --om-viz-muted: {c['muted']};",
                            f"  --om-viz-grid: {c['gridline']};",f"  --om-viz-baseline: {c['baseline']};",f"  --om-viz-other: {c['other']};",f"  --om-viz-emphasis: {c['emphasisAccent']};",
                            f"  --om-viz-series-count: {len(r['categorical'])};",f"  --om-viz-monochrome: {1 if r['monochrome'] else 0};"]
        L.append("}"); return "\n".join(L)
    vizcss=["/* Omarchy Design System — data-viz tokens, DERIVED per theme by tools/viz.py (dataviz snap-to-passing). */",
            "/* Roles: --om-viz-cat-N (identity, fixed order, never cycled), --om-viz-seq-N (magnitude, one hue = accent), --om-viz-ord-N (ordered categories), --om-viz-div-* (polarity), --om-viz-status-* (state; icon+label always), chrome. */",
            vcss(":root",VIZ[DEFAULT_THEME])]+[vcss(f'[data-om-theme="{k}"]',r) for k,r in VIZ.items()]
    (ROOT/"tokens/omarchy-viz.css").write_text("\n".join(vizcss)+"\n")
    vizcss_text="\n".join(vizcss)

    # ---- extend base tokens/css with motion, float, status
    tj=json.loads((ROOT/"tokens/omarchy.tokens.json").read_text())
    tj["motion"]={"curves":CURVES,"hyprlandDefaults":[{"leaf":a,"ms":b,"curve":c,"style":d} for a,b,c,d in HYPR_ANIM],"ui":MOTION}
    tj["floatingWindow"]=FLOAT
    tj["status"]={"good":"green","warning":"yellow","serious":"orange","critical":"red (= urgent)","info":"accent","rule":"always glyph + label; never colour alone; never reused as a series colour"}
    tj["iconography"]={"font":"Nerd Font glyphs from the monospace alias","sizes":{"icon-small":11,"icon":14,"icon-large":18,"display":24,"display-large":28},"rule":"one weight, optical centring via OpticalGlyph/BarIconButton, glyph colour = text colour of its row"}
    tj["density"]={"root":"[font] base-size in ~/.config/omarchy/shell.toml (omarchy display text size)","compact":11,"default":12,"comfortable":14,"large":16,"rule":"everything scales: spacing × fontScale, bar × fontScale"}
    (ROOT/"tokens/omarchy.tokens.json").write_text(json.dumps(tj,indent=2))
    css=(ROOT/"tokens/omarchy.css").read_text()
    css+="\n:root {\n  /* motion — from Hyprland defaults (speed ×100ms) */\n"
    for k,v in CURVES.items(): css+=f"  --om-ease-{k}: {v};\n"
    for k,v in MOTION.items():
        if isinstance(v,dict): css+=f"  --om-motion-{k}: {v['ms']}ms var(--om-ease-{v['curve']});\n"
    css+="  /* floating window — Hyprland defaults */\n  --om-win-gap: 10px; --om-win-gap-in: 5px; --om-win-border: 2px; --om-win-border-inactive: rgba(89,89,89,.67); --om-win-opacity: .985; --om-win-opacity-inactive: .96;\n"
    css+="  /* status */\n  --om-status-good: var(--om-green); --om-status-warning: var(--om-yellow); --om-status-serious: var(--om-orange); --om-status-critical: var(--om-urgent); --om-status-info: var(--om-accent);\n}\n"
    css+="@media (prefers-reduced-motion: reduce) { :root { --om-motion-enter: 0s; --om-motion-exit: 0s; --om-motion-fade: 0s; --om-motion-micro: 0s; --om-motion-emphasis: 0s; } }\n"
    (ROOT/"tokens/omarchy.css").write_text(css)

    # ---- shared viz chrome + JS
    VIZ_CSS="""<style>
%s
.viz{font-family:var(--om-font);color:var(--om-viz-ink)}
.viz svg{display:block;overflow:visible}
.viz .grid{stroke:var(--om-viz-grid);stroke-width:1}
.viz .baseline{stroke:var(--om-viz-baseline);stroke-width:1}
.viz .tick{fill:var(--om-viz-muted);font-size:10px}
.viz .lbl{fill:var(--om-viz-ink-2);font-size:10px}
.viz .bar{transition:opacity var(--om-motion-micro)}
.viz .bar:hover,.viz .cell:hover{opacity:.8}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:10px;color:var(--om-viz-ink-2);margin:6px 0 0}
.legend i{display:inline-block;width:10px;height:10px;margin-right:5px;vertical-align:-1px}
.legend i.line{height:2px;vertical-align:2px}
.tip{position:fixed;pointer-events:none;background:var(--om-background);color:var(--om-foreground);border:1px solid var(--om-border-normal);padding:6px 8px;font:10px/1.5 var(--om-font);display:none;z-index:9;min-width:120px}
.tip b{font-size:12px}
.tip i{display:inline-block;width:10px;height:2px;margin-right:5px;vertical-align:3px}
.tile{border:1px solid var(--om-separator);padding:12px 14px;min-width:170px}
.tile .l{font-size:var(--om-font-caption);color:var(--om-viz-muted)}
.tile .v{font-size:24px;font-weight:600;margin:2px 0}
.tile .d{font-size:var(--om-font-caption);color:var(--om-viz-ink-2)}
.tile .d.up{color:var(--om-viz-status-good)}.tile .d.down{color:var(--om-viz-status-critical)}
table.tv{border-collapse:collapse;font-size:10px;margin-top:8px}table.tv td,table.tv th{padding:3px 10px 3px 0;text-align:right;border-bottom:1px solid var(--om-viz-grid);font-variant-numeric:tabular-nums}table.tv th{color:var(--om-viz-muted);font-weight:normal}table.tv td:first-child,table.tv th:first-child{text-align:left}
details.tv summary{font-size:10px;color:var(--om-viz-muted);cursor:pointer;margin-top:6px}
</style><div class="tip" id="tip"></div>
<script>
(function(){var tip=document.getElementById('tip');
function show(e,html){tip.innerHTML=html;tip.style.display='block';tip.style.left=(e.clientX+14)+'px';tip.style.top=(e.clientY+14)+'px'}
document.addEventListener('pointermove',function(e){var el=e.target.closest&&e.target.closest('[data-tip]');if(el){show(e,el.getAttribute('data-tip'))}else if(!e.target.closest||!e.target.closest('.xh')){tip.style.display='none'}});
document.addEventListener('focusin',function(e){var el=e.target.closest&&e.target.closest('[data-tip]');if(el){var r=el.getBoundingClientRect();show({clientX:r.right,clientY:r.top},el.getAttribute('data-tip'))}});
document.querySelectorAll('.xh').forEach(function(svg){var pts=JSON.parse(svg.getAttribute('data-x'));var series=JSON.parse(svg.getAttribute('data-series'));var line=svg.querySelector('.crosshair');
svg.addEventListener('pointermove',function(e){var r=svg.getBoundingClientRect();var vb=svg.viewBox.baseVal;var x=(e.clientX-r.left)/r.width*vb.width;var best=0;for(var i=1;i<pts.length;i++){if(Math.abs(pts[i].x-x)<Math.abs(pts[best].x-x))best=i}
line.setAttribute('x1',pts[best].x);line.setAttribute('x2',pts[best].x);line.style.display='block';var html='<b>'+pts[best].label+'</b><br>';series.forEach(function(s){html+='<i style="background:'+s.color+'"></i><b>'+s.values[best]+'</b> <span style="color:var(--om-viz-muted)">'+s.name+'</span><br>'});show(e,html)});
svg.addEventListener('pointerleave',function(){line.style.display='none';tip.style.display='none'})});
})();
</script>""" % vizcss_text

    def vpage(fname, group, title, body):
        page(fname, group, title, VIZ_CSS+'<div class="viz">'+body+'</div>')

    # ---- viz palette card
    def sw(var,label=""):
        return f'<div style="width:60px"><b style="display:block;height:34px;background:var({var});border:1px solid var(--om-separator)"></b><span style="font-size:9px;color:var(--om-viz-muted)">{label}</span></div>'
    body='<p class="om-h">Derived from the active theme — categorical order validated per theme (dataviz six checks)</p>'
    body+='<div class="om-h" style="margin-top:12px">Categorical · fixed order, never cycled · beyond <span id="sc"></span> series fold to “Other”</div><div class="row" style="gap:4px">'+"".join(sw(f"--om-viz-cat-{i}",f"cat-{i}") for i in range(1,9))+sw("--om-viz-other","other")+'</div>'
    body+='<div class="om-h" style="margin-top:16px">Sequential · one hue (accent) · magnitude</div><div class="row" style="gap:4px">'+"".join(sw(f"--om-viz-seq-{i}",f"seq-{i}") for i in range(1,8))+'</div>'
    body+='<div class="om-h" style="margin-top:16px">Ordinal · 4 steps · light end ≥ 2:1</div><div class="row" style="gap:4px">'+"".join(sw(f"--om-viz-ord-{i}",f"ord-{i}") for i in range(1,5))+'</div>'
    body+='<div class="om-h" style="margin-top:16px">Diverging · accent ↔ farthest theme hue · neutral midpoint</div><div class="row" style="gap:4px">'+sw("--om-viz-div-neg","neg")+sw("--om-viz-div-mid","mid")+sw("--om-viz-div-pos","pos")+'</div>'
    body+='<div class="om-h" style="margin-top:16px">Status · reserved meaning · glyph + label always</div><div class="row" style="gap:4px">'+"".join(sw(f"--om-viz-status-{k}",k) for k in ("good","warning","serious","critical"))+'</div>'
    body+='<div class="om-h" style="margin-top:16px">Chrome</div><div class="row" style="gap:4px">'+"".join(sw(f"--om-viz-{k}",k) for k in ("surface","ink","ink-2","muted","grid","baseline","emphasis"))+'</div>'
    body+='<script>document.getElementById("sc").textContent=getComputedStyle(document.documentElement).getPropertyValue("--om-viz-series-count").trim();document.querySelector(".themes select").addEventListener("change",function(){setTimeout(function(){document.getElementById("sc").textContent=getComputedStyle(document.documentElement).getPropertyValue("--om-viz-series-count").trim()},0)})</script>'
    rows="".join(f'<tr><td>{r["name"]}</td><td>{"ordinal" if r["monochrome"] else len(r["categorical"])}</td><td>{", ".join(r.get("dropped",[])) or "—"}</td><td>{r.get("worstAdjacentCVD","—")}</td><td>{r.get("worstAdjacentNormal","—")}</td><td>{r["contrast"]["ink/surface"]}</td></tr>' for r in VIZ.values())
    body+=f'<details class="tv" open><summary>Per-theme derivation report</summary><table class="tv"><tr><th>Theme</th><th>Series</th><th>Dropped (series cap)</th><th>Worst CVD ΔE</th><th>Worst normal ΔE</th><th>Ink:surface</th></tr>{rows}</table></details>'
    vpage("viz-palette.html","Data viz","Chart palette (derived)",body)

    # ---- stat tiles + sparkline
    spark=[30,34,31,38,42,40,47,45,52,50,58,61]
    def sparkline(vals,w=110,h=28,cls="--om-viz-cat-1"):
        mn,mx=min(vals),max(vals); pts=" ".join(f"{i*(w/(len(vals)-1)):.1f},{h-(v-mn)/(mx-mn)*h:.1f}" for i,v in enumerate(vals))
        lx,ly=pts.split(" ")[-1].split(",")
        return f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}"><polyline points="{pts}" fill="none" stroke="var(--om-viz-other)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/><circle cx="{lx}" cy="{ly}" r="4" fill="var({cls})" stroke="var(--om-viz-surface)" stroke-width="2"/></svg>'
    tiles=[("Ice sessions this week","14","+3 vs last week","up",spark),("CPU","41%","−6 pts vs 1h","up",[60,58,55,57,50,48,49,45,44,43,42,41]),("Battery","68%","2h 40m remaining","",[90,88,85,83,80,78,76,74,72,70,69,68]),("Agent spend","$12.40","+$4.10 vs yesterday","down",[4,5,6,5,7,8,8,9,10,11,12,12])]
    body='<p class="om-h">Stat tile: label · value (proportional figures) · delta (direction × whether up is good) · 12-pt sparkline, current period in the series hue</p><div class="row" style="align-items:stretch">'
    for l,v,d,cls,sp in tiles: body+=f'<div class="tile"><div class="l">{l}</div><div class="v">{v}</div><div class="d {cls}">{"󰁝 " if cls=="up" else ("󰁅 " if cls=="down" else "")}{d}</div><div style="margin-top:8px">{sparkline(sp)}</div></div>'
    body+='</div><div class="sep"></div><p class="om-h">Hero figure — one per view, ≥48px, same mono face</p><div style="font-size:48px;font-weight:600;line-height:1">4.2 <span style="font-size:14px;font-weight:400;color:var(--om-viz-muted)">ms p95 latency</span></div>'
    body+='<div class="sep"></div><p class="om-h">Meter — fill carries severity, track is a lighter step of the same ramp</p>'
    for l,p,st in (("Disk /home",62,"--om-viz-seq-5"),("Memory",81,"--om-viz-status-warning"),("Swap",94,"--om-viz-status-critical")):
        body+=f'<div style="display:flex;align-items:center;gap:10px;margin:6px 0;font-size:10px"><span style="width:90px;color:var(--om-viz-ink-2)">{l}</span><div style="flex:1;height:6px;background:var(--om-viz-seq-2)" data-tip="<b>{p}%</b> {l}"><i style="display:block;height:6px;width:{p}%;background:var({st})"></i></div><span style="width:34px;text-align:right;font-variant-numeric:tabular-nums">{p}%</span></div>'
    vpage("viz-stat-tiles.html","Data viz","Stat tiles, hero, meter",body)

    # ---- bars
    cats=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]; s1=[12,18,9,22,17,25,14]; s2=[8,6,11,7,9,10,12]
    W,H,PL,PB=520,200,36,24; ph=H-PB-10; mx=40
    def y(v): return 10+ph-(v/mx)*ph
    g="".join(f'<line class="grid" x1="{PL}" x2="{W}" y1="{y(v):.1f}" y2="{y(v):.1f}"/><text class="tick" x="{PL-6}" y="{y(v)+3:.1f}" text-anchor="end">{v}</text>' for v in (10,20,30,40))
    bw=(W-PL)/len(cats); bars=""
    for i,c in enumerate(cats):
        x=PL+i*bw+bw/2
        bars+=f'<rect class="bar" x="{x-22:.1f}" y="{y(s1[i]):.1f}" width="20" height="{ph-(y(s1[i])-10):.1f}" rx="0" fill="var(--om-viz-cat-1)" data-tip="<b>{s1[i]}</b> On-ice · {c}"/>'
        bars+=f'<rect class="bar" x="{x+2:.1f}" y="{y(s2[i]):.1f}" width="20" height="{ph-(y(s2[i])-10):.1f}" fill="var(--om-viz-cat-2)" data-tip="<b>{s2[i]}</b> Dryland · {c}"/>'
        bars+=f'<text class="tick" x="{x:.1f}" y="{H-6}" text-anchor="middle">{c}</text>'
    bars+=f'<text class="lbl" x="{PL+5*bw+bw/2-12:.1f}" y="{y(25)-5:.1f}" text-anchor="middle">25</text>'
    body=f'<p class="om-h">Grouped bars — ≤24px thick, square at baseline, 2px surface gap, one axis, selective label on the extreme</p><svg viewBox="0 0 {W} {H}" width="{W}" height="{H}">{g}<line class="baseline" x1="{PL}" x2="{W}" y1="{y(0):.1f}" y2="{y(0):.1f}"/>{bars}</svg>'
    body+='<div class="legend"><span><i style="background:var(--om-viz-cat-1)"></i>On-ice</span><span><i style="background:var(--om-viz-cat-2)"></i>Dryland</span></div>'
    # stacked horizontal + emphasis
    parts=[("Claude",46),("Codex",28),("Gemini",14),("Other",12)]
    body+='<div class="sep"></div><p class="om-h">Part-to-whole — horizontal stacked bar, tail folded into “Other” (de-emphasis)</p><svg viewBox="0 0 520 34" width="520" height="34">'
    x=0
    for i,(n,p) in enumerate(parts):
        col=f"var(--om-viz-cat-{i+1})" if n!="Other" else "var(--om-viz-other)"
        body+=f'<rect class="bar" x="{x*5.2:.1f}" y="4" width="{p*5.2-2:.1f}" height="18" fill="{col}" data-tip="<b>{p}%</b> {n}"/>'
        if p>=14: body+=f'<text x="{(x+p/2)*5.2:.1f}" y="16" text-anchor="middle" font-size="10" fill="var(--om-viz-surface)">{p}%</text>'
        x+=p
    body+='</svg><div class="legend">'+"".join(f'<span><i style="background:{"var(--om-viz-cat-%d)"%(i+1) if n!="Other" else "var(--om-viz-other)"}"></i>{n}</span>' for i,(n,p) in enumerate(parts))+'</div>'
    emp=[("Kirkland",31),("Lynnwood",22),("Everett",19),("Renton",17),("Bellevue",12)]
    body+='<div class="sep"></div><p class="om-h">Emphasis — the one that matters in the accent, the rest in “other”</p><svg viewBox="0 0 520 136" width="520" height="136">'
    for i,(n,v) in enumerate(emp):
        col="var(--om-viz-emphasis)" if n=="Everett" else "var(--om-viz-other)"
        body+=f'<text class="lbl" x="70" y="{i*26+16}" text-anchor="end">{n}</text><rect class="bar" x="80" y="{i*26+5}" width="{v*12}" height="16" fill="{col}" data-tip="<b>{v}</b> sessions · {n}"/>'
        if n=="Everett": body+=f'<text class="lbl" x="{86+v*12}" y="{i*26+17}">{v}</text>'
    body+='</svg><details class="tv"><summary>Table view</summary><table class="tv"><tr><th>Rink</th><th>Sessions</th></tr>'+"".join(f'<tr><td>{n}</td><td>{v}</td></tr>' for n,v in emp)+'</table></details>'
    vpage("viz-bars.html","Data viz","Bars: grouped, stacked, emphasis",body)

    # ---- lines
    months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug"]; a=[12,14,13,17,19,18,22,24]; b=[9,10,12,11,14,13,15,16]; c=[6,7,7,8,8,10,9,11]
    W,H,PL,PB=520,200,36,24; ph=H-PB-10; mx=30
    def yy(v): return 10+ph-(v/mx)*ph
    xs=[PL+i*(W-PL-10)/(len(months)-1) for i in range(len(months))]
    def poly(vals): return " ".join(f"{xs[i]:.1f},{yy(v):.1f}" for i,v in enumerate(vals))
    g="".join(f'<line class="grid" x1="{PL}" x2="{W}" y1="{yy(v):.1f}" y2="{yy(v):.1f}"/><text class="tick" x="{PL-6}" y="{yy(v)+3:.1f}" text-anchor="end">{v}</text>' for v in (10,20,30))
    ticks="".join(f'<text class="tick" x="{xs[i]:.1f}" y="{H-6}" text-anchor="middle">{m}</text>' for i,m in enumerate(months))
    lines=""
    for k,(vals,nm) in enumerate(((a,"Sessions"),(b,"Users"),(c,"Repeat"))):
        lines+=f'<polygon points="{poly(vals)} {xs[-1]:.1f},{yy(0):.1f} {xs[0]:.1f},{yy(0):.1f}" fill="var(--om-viz-cat-{k+1})" opacity=".08"/>' if k==0 else ""
        lines+=f'<polyline points="{poly(vals)}" fill="none" stroke="var(--om-viz-cat-{k+1})" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/><circle cx="{xs[-1]:.1f}" cy="{yy(vals[-1]):.1f}" r="4" fill="var(--om-viz-cat-{k+1})" stroke="var(--om-viz-surface)" stroke-width="2"/><text class="lbl" x="{xs[-1]+8:.1f}" y="{yy(vals[-1])+3:.1f}">{nm} {vals[-1]}</text>'
    pts=json.dumps([{"x":round(xs[i],1),"label":m} for i,m in enumerate(months)])
    series=json.dumps([{"name":"Sessions","color":"var(--om-viz-cat-1)","values":a},{"name":"Users","color":"var(--om-viz-cat-2)","values":b},{"name":"Repeat","color":"var(--om-viz-cat-3)","values":c}])
    body=f'<p class="om-h">Multi-series line — 2px, end-dots with surface ring, direct end-labels, crosshair tooltip lists every series</p><svg class="xh" viewBox="0 0 {W+70} {H}" width="{W+70}" height="{H}" data-x=\'{pts}\' data-series=\'{series}\'>{g}<line class="baseline" x1="{PL}" x2="{W}" y1="{yy(0):.1f}" y2="{yy(0):.1f}"/>{ticks}{lines}<line class="crosshair" x1="0" x2="0" y1="10" y2="{10+ph}" stroke="var(--om-viz-muted)" stroke-width="1" style="display:none"/></svg>'
    body+='<div class="legend"><span><i class="line" style="background:var(--om-viz-cat-1)"></i>Sessions</span><span><i class="line" style="background:var(--om-viz-cat-2)"></i>Users</span><span><i class="line" style="background:var(--om-viz-cat-3)"></i>Repeat</span></div>'
    body+='<div class="sep"></div><p class="om-h">Diverging vs baseline — polarity: positive pole = accent side, negative = farthest hue, neutral midpoint</p><svg viewBox="0 0 520 110" width="520" height="110">'
    dv=[("Q1",-8),("Q2",5),("Q3",12),("Q4",-3),("Q5",9),("Q6",-11)]
    for i,(n,v) in enumerate(dv):
        x=40+i*80; col="var(--om-viz-div-pos)" if v>0 else "var(--om-viz-div-neg)"; h=abs(v)*3.2
        yb=55-h if v>0 else 55
        body+=f'<rect class="bar" x="{x}" y="{yb:.1f}" width="20" height="{h:.1f}" fill="{col}" data-tip="<b>{v:+d}</b> {n}"/><text class="tick" x="{x+10}" y="104" text-anchor="middle">{n}</text>'
    body+='<line class="baseline" x1="30" x2="520" y1="55" y2="55"/></svg>'
    vpage("viz-lines.html","Data viz","Lines, area, diverging",body)

    # ---- heatmap
    import random
    random.seed(7)
    days=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]; hours=[f"{h:02d}" for h in range(6,24,2)]
    body='<p class="om-h">Heatmap — sequential one-hue ramp, 2px surface gaps, scale legend, values in tooltip + table</p><svg viewBox="0 0 520 190" width="520" height="190">'
    data=[[random.randint(0,6) for _ in hours] for _ in days]
    for r,d in enumerate(days):
        body+=f'<text class="tick" x="30" y="{r*22+26}" text-anchor="end">{d}</text>'
        for c,hh in enumerate(hours):
            v=data[r][c]; step=1+round(v/6*6)
            body+=f'<rect class="cell" x="{38+c*52}" y="{r*22+12}" width="50" height="20" fill="var(--om-viz-seq-{step})" data-tip="<b>{v}</b> sessions · {d} {hh}:00"/>'
    for c,hh in enumerate(hours): body+=f'<text class="tick" x="{38+c*52+25}" y="184" text-anchor="middle">{hh}</text>'
    body+='</svg><div class="legend" style="align-items:center"><span>0</span>'+"".join(f'<i style="background:var(--om-viz-seq-{i});margin:0"></i>' for i in range(1,8))+'<span>6+</span><span style="color:var(--om-viz-muted)">sessions / 2h</span></div>'
    body+='<div class="sep"></div><p class="om-h">Ordinal (ordered categories) — one hue, monotone lightness</p><svg viewBox="0 0 520 44" width="520" height="44">'
    for i,(n,p) in enumerate((("Mite",34),("Squirt",28),("Peewee",22),("Bantam",16))):
        body+=f'<rect class="bar" x="{i*130}" y="4" width="{p*3.6}" height="18" fill="var(--om-viz-ord-{i+1})" data-tip="<b>{p}</b> {n}"/><text class="lbl" x="{i*130}" y="40">{n}</text>'
    body+='</svg>'
    vpage("viz-heatmap.html","Data viz","Heatmap & ordinal",body)

    # ================================================================ floating app
    WIN_CSS="""<style>
.desk{background:var(--om-darker-background);padding:var(--om-win-gap);position:relative}
.win{background:var(--om-background);border:var(--om-win-border) solid var(--om-accent);opacity:var(--om-win-opacity);display:flex;flex-direction:column;min-height:280px;font-size:var(--om-font-body)}
.win.inactive{border-color:var(--om-win-border-inactive);opacity:var(--om-win-opacity-inactive)}
.tb{display:flex;align-items:center;gap:var(--om-space-control-gap);padding:var(--om-space-md) var(--om-space-xl);border-bottom:1px solid var(--om-separator);height:36px}
.tb .sp{flex:1}
.tabs{display:flex;gap:0}.tab{padding:0 var(--om-space-control-padding-x);height:28px;display:flex;align-items:center;color:var(--om-text-dim);border-bottom:2px solid transparent}.tab.on{color:var(--om-foreground);border-bottom-color:var(--om-accent)}
.side{width:200px;border-right:1px solid var(--om-separator);padding:var(--om-space-lg)}
.side .cursor-row{height:26px;padding:0 8px}
.main{flex:1;padding:var(--om-space-panel-padding)}
.insp{width:220px;border-left:1px solid var(--om-separator);padding:var(--om-space-lg)}
.sb{display:flex;gap:16px;padding:var(--om-space-xs) var(--om-space-xl);border-top:1px solid var(--om-separator);font-size:var(--om-font-caption);color:var(--om-text-dim);height:22px;align-items:center}
kbd{font:inherit;font-size:10px;padding:1px 5px;border:1px solid var(--om-border-normal);background:var(--om-fill-normal);color:var(--om-foreground)}
.badge{display:inline-flex;align-items:center;gap:4px;font-size:10px;padding:1px 6px;border:1px solid var(--om-border-normal);background:var(--om-fill-normal)}
.badge.accent{border-color:var(--om-accent);color:var(--om-accent)}
.badge.urgent{border-color:var(--om-urgent);color:var(--om-urgent)}
.chip{display:inline-flex;align-items:center;gap:6px;height:22px;padding:0 8px;border:1px solid var(--om-border-normal);background:var(--om-fill-normal);font-size:10px}
.chip.on{background:var(--om-fill-selected);border-color:var(--om-border-selected)}
.scrim{position:absolute;inset:0;background:color-mix(in srgb,var(--om-background) 50%,transparent);display:flex;align-items:center;justify-content:center}
.dlg{background:var(--om-background);border:2px solid var(--om-accent);width:420px;padding:var(--om-space-panel-padding)}
.prog{height:4px;background:var(--om-fill-selected)}.prog i{display:block;height:4px;background:var(--om-foreground)}
.skel{background:var(--om-fill-normal);height:12px;margin:6px 0;animation:sk 1.2s var(--om-ease-almostLinear) infinite alternate}@keyframes sk{to{opacity:.4}}
.toast{display:flex;gap:10px;align-items:center;background:var(--om-background);border:2px solid var(--om-accent);padding:7px 12px;width:380px}
</style>"""
    def apage(fname,group,title,body): page(fname,group,title,WIN_CSS+body)

    apage("app-window.html","Floating app","Floating window anatomy",
     '<p class="om-h">A floating Omarchy window owns no chrome — the compositor draws the 2px border (accent when active), gaps 10, rounding 0, opacity .985/.96, no shadow, no blur. The app starts at its content.</p>'
     '<div class="desk" style="display:flex;gap:var(--om-win-gap)"><div class="win" style="flex:1"><div class="tb"><b>Ice Availability</b><span class="badge accent">live</span><span class="sp"></span><span class="btn" style="height:24px">󰑐</span><span class="btn" style="height:24px">󰒓</span></div>'
     '<div style="display:flex;flex:1"><div class="side"><div class="om-h">Rinks</div><div class="cursor-row current">Kirkland</div><div class="cursor-row cur">Lynnwood</div><div class="cursor-row">Everett</div></div><div class="main"><div class="om-h">Today</div><div class="cursor-row"><span>06:00 Stick &amp; Puck</span><span class="badge">12 open</span></div><div class="cursor-row"><span>07:30 Freestyle</span><span class="badge urgent">full</span></div><div class="cursor-row"><span>12:00 Public</span><span class="badge">40 open</span></div></div></div>'
     '<div class="sb"><span>3 rinks</span><span>updated 2m ago</span><span class="sp" style="flex:1"></span><span><kbd>j</kbd><kbd>k</kbd> move · <kbd>⏎</kbd> open · <kbd>?</kbd> help</span></div></div>'
     '<div class="win inactive" style="width:260px"><div class="tb"><b>Inspector</b></div><div class="main" style="color:var(--om-text-dim)">Inactive window: border rgba(59,59,59,.67), opacity .96</div></div></div>'
     '<p style="color:var(--om-text-dim);font-size:var(--om-font-caption);margin-top:14px">Float it with a Hyprland rule in <code>~/.config/hypr/windows.lua</code>: <code>o.window({ class = "^(your-app)$" }, { float = true, size = "1200 800", center = true })</code>. Never draw a title bar, close button, or drop shadow; Hyprland already owns move/resize/close (Super+drag, Super+W).</p>')

    apage("app-shell.html","Floating app","App shell layout",
     '<p class="om-h">Three-column shell: nav (200) · content (flex) · inspector (220, optional). Toolbar 36, status bar 22. All rows are CursorSurfaces — j/k everywhere.</p>'
     '<div class="desk"><div class="win" style="min-height:360px"><div class="tb"><div class="tabs"><span class="tab on">Sessions</span><span class="tab">Rinks</span><span class="tab">Alerts</span></div><span class="sp"></span><input class="field" style="height:26px;min-width:200px" placeholder="Search  /"><span class="btn bordered" style="height:26px">󰐕 New</span></div>'
     '<div style="display:flex;flex:1"><div class="side"><div class="om-h">Filters</div><div class="cursor-row current">All</div><div class="cursor-row">Open only</div><div class="cursor-row">Weekend</div><div class="sep"></div><div class="om-h">Saved</div><div class="cursor-row cur">Morning skate</div></div>'
     '<div class="main"><div class="om-h">Sessions · 12</div>'+"".join(f'<div class="cursor-row{" cur" if i==1 else ""}"><span>{t}</span><span style="color:var(--om-text-dim)">{r}</span></div>' for i,(t,r) in enumerate((("Sat 06:00 · Stick &amp; Puck","Kirkland"),("Sat 07:30 · Freestyle","Lynnwood"),("Sat 12:00 · Public","Everett"),("Sun 06:15 · Adult drop-in","Kirkland"))))+'</div>'
     '<div class="insp"><div class="om-h">Details</div><div style="font-size:var(--om-font-subtitle)">Sat 07:30 · Freestyle</div><div style="color:var(--om-text-dim);font-size:var(--om-font-caption);margin:4px 0 10px">Lynnwood · 60 min · 8 open</div><div class="row" style="gap:6px"><span class="btn bordered" style="height:24px">Book</span><span class="btn" style="height:24px">Remind</span></div></div></div>'
     '<div class="sb"><span>12 sessions</span><span style="flex:1"></span><span>Lake Sunset · 12px</span></div></div></div>')

    apage("command-palette.html","Floating app","Command palette",
     '<p class="om-h">The menu surface ([menu] roles): scrim .5, card border = active-border-foreground, selected row = fg@.08 + accent text. Same shape as omarchy-menu, so it feels native.</p>'
     '<div class="desk" style="min-height:360px"><div class="scrim"><div class="dlg" style="width:560px;padding:0;border-color:var(--om-foreground)"><div style="display:flex;align-items:center;gap:8px;padding:10px 14px;border-bottom:1px solid var(--om-separator)"><span></span><input class="field" style="border:0;background:transparent;flex:1;padding:0;height:22px" value="book"></div>'
     '<div style="padding:6px 0">'+"".join(f'<div class="cursor-row{" cur" if i==0 else ""}" style="height:28px;{"color:var(--om-accent)" if i==0 else ""}"><span>{g}  {t}</span><span style="color:var(--om-text-dim);font-size:10px">{k}</span></div>' for i,(g,t,k) in enumerate(((" ","Book Sat 07:30 Freestyle","⏎"),("󰃭","Book next open session","⇧⏎"),("󰂚","Remind me 30 min before","r"),("󰇚","Export week to calendar","e"))))+'</div>'
     '<div class="sb" style="border-top:1px solid var(--om-separator)"><span><kbd>↑↓</kbd> navigate</span><span><kbd>⏎</kbd> run</span><span><kbd>esc</kbd> close</span></div></div></div></div>')

    apage("app-dialogs.html","Floating app","Dialogs & confirm",
     '<p class="om-h">ConfirmDialog contract: message · Cancel (default focus) · Confirm; destructive confirm in urgent. Scrim = background@.7. j/k or h/l between buttons, Esc cancels.</p>'
     '<div class="desk" style="min-height:300px"><div class="scrim" style="background:color-mix(in srgb,var(--om-background) 70%,transparent)"><div class="dlg"><div style="font-size:var(--om-font-title);margin-bottom:6px">Forget “Home Wi-Fi”?</div><div style="color:var(--om-text-body);font-size:var(--om-font-body-small)">You will need the passphrase to reconnect.</div><div class="row" style="justify-content:flex-end;margin-top:18px;gap:6px"><span class="btn bordered hover">Cancel</span><span class="btn bordered" style="color:var(--om-urgent)">Forget</span></div></div></div></div>'
     '<div class="sep"></div><p class="om-h">Form dialog — single column, labels above, 30px fields, primary action bordered</p><div class="desk" style="min-height:300px"><div class="scrim"><div class="dlg"><div style="font-size:var(--om-font-title);margin-bottom:12px">Add rink</div><div class="label">Name</div><input class="field" style="width:100%" value="Sno-King Kirkland"><div class="label" style="margin-top:10px">Timezone</div><div class="field" style="display:flex;justify-content:space-between;align-items:center;width:100%"><span>America/Los_Angeles</span><span>󰅀</span></div><div class="row" style="margin-top:12px"><div class="sw on sq" style="transform:scale(.7);transform-origin:left"><i></i></div><span style="font-size:var(--om-font-caption);color:var(--om-text-dim)">Notify on new sessions</span></div><div class="row" style="justify-content:flex-end;margin-top:18px;gap:6px"><span class="btn">Cancel</span><span class="btn bordered selected">Save</span></div></div></div></div>')

    apage("app-states.html","Floating app","Empty, loading, error",
     '<p class="om-h">Empty — glyph at display size, one sentence, one action</p><div class="desk"><div class="win" style="align-items:center;justify-content:center;min-height:200px"><div style="font-size:var(--om-font-display-large);color:var(--om-text-dim)">󰃭</div><div style="margin:6px 0 12px;color:var(--om-text-body)">No sessions match these filters.</div><span class="btn bordered">Clear filters</span></div></div>'
     '<div class="sep"></div><p class="om-h">Loading — keep stale data at reduced opacity; skeleton only on first load; spinner glyph inline</p><div class="desk"><div class="win" style="min-height:160px"><div class="tb"><b>Sessions</b><span style="color:var(--om-text-dim)">󰑐 refreshing…</span></div><div class="main" style="opacity:.6"><div class="cursor-row"><span>Sat 06:00 · Stick &amp; Puck</span><span>Kirkland</span></div><div class="cursor-row"><span>Sat 07:30 · Freestyle</span><span>Lynnwood</span></div></div></div></div>'
     '<div class="desk" style="margin-top:8px"><div class="win" style="min-height:120px"><div class="main"><div class="skel" style="width:60%"></div><div class="skel" style="width:80%"></div><div class="skel" style="width:45%"></div></div></div></div>'
     '<div class="sep"></div><p class="om-h">Error — inline, urgent glyph + text, retry action; never a blank panel</p><div class="desk"><div class="win" style="min-height:120px"><div class="main"><div class="cursor-row" style="border:1px solid var(--om-urgent);height:auto;padding:8px 12px"><span><span style="color:var(--om-urgent)">󰀦</span>  Could not reach rink API (timeout)</span><span class="btn" style="height:22px">Retry</span></div><div class="cursor-row" style="opacity:.6"><span>Sat 06:00 · Stick &amp; Puck</span><span>stale · 14m</span></div></div></div></div>')

    apage("app-table.html","Floating app","Table & list",
     '<p class="om-h">Table — header caption in muted, tabular numbers right-aligned, hairline rows, sortable header carries a glyph, cursor row = hover fill</p>'
     '<div class="desk"><div class="win" style="min-height:0"><table style="border-collapse:collapse;width:100%;font-size:var(--om-font-body)"><tr style="font-size:var(--om-font-caption);color:var(--om-text-dim);text-transform:uppercase;letter-spacing:1px"><th style="text-align:left;padding:8px 12px;font-weight:normal">Session</th><th style="text-align:left;padding:8px 12px;font-weight:normal">Rink</th><th style="text-align:right;padding:8px 12px;font-weight:normal">Open 󰁅</th><th style="text-align:right;padding:8px 12px;font-weight:normal">Price</th><th style="padding:8px 12px"></th></tr>'
     +"".join(f'<tr style="border-top:1px solid var(--om-separator);{"background:var(--om-fill-hover)" if i==1 else ""}"><td style="padding:6px 12px">{s}</td><td style="padding:6px 12px;color:var(--om-text-body)">{r}</td><td style="padding:6px 12px;text-align:right;font-variant-numeric:tabular-nums">{o}</td><td style="padding:6px 12px;text-align:right;font-variant-numeric:tabular-nums">${p}</td><td style="padding:6px 12px;text-align:right"><span class="btn" style="height:22px;padding:0 4px">󰐕</span></td></tr>' for i,(s,r,o,p) in enumerate((("Sat 06:00 Stick &amp; Puck","Kirkland",12,"18"),("Sat 07:30 Freestyle","Lynnwood",8,"25"),("Sat 12:00 Public","Everett",40,"12"),("Sun 06:15 Adult drop-in","Kirkland",3,"20"))))+'</table></div></div>'
     '<div class="sep"></div><p class="om-h">Badges, chips, kbd — chrome-only colours; accent = highlighted, urgent = attention</p><div class="row"><span class="badge">default</span><span class="badge accent">accent</span><span class="badge urgent">󰀦 urgent</span><span class="chip on">󰄬 Weekend</span><span class="chip">Morning</span><span class="chip">Adult</span><span><kbd>Super</kbd> + <kbd>Space</kbd></span></div>')

    # ================================================================ evolution cards
    body='<p class="om-h">Motion tokens — lifted from Hyprland’s default animation table (speed × 100 ms). UI motion mirrors window motion so apps feel like the compositor.</p><table class="tv" style="font-size:11px;text-align:left"><tr><th style="text-align:left">Token</th><th style="text-align:left">Duration</th><th style="text-align:left">Curve</th><th style="text-align:left">Style</th><th style="text-align:left">From Hyprland</th></tr>'
    for k,v in MOTION.items():
        if isinstance(v,dict): body+=f'<tr><td style="text-align:left">{k}</td><td style="text-align:left">{v["ms"]} ms</td><td style="text-align:left">{v["curve"]}</td><td style="text-align:left">{v["style"]}</td><td style="text-align:left;color:var(--om-text-dim)">{v["from"]}</td></tr>'
    body+='</table><p class="om-h" style="margin-top:16px">Curves (hover to play)</p><div class="row">'
    for k,v in CURVES.items():
        body+=f'<div style="width:150px"><div style="font-size:10px;color:var(--om-text-dim);margin-bottom:4px">{k}</div><div style="height:22px;border:1px solid var(--om-separator);position:relative;overflow:hidden" onmouseenter="this.firstElementChild.style.transform=\'translateX(118px)\'" onmouseleave="this.firstElementChild.style.transform=\'\'"><i style="display:block;position:absolute;left:4px;top:4px;width:14px;height:14px;background:var(--om-accent);transition:transform 540ms {v}"></i></div></div>'
    body+='</div><p class="om-h" style="margin-top:16px">Enter / exit demo — popin 87% + fade, 400 ms in, 150 ms out</p><div class="row"><span class="btn bordered" onclick="var d=this.nextElementSibling;d.style.display=\'block\';d.style.opacity=0;d.style.transform=\'scale(.87)\';requestAnimationFrame(function(){d.style.transition=\'opacity var(--om-motion-enter),transform var(--om-motion-enter)\';d.style.opacity=1;d.style.transform=\'scale(1)\'})">Open</span><div class="card" style="display:none;width:220px;padding:10px" onclick="var d=this;d.style.transition=\'opacity var(--om-motion-exit),transform var(--om-motion-exit)\';d.style.opacity=0;d.style.transform=\'scale(.87)\';setTimeout(function(){d.style.display=\'none\'},160)">Popup (click to close)</div></div>'
    body+='<p style="color:var(--om-text-dim);font-size:var(--om-font-caption);margin-top:16px">Respect <code>prefers-reduced-motion</code> and Hyprland <code>animations.enabled = false</code>: durations → 0, end state kept. QML: <code>Behavior on opacity { NumberAnimation { duration: 300; easing.bezierCurve: [0.15,0,0.1,1,1,1] } }</code>.</p>'
    page("motion.html","Foundations","Motion",body)

    glyphs=[("󰖙","weather"),("󰤨","wifi"),("󰂯","bluetooth"),("󰕾","audio"),("󰍬","mic"),("󰁹","battery"),("󰃭","calendar"),("󰂚","bell"),("󰒓","settings"),("󰑐","refresh"),("󰐕","add"),("󰆴","delete"),("󰀦","warning"),("󰄬","check"),("󰅖","close"),("󰍉","search"),("󰇚","download"),("󰌆","key"),("󰆍","terminal"),("󰊢","git"),("󰚰","update"),("󰌌","keyboard"),("󰍹","monitor"),("󰒲","sleep")]
    body='<p class="om-h">Nerd Font glyphs only — same family as text, so icons inherit weight, colour, and the font the user picked. Sizes: icon-small 11 · icon 14 · icon-large 18 · display 24 · display-large 28.</p><div class="row" style="gap:6px">'
    for g,n in glyphs: body+=f'<div style="width:72px;text-align:center;padding:8px 0;border:1px solid var(--om-separator)"><div style="font-size:18px">{g}</div><div style="font-size:9px;color:var(--om-text-dim)">{n}</div></div>'
    body+='</div><div class="sep"></div><p class="om-h">Scale</p><div class="row" style="align-items:baseline;gap:18px">'+"".join(f'<span style="font-size:{s}px">󰖙<small style="font-size:9px;color:var(--om-text-dim)"> {n} {s}</small></span>' for n,s in (("icon-small",11),("icon",14),("icon-large",18),("display",24),("display-large",28)))+'</div>'
    body+='<p style="color:var(--om-text-dim);font-size:var(--om-font-caption);margin-top:16px">Rules: glyph colour = the text colour of its row (urgent only for attention). Optical centring via <code>OpticalGlyph</code> / <code>BarIconButton</code>. No SVG icon sets, no emoji in chrome, no filled/outlined mixing — Nerd Font has one weight.</p>'
    page("iconography.html","Foundations","Iconography",body)

    body='<p class="om-h">Density is one number — [font] base-size — and everything follows (spacing × fontScale, bar × fontScale). Preview at four roots:</p><div class="row" style="align-items:flex-start">'
    for n,s in (("compact",11),("default",12),("comfortable",14),("large",16)):
        sc=s/12
        body+=f'<div style="--om-font-base:{s}px;--om-space-control-height:{round(28*sc)}px;--om-space-control-padding-x:{round(10*sc)}px;--om-space-row-padding-x:{round(12*sc)}px;--om-space-panel-padding:{round(18*sc)}px;font-size:var(--om-font-body)"><div class="om-h">{n} · {s}px</div><div class="card" style="width:{round(230*sc)}px"><div style="font-size:var(--om-font-title)">Wi-Fi</div><div class="cursor-row cur" style="height:var(--om-space-control-height)"><span>Home</span><span style="font-size:var(--om-font-caption);color:var(--om-text-dim)">-52</span></div><div class="cursor-row" style="height:var(--om-space-control-height)"><span>Cafe</span><span style="font-size:var(--om-font-caption);color:var(--om-text-dim)">-70</span></div><div class="row" style="margin-top:8px"><span class="btn bordered" style="height:var(--om-space-control-height)">Scan</span></div></div></div>'
    body+='</div><p style="color:var(--om-text-dim);font-size:var(--om-font-caption);margin-top:16px">Set with <code>omarchy display text size</code> (writes ~/.config/omarchy/shell.toml). Apps: read the same file, or map base-size → your rem root.</p>'
    page("density.html","Foundations","Density",body)

    body='<p class="om-h">Feedback — toast (= notification card), progress (foreground on selected fill), inline status with glyph + label</p>'
    body+='<div class="toast"><span style="font-size:var(--om-font-display)">󰄬</span><div><div style="font-size:var(--om-font-subtitle);font-weight:600">Booked</div><div style="font-size:var(--om-font-body-small);color:var(--om-text-body)">Sat 07:30 Freestyle · Lynnwood</div></div></div>'
    body+='<div style="height:10px"></div><div class="toast" style="border-color:var(--om-urgent)"><span style="color:var(--om-urgent)">󰀦</span><div>Booking failed — card declined</div></div>'
    body+='<div class="sep"></div><p class="om-h">Progress — determinate, indeterminate (sweep), stepped</p><div style="width:380px"><div class="prog"><i style="width:62%"></i></div><div style="font-size:10px;color:var(--om-text-dim);margin:4px 0 12px">Syncing 62%</div><div class="prog" style="position:relative;overflow:hidden"><i style="width:30%;position:absolute;animation:sw 1.2s var(--om-ease-easeInOutCubic) infinite"></i></div><style>@keyframes sw{from{left:-30%}to{left:100%}}</style><div style="font-size:10px;color:var(--om-text-dim);margin:4px 0 12px">Connecting…</div><div class="row" style="gap:4px">'+"".join(f'<div style="flex:1;height:4px;background:{"var(--om-foreground)" if i<3 else "var(--om-fill-selected)"}"></div>' for i in range(5))+'</div><div style="font-size:10px;color:var(--om-text-dim);margin-top:4px">Step 3 of 5</div></div>'
    body+='<div class="sep"></div><p class="om-h">Status — colour never alone</p><div class="row" style="gap:18px;font-size:11px"><span><span style="color:var(--om-status-good)">󰄬</span> good · connected</span><span><span style="color:var(--om-status-warning)">󰀦</span> warning · weak signal</span><span><span style="color:var(--om-status-serious)">󰀦</span> serious · 5% battery</span><span><span style="color:var(--om-status-critical)">󰅖</span> critical · unreachable</span><span><span style="color:var(--om-status-info)">󰋼</span> info · update available</span></div>'
    apage("feedback.html","Components","Feedback & status",body)

    # a11y contrast matrix
    rows=""
    def cell(v):
        col="var(--om-status-good)" if v>=4.5 else ("var(--om-status-warning)" if v>=3 else "var(--om-urgent)")
        return f'<td style="text-align:right;font-variant-numeric:tabular-nums"><span style="color:{col}">●</span> {v:.2f}</td>'
    for slug,t in THEMES.items():
        bg,fg,ac,ur=t["background"],t["foreground"],t["accent"],t["red"]
        dim=viz.mix(fg,bg,0.3)
        rows+=f'<tr><td><i style="display:inline-block;width:10px;height:10px;background:{bg};border:1px solid {fg};margin-right:6px;vertical-align:-1px"></i>{t["name"]}</td><td>{t["mode"]}</td>{cell(viz.contrast(fg,bg))}{cell(viz.contrast(dim,bg))}{cell(viz.contrast(ac,bg))}{cell(viz.contrast(ur,bg))}{cell(viz.contrast(ac,fg))}</tr>'
    body=f'<p class="om-h">WCAG contrast per theme — the numbers behind “test on light themes”. ● ≥4.5 text · ● ≥3 large/UI · ● below 3 (needs a label, a border, or a different role)</p><table class="tv" style="font-size:11px"><tr><th>Theme</th><th>Mode</th><th>fg / bg</th><th>dim / bg</th><th>accent / bg</th><th>urgent / bg</th><th>accent / fg</th></tr>{rows}</table>'
    body+='<p style="color:var(--om-text-dim);font-size:var(--om-font-caption);margin-top:16px">Read: accent-on-background is fine for borders and glyphs but not always for body text (Kanagawa, Solitude, Vantablack accents are near-ink). Urgent on Hackerman and Lumon is a *green/blue* — never rely on “red means danger”; pair the glyph. Dim text (fg mixed 30% toward bg) is the floor for secondary copy.</p>'
    page("a11y-contrast.html","Foundations","Contrast matrix",body)
    return VIZ
