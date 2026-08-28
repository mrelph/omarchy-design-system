"""Derive a validated data-viz palette from an Omarchy theme's colors.toml.

Method: the dataviz "snap-to-passing" procedure, made theme-generic.
  * Categorical: theme hues, hue angle preserved; OKLCH L moved into the mode
    band, chroma raised to the floor; near-duplicate hues dropped; slot ORDER
    chosen by enumerating permutations and maximising the worst adjacent CVD
    distance (Machado 2009 protan/deutan, OKLab dE x100). If the best order
    still fails a floor, the weaker member of the worst pair is dropped (the
    series cap) until it passes or three slots remain; three failing slots
    fall back to monochrome.
  * Monochrome themes (fewer than 3 chromatic hues): an ordinal ramp on the
    accent (or ink), plus texture + direct labels as the identity channel.
  * Sequential: one hue (accent), L walks from near-surface to accent to ink.
  * Ordinal: same hue, 4 steps, light end >= 2:1 on the surface, dL >= 0.07.
  * Diverging: accent vs the categorical hue farthest from it in hue angle,
    neutral midpoint mixed from surface and ink.
  * Status: green/yellow/orange/red snapped for contrast; icon + label always.

Confirm with the reference validator (dataviz skill):
  node validate_palette.js "<hex,...>" --mode dark --surface <background>
"""
import itertools, math

BAND = {"light": (0.43, 0.77), "dark": (0.48, 0.67)}
CHROMA_TARGET = 0.125          # validator floor is 0.10; keep a margin
MACHADO = {
 "protan": [[0.152286,1.052583,-0.204868],[0.114503,0.786281,0.099216],[-0.003882,-0.048116,1.051998]],
 "deutan": [[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]],
}

def hex2rgb(h):
    h=h.lstrip("#"); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def rgb2hex(c):
    return "#%02x%02x%02x" % tuple(max(0,min(255,round(v*255))) for v in c)
def lin(v): return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4
def unlin(v):
    v=max(0,min(1,v)); return 12.92*v if v<=0.0031308 else 1.055*v**(1/2.4)-0.055
def rgb2oklab(c):
    r,g,b=(lin(x) for x in c)
    l=0.4122214708*r+0.5363325363*g+0.0514459929*b
    m=0.2119034982*r+0.6806995451*g+0.1073969566*b
    s=0.0883024619*r+0.2817188376*g+0.6299787005*b
    l,m,s=(x**(1/3) if x>0 else -((-x)**(1/3)) for x in (l,m,s))
    return (0.2104542553*l+0.7936177850*m-0.0040720468*s,
            1.9779984951*l-2.4285922050*m+0.4505937099*s,
            0.0259040371*l+0.7827717662*m-0.8086757660*s)
def oklab2rgb(lab):
    L,a,b=lab
    l=(L+0.3963377774*a+0.2158037573*b)**3
    m=(L-0.1055613458*a-0.0638541728*b)**3
    s=(L-0.0894841775*a-1.2914855480*b)**3
    return (4.0767416621*l-3.3077115913*m+0.2309699292*s,
            -1.2684380046*l+2.6097574011*m-0.3413193965*s,
            -0.0041960863*l-0.7034186147*m+1.7076147010*s)
def in_gamut(lr): return all(-0.002<=v<=1.002 for v in lr)
def lab2lch(lab):
    L,a,b=lab; return (L,math.hypot(a,b),math.degrees(math.atan2(b,a))%360)
def lch2lab(lch):
    L,C,h=lch; r=math.radians(h); return (L,C*math.cos(r),C*math.sin(r))
def fits(lch): return in_gamut(oklab2rgb(lch2lab(lch)))
def lch2hex(lch):
    L,C,h=lch
    if C<0.012:  # exact neutral (achromatic themes stay achromatic; the validator's
        g=unlin(oklab2rgb((L,0,0))[0]); return rgb2hex((g,g,g))  # single-hue check is undefined here)
    while C>0 and not fits((L,C,h)): C-=0.004
    return rgb2hex(tuple(unlin(v) for v in oklab2rgb(lch2lab((L,max(C,0),h)))))
def hex2lch(h): return lab2lch(rgb2oklab(hex2rgb(h)))

def cvd(c, kind):
    r,g,b=(lin(x) for x in c); M=MACHADO[kind]
    return tuple(unlin(M[i][0]*r+M[i][1]*g+M[i][2]*b) for i in range(3))
def dE(h1,h2,kind=None):
    c1,c2=hex2rgb(h1),hex2rgb(h2)
    if kind: c1,c2=cvd(c1,kind),cvd(c2,kind)
    return 100*math.dist(rgb2oklab(c1),rgb2oklab(c2))
def cvd_dE(h1,h2): return min(dE(h1,h2,"protan"),dE(h1,h2,"deutan"))
def rel_lum(h):
    r,g,b=(lin(x) for x in hex2rgb(h)); return 0.2126*r+0.7152*g+0.0722*b
def contrast(h1,h2):
    a,b=sorted((rel_lum(h1),rel_lum(h2)),reverse=True); return (a+0.05)/(b+0.05)
def mix(h1,h2,t):
    a,b=rgb2oklab(hex2rgb(h1)),rgb2oklab(hex2rgb(h2))
    return rgb2hex(tuple(unlin(v) for v in oklab2rgb(tuple(a[i]+(b[i]-a[i])*t for i in range(3)))))
def chromatic(h): return hex2lch(h)[1]>=0.04

def snap(h, mode, bg):
    """Keep hue; put L in the band and C at the target, searching L across the
    band for the first position where the target chroma fits the sRGB gamut
    and the mark clears 3:1 on the surface."""
    L0,C0,hue=hex2lch(h); lo,hi=BAND[mode]
    C=max(C0,CHROMA_TARGET)
    Lpref=min(max(L0,lo+0.02),hi-0.02)
    # candidate L values ordered by distance from the preferred L
    cands=sorted([lo+0.02+i*0.01 for i in range(int((hi-lo-0.04)/0.01)+1)],key=lambda L:abs(L-Lpref))
    for Ltry in cands:
        if fits((Ltry,C,hue)) and contrast(lch2hex((Ltry,C,hue)),bg)>=3.0:
            return lch2hex((Ltry,C,hue))
    for Ltry in cands:  # relax contrast (relief rule: labels/table view)
        if fits((Ltry,C,hue)): return lch2hex((Ltry,C,hue))
    for Ctry in (0.12,0.115,0.11,0.106):  # hue can't carry target chroma at any band L
        for Ltry in cands:
            if fits((Ltry,Ctry,hue)): return lch2hex((Ltry,Ctry,hue))
    return lch2hex((Lpref,C,hue))

def one_hue_ramp(base, bg, ink, n, min_contrast, min_dL):
    """One hue (from base), L from a surface-side start that clears
    min_contrast to an end at/after base, guaranteeing dL >= min_dL."""
    Lb,Cb,hb=hex2lch(base); Lbg=hex2lch(bg)[0]; Link=hex2lch(ink)[0]
    direction=1 if Link>Lbg else -1
    if Cb<0.04: Cb=0.0  # neutral ramp
    # start: first L from the surface that clears contrast
    L=Lbg; start=None
    for _ in range(200):
        L+=direction*0.005
        if contrast(lch2hex((L,Cb*0.6,hb)),bg)>=min_contrast: start=L; break
    if start is None: start=Lbg+direction*0.3
    end=Lb if (Lb-start)*direction>0 else start+direction*0.3
    need=start+direction*min_dL*(n-1)*1.15
    if (need-end)*direction>0: end=need
    # never overshoot ink
    if (end-Link)*direction>0: end=Link
    out=[]
    for i in range(n):
        t=i/(n-1); Li=start+(end-start)*t; Ci=Cb*(0.55+0.45*t)
        out.append(lch2hex((Li,Ci,hb)))
    return out

def _prune(theme, drop):
    t2=dict(theme)
    for kk in (drop,"bright_"+drop): t2.pop(kk,None)
    return t2

def derive(theme, _dropped=()):
    mode=theme.get("mode","dark"); bg=theme["background"]; fg=theme["foreground"]
    accent=theme.get("accent",fg); urgent=theme.get("red",accent)
    keys=["blue","orange","green","yellow","magenta","cyan","red","brown"]
    raw=[]
    for k in keys:
        for kk in (k,"bright_"+k):
            v=theme.get(kk)
            if v and v.lower() not in [r[1].lower() for r in raw]: raw.append((k,v))
    cands=[(k,snap(v,mode,bg),hex2lch(v)[2]) for k,v in raw if chromatic(v)]
    uniq=[]
    for k,s,hue in cands:
        if all(min(abs(hue-u[2]),360-abs(hue-u[2]))>=18 for u in uniq): uniq.append((k,s,hue))
    uniq=uniq[:8]
    mono=len(uniq)<3
    result={"mode":mode,"surface":bg,"ink":fg,"monochrome":mono,"dropped":list(_dropped)}
    base=accent if chromatic(accent) else fg
    if not mono:
        hexes=[u[1] for u in uniq]; n=len(hexes)
        M=[[cvd_dE(hexes[i],hexes[j]) if i!=j else 0 for j in range(n)] for i in range(n)]
        N=[[dE(hexes[i],hexes[j]) if i!=j else 0 for j in range(n)] for i in range(n)]
        best=None
        for perm in itertools.permutations(range(n)):
            if perm[0]>perm[-1]: continue
            worst=min(M[perm[i]][perm[i+1]] for i in range(n-1))
            worstN=min(N[perm[i]][perm[i+1]] for i in range(n-1))
            score=(worstN>=15.0, worst>=6.0, worst, worstN)
            if best is None or score>best[0]: best=(score,perm)
        perm=best[1]; worst,worstN=best[0][2],best[0][3]
        if worst<6.0 or worstN<15.0:
            if n>3:
                i=min(range(n-1),key=lambda i:(M[perm[i]][perm[i+1]] if worst<6.0 else N[perm[i]][perm[i+1]]))
                a,b=perm[i],perm[i+1]; loser=a if sum(M[a])<sum(M[b]) else b
                return derive(_prune(theme,uniq[loser][0]),_dropped+(uniq[loser][0],))
            mono=True; result["monochrome"]=True; result["note"]="three hues still collide; ordinal fallback"
        else:
            result["categorical"]=[{"slot":i+1,"hue":uniq[p][0],"hex":hexes[p]} for i,p in enumerate(perm)]
            result["worstAdjacentCVD"]=round(worst,1); result["worstAdjacentNormal"]=round(worstN,1)
            aL,aC,ah=hex2lch(accent)
            far=max(uniq,key=lambda u: min(abs(u[2]-ah),360-abs(u[2]-ah)))
            poleA=snap(accent,mode,bg) if chromatic(accent) else uniq[0][1]
            result["diverging"]={"negative":far[1],"midpoint":mix(bg,fg,0.18),"positive":poleA}
    if mono:
        ordinal=one_hue_ramp(base,bg,fg,4,2.1,0.07)
        result["categorical"]=[{"slot":i+1,"hue":"ordinal","hex":h} for i,h in enumerate(ordinal)]
        result["diverging"]={"negative":mix(bg,fg,0.6),"midpoint":mix(bg,fg,0.18),"positive":ordinal[-1]}
    result["ordinal"]=one_hue_ramp(base,bg,fg,4,2.1,0.07)
    result["sequential"]=one_hue_ramp(base,bg,fg,7,1.15,0.0)
    def st(k,fallback):
        v=theme.get(k); return snap(v,mode,bg) if v and chromatic(v) else fallback
    result["status"]={"good":st("green",mix(bg,fg,0.7)),"warning":st("yellow",mix(bg,fg,0.55)),
                      "serious":st("orange",mix(bg,fg,0.85)),"critical":snap(urgent,mode,bg) if chromatic(urgent) else fg}
    result["chrome"]={"surface":bg,"ink":fg,"secondary":mix(fg,bg,0.13),"muted":mix(fg,bg,0.3),
                      "gridline":mix(bg,fg,0.12),"baseline":mix(bg,fg,0.25),"other":mix(bg,fg,0.32),"emphasisAccent":accent}
    result["contrast"]={"ink/surface":round(contrast(fg,bg),2),"muted/surface":round(contrast(result["chrome"]["muted"],bg),2),
                        "accent/surface":round(contrast(accent,bg),2),"urgent/surface":round(contrast(urgent,bg),2)}
    return result
