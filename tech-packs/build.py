#!/usr/bin/env python3
"""Generates the three Infinity Story tech-pack HTML files (SVG flats inline).
Run: python3 build.py && node render_pdf.js *.html
"""
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATE = "08 Sep 2026"
BRAND = "INFINITY STORY"

# ----------------------------------------------------------------- CSS
CSS = """
@page { size: A4; margin: 12mm; }
* { box-sizing: border-box; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 9.5pt; color: #111; margin: 0; background: #fff; }
h1 { font-size: 16pt; margin: 0 0 2mm; letter-spacing: .5px; }
h2, h3 { page-break-after: avoid; }
h2 { font-size: 12pt; margin: 6mm 0 2mm; padding-bottom: 1mm; border-bottom: 1.5px solid #111; text-transform: uppercase; letter-spacing: .5px; }
h3 { font-size: 10pt; margin: 4mm 0 1.5mm; }
p { margin: 0 0 2mm; line-height: 1.35; }
table { border-collapse: collapse; width: 100%; margin: 1.5mm 0 3mm; page-break-inside: avoid; }
th, td { border: 1px solid #777; padding: 1.2mm 1.8mm; vertical-align: top; text-align: left; font-size: 8.8pt; }
th { background: #e9e9e9; font-weight: bold; }
td.num, th.num { text-align: center; white-space: nowrap; }
tr { page-break-inside: avoid; }
.head { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2mm 6mm; border: 1.5px solid #111; padding: 3mm; margin-bottom: 4mm; }
.head div { font-size: 9pt; }
.head b { display: inline-block; min-width: 30mm; color: #444; font-weight: normal; }
.brand { font-size: 20pt; font-weight: bold; letter-spacing: 3px; }
.sub { color: #555; font-size: 9pt; }
.page { page-break-before: always; }
.note { background: #fff6d6; border-left: 3px solid #e0b100; padding: 2mm 3mm; margin: 2mm 0 3mm; font-size: 8.8pt; }
.tbc { background: #fff0f0; border-left: 3px solid #d33; padding: 2mm 3mm; margin: 2mm 0 3mm; font-size: 8.8pt; }
.tag { display: inline-block; background: #d33; color: #fff; font-size: 7.5pt; padding: 0 1.2mm; border-radius: 2px; font-weight: bold; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; }
.three { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4mm; }
figure { margin: 0; text-align: center; page-break-inside: avoid; }
figcaption { font-size: 8pt; color: #444; margin-top: 1mm; }
svg { max-width: 100%; height: auto; }
ul, ol { margin: 0 0 2mm; padding-left: 5mm; }
li { margin-bottom: .8mm; line-height: 1.3; }
.small { font-size: 8pt; color: #444; }
.sw { display: inline-block; width: 5mm; height: 3.5mm; border: 1px solid #555; vertical-align: middle; margin-right: 1.5mm; }
.kv td:first-child { width: 38%; background: #f5f5f5; }
"""

def html_page(title, body, subtitle=""):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<style>{CSS}</style></head><body>{body}</body></html>"""

def header(style_no, style_name, doc_type, size_info, sample, season="FW 2026/27", extra=None):
    cells = [
        ("Style No.", style_no), ("Style name", style_name), ("Document", doc_type),
        ("Brand", "Infinity Story (Russia)"), ("Season", season), ("Date / version", f"{DATE} / v1.0"),
        ("Size range", size_info), ("Sample size", sample), ("Units", "centimetres (cm), grams (g)"),
    ]
    if extra: cells += extra
    inner = "".join(f"<div><b>{k}</b>{v}</div>" for k, v in cells)
    return f"""<div class="brand">{BRAND}</div><div class="sub">Women's ready-to-wear · Technical specification</div>
<h1 style="margin-top:2mm">{doc_type}: {style_name}</h1><div class="head">{inner}</div>"""

# ----------------------------------------------------------------- SVG helpers
STROKE = 'stroke="#111" stroke-width="1.3" stroke-linejoin="round" stroke-linecap="round"'
THIN = 'stroke="#111" stroke-width="0.7" stroke-linejoin="round" stroke-linecap="round"'
DASH = 'stroke="#111" stroke-width="0.6" stroke-dasharray="3 2"'
DIM = 'stroke="#c00" stroke-width="0.6"'

def wavy(x1, y1, x2, y2, amp=2.2, n=None, phase=0.0):
    """Path of a wavy line between two points (ruffle edge)."""
    L = math.hypot(x2 - x1, y2 - y1)
    if n is None: n = max(3, int(L / 6))
    dx, dy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -dy, dx
    pts = []
    for i in range(n + 1):
        t = i / n
        px, py = x1 + dx * L * t, y1 + dy * L * t
        s = amp * math.sin(t * n * math.pi + phase)
        pts.append((px + nx * s, py + ny * s))
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(pts)):
        (ax, ay), (bx, by) = pts[i - 1], pts[i]
        cx, cy = (ax + bx) / 2, (ay + by) / 2
        d += f" Q{ax + (cx-ax)*0.3:.1f},{ay + (cy-ay)*0.3 + (ny*amp*0.9 if i%2 else -ny*amp*0.9):.1f} {bx:.1f},{by:.1f}"
    return d

def gathers(x1, y1, x2, y2, depth, n=14, side=1):
    """Short perpendicular ticks along a line to show gathering."""
    L = math.hypot(x2 - x1, y2 - y1)
    dx, dy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -dy * side, dx * side
    out = []
    for i in range(1, n):
        t = i / n
        px, py = x1 + dx * L * t, y1 + dy * L * t
        out.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px + nx*depth:.1f}" y2="{py + ny*depth:.1f}" {THIN} stroke-width="0.5"/>')
    return "".join(out)

def dim_h(x1, x2, y, label, above=True, color="#c00"):
    off = -3 if above else 3
    ty = y - 3 if above else y + 8
    return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="0.6"/>'
            f'<line x1="{x1}" y1="{y-3}" x2="{x1}" y2="{y+3}" stroke="{color}" stroke-width="0.6"/>'
            f'<line x1="{x2}" y1="{y-3}" x2="{x2}" y2="{y+3}" stroke="{color}" stroke-width="0.6"/>'
            f'<text x="{(x1+x2)/2}" y="{ty}" font-size="7" fill="{color}" text-anchor="middle" font-family="Arial">{label}</text>')

def dim_v(x, y1, y2, label, left=True, color="#c00"):
    tx = x - 3 if left else x + 3
    anchor = "end" if left else "start"
    return (f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{color}" stroke-width="0.6"/>'
            f'<line x1="{x-3}" y1="{y1}" x2="{x+3}" y2="{y1}" stroke="{color}" stroke-width="0.6"/>'
            f'<line x1="{x-3}" y1="{y2}" x2="{x+3}" y2="{y2}" stroke="{color}" stroke-width="0.6"/>'
            f'<text x="{tx}" y="{(y1+y2)/2+2.5}" font-size="7" fill="{color}" text-anchor="{anchor}" font-family="Arial">{label}</text>')

def label(x, y, t, size=7, anchor="middle", color="#111", bold=False):
    w = ' font-weight="bold"' if bold else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-family="Arial"{w}>{t}</text>'

def callout(x1, y1, x2, y2, t, anchor="start"):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#333" stroke-width="0.5"/>'
            f'<circle cx="{x1}" cy="{y1}" r="1.2" fill="#333"/>'
            + label(x2 + (2 if anchor == "start" else -2), y2 + 2.5, t, 6.5, anchor, "#333"))

# ----------------------------------------------------------------- CARDIGAN drawings
PINK = "#f2c4cb"; PINK2 = "#e7aeb8"; OLIVE = "#6f7a2e"; CHART = "#b7b03a"; PETAL = "#fbf3f3"; BLUSH = "#f4d9dd"
CHK_BLUE = "#a9d6e6"; CHK_GREEN = "#3f9a6a"

TULIP_DEF = f"""
<symbol id="tulip" viewBox="-14 -34 28 40" overflow="visible">
  <path d="M0,6 C-1,-4 1,-14 0,-22" fill="none" stroke="{OLIVE}" stroke-width="2.2" stroke-linecap="round"/>
  <path d="M0,4 C-6,-2 -12,-4 -13,-14 C-8,-11 -3,-8 0,-2 Z" fill="{OLIVE}"/>
  <path d="M0,2 C5,-4 10,-8 13,-16 C10,-8 5,-4 1,0 Z" fill="{CHART}"/>
  <path d="M-1,-8 C-5,-12 -9,-14 -11,-20 C-7,-18 -3,-15 0,-12 Z" fill="{CHART}"/>
  <path d="M-6,-22 C-7,-27 -6,-32 0,-33 C6,-32 7,-27 6,-22 C4,-20 -4,-20 -6,-22 Z" fill="{PETAL}" stroke="{BLUSH}" stroke-width="0.6"/>
  <path d="M-2,-21 C-3,-27 -2,-31 0,-33 C2,-31 3,-27 2,-21 Z" fill="{BLUSH}"/>
</symbol>
<pattern id="check" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <rect width="7" height="7" fill="#fff"/><rect width="3.5" height="3.5" fill="{CHK_BLUE}"/><rect x="3.5" y="3.5" width="3.5" height="3.5" fill="{CHK_GREEN}"/>
</pattern>
<pattern id="rib" width="3" height="6" patternUnits="userSpaceOnUse">
  <rect width="3" height="6" fill="{PINK2}"/><line x1="1.5" y1="0" x2="1.5" y2="6" stroke="#d894a1" stroke-width="0.8"/>
</pattern>
"""

def cardigan_body(front=True):
    """Shared body silhouette; returns svg fragments. Scale 2.5px/cm, centre x=260, HPS y=36."""
    s = 2.5; cx = 260; y0 = 36
    nh = 10.5 * s; sh = 29 * s; slope = 2 * s; ah = 24 * s
    L = 50 * s; rib = 6 * s; hemh = 25 * s
    ys = y0 + slope; ya = ys + ah; yr = y0 + L - rib; yh = y0 + L
    # sleeves
    ang = math.radians(28); d = (math.cos(ang), math.sin(ang)); n = (-d[1], d[0])
    SL = 45 * s; cuff = 6 * s; topw = 48 * s; cw = 12 * s * 2; cr = 9.5 * s * 2
    parts = []
    def sleeve(sign):
        S = (cx + sign * sh, ys)
        dd = (sign * d[0], d[1])
        nn = (sign * n[0], n[1])
        E = (S[0] + dd[0] * (SL - cuff), S[1] + dd[1] * (SL - cuff))     # top edge at rib start
        E2 = (S[0] + dd[0] * SL, S[1] + dd[1] * SL)                       # cuff end
        U = (S[0] + nn[0] * topw * 0.72, S[1] + nn[1] * topw * 0.72)      # underarm on sleeve
        Eu = (E[0] + nn[0] * cw, E[1] + nn[1] * cw)
        E2u = (E2[0] + nn[0] * cr, E2[1] + nn[1] * cr)
        Ec = (E2[0] - nn[0] * (cr - cw) / 2 * 0 , E2[1])
        body_under = (cx + sign * sh, ya)
        p = (f'<path d="M{S[0]:.1f},{S[1]:.1f} L{E[0]:.1f},{E[1]:.1f} L{Eu[0]:.1f},{Eu[1]:.1f} '
             f'Q{body_under[0] + sign*6:.1f},{body_under[1] + 14:.1f} {body_under[0]:.1f},{body_under[1]:.1f} Z" fill="{PINK}" {STROKE}/>')
        # cuff rib
        p += (f'<path d="M{E[0]:.1f},{E[1]:.1f} L{E2[0]:.1f},{E2[1]:.1f} L{E2u[0]:.1f},{E2u[1]:.1f} L{Eu[0]:.1f},{Eu[1]:.1f} Z" fill="url(#rib)" {STROKE}/>')
        # white stripes on cuff
        for k in (0.35, 0.62):
            a = (E[0] + dd[0] * cuff * k, E[1] + dd[1] * cuff * k)
            b = (a[0] + nn[0] * (cw + (cr - cw) * k), a[1] + nn[1] * (cw + (cr - cw) * k))
            p += f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#fff" stroke-width="2"/>'
        # tulips on sleeve (near cuff, outer side)
        angdeg = math.degrees(math.atan2(dd[1], dd[0]))
        base = (E[0] + nn[0] * cw * 0.55, E[1] + nn[1] * cw * 0.55)
        p += f'<g transform="translate({base[0]:.1f},{base[1]:.1f}) rotate({angdeg + 90 if sign>0 else angdeg - 90 + 180:.0f})"><use href="#tulip" x="-8" y="-6" width="28" height="40"/><use href="#tulip" x="8" y="-2" width="24" height="34"/></g>'
        return p, S, E2, E2u
    left = sleeve(-1); right = sleeve(1)
    # body
    bx1, bx2 = cx - sh, cx + sh
    body = (f'<path d="M{bx1},{ys} L{bx2},{ys} L{bx2},{yr} L{bx1},{yr} Z" fill="{PINK}" {STROKE}/>')
    ribp = (f'<path d="M{bx1},{yr} L{bx2},{yr} Q{bx2-2},{yh-4} {cx+hemh},{yh} L{cx-hemh},{yh} Q{bx1+2},{yh-4} {bx1},{yr} Z" fill="url(#rib)" {STROKE}/>')
    for k in (0.4, 0.68):
        yy = yr + rib * k
        ribp += f'<line x1="{bx1+1.5}" y1="{yy}" x2="{bx2-1.5}" y2="{yy}" stroke="#fff" stroke-width="2"/>'
    return dict(s=s, cx=cx, y0=y0, nh=nh, sh=sh, ys=ys, ya=ya, yr=yr, yh=yh, sleeves=left[0] + right[0], body=body, rib=ribp)

def cardigan_front_svg():
    g = cardigan_body(True)
    s, cx, y0, nh, sh, ys, ya, yr, yh = [g[k] for k in ("s", "cx", "y0", "nh", "sh", "ys", "ya", "yr", "yh")]
    fd = 9 * s   # front neck drop
    pw = 4 * s   # placket width
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 250" width="680">', TULIP_DEF]
    out.append(g["sleeves"]); out.append(g["body"]); out.append(g["rib"])
    # tulips on fronts (4) rising from rib
    for x in (cx - 60, cx - 28, cx + 28, cx + 60):
        out.append(f'<use href="#tulip" x="{x-15}" y="{yr-38}" width="30" height="42"/>')
    # neck opening
    out.append(f'<path d="M{cx-nh},{y0} Q{cx-nh},{y0+fd} {cx},{y0+fd} Q{cx+nh},{y0+fd} {cx+nh},{y0}" fill="#fff" {STROKE}/>')
    # front opening line (right front over left)
    out.append(f'<line x1="{cx}" y1="{y0+fd}" x2="{cx}" y2="{yh}" {THIN}/>')
    # placket (check)
    out.append(f'<rect x="{cx-pw/2}" y="{y0+fd-2}" width="{pw}" height="{yh-(y0+fd)+2}" fill="url(#check)" {STROKE}/>')
    out.append(f'<rect x="{cx-pw/2-1.5}" y="{y0+fd-2}" width="1.5" height="{yh-(y0+fd)+2}" fill="#fff" stroke="none"/>')
    out.append(f'<rect x="{cx+pw/2}" y="{y0+fd-2}" width="1.5" height="{yh-(y0+fd)+2}" fill="#fff" stroke="none"/>')
    # buttons 5
    yb0 = y0 + fd + 1.5 * s; sp = 8.5 * s
    for i in range(5):
        yy = yb0 + i * sp
        out.append(f'<circle cx="{cx}" cy="{yy}" r="3" fill="#b89a6a" {THIN}/><circle cx="{cx-1}" cy="{yy-1}" r=".6" fill="#111"/><circle cx="{cx+1}" cy="{yy+1}" r=".6" fill="#111"/>')
    # collar: pointed, check
    ch = 8 * s; cp = 8.5 * s
    colL = f'M{cx-nh-2},{y0-1} L{cx-nh-9},{y0+ch+2} L{cx-2},{y0+fd+2} L{cx-nh+2},{y0+fd-14} Q{cx-nh+1},{y0+3} {cx-nh-2},{y0-1} Z'
    colR = f'M{cx+nh+2},{y0-1} L{cx+nh+9},{y0+ch+2} L{cx+2},{y0+fd+2} L{cx+nh-2},{y0+fd-14} Q{cx+nh-1},{y0+3} {cx+nh+2},{y0-1} Z'
    for c in (colL, colR):
        out.append(f'<path d="{c}" fill="url(#check)" {STROKE}/>')
    out.append(f'<path d="M{cx-nh-2},{y0-1} Q{cx},{y0-9} {cx+nh+2},{y0-1}" fill="none" {STROKE}/>')  # back collar stand edge
    # callouts
    out.append(callout(cx + nh + 6, y0 + 6, cx + 150, y0 - 14, "Knitted point collar, jacquard check, white edge tipping"))
    out.append(callout(cx + pw / 2, y0 + fd + 30, cx + 150, y0 + fd + 30, "Jacquard check placket, 4 cm, 5 buttons (brand supplied)"))
    out.append(callout(cx + 60, yr - 20, cx + 150, yr - 2, "Intarsia tulip motif, front x4 / back x4 / sleeve x2 each"))
    out.append(callout(cx - 30, yr + 8, cx - 150, yh + 14, "1x1 rib hem 6 cm, 2 white stripes", "end"))
    out.append(callout(cx - sh - 60, ys + 60, cx - 150, ys + 84, "1x1 rib cuff 6 cm, 2 white stripes", "end"))
    out.append(callout(cx - sh, ys, cx - 150, ys - 22, "Drop shoulder, linked seam", "end"))
    out.append(label(cx, 246, "FRONT VIEW · not to scale · colours indicative only", 7, "middle", "#444"))
    out.append("</svg>")
    return "".join(out)

def cardigan_back_svg():
    g = cardigan_body(False)
    s, cx, y0, nh, sh, ys, ya, yr, yh = [g[k] for k in ("s", "cx", "y0", "nh", "sh", "ys", "ya", "yr", "yh")]
    bd = 2 * s
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 250" width="680">', TULIP_DEF]
    out.append(g["sleeves"]); out.append(g["body"]); out.append(g["rib"])
    for x in (cx - 60, cx - 20, cx + 20, cx + 60):
        out.append(f'<use href="#tulip" x="{x-15}" y="{yr-38}" width="30" height="42"/>')
    # back neck + collar seen from back (folded collar)
    out.append(f'<path d="M{cx-nh},{y0} Q{cx},{y0+bd*2} {cx+nh},{y0}" fill="#fff" {STROKE}/>')
    out.append(f'<path d="M{cx-nh-3},{y0-1} Q{cx},{y0+bd*2+2} {cx+nh+3},{y0-1} L{cx+nh+10},{y0+16} Q{cx},{y0+26} {cx-nh-10},{y0+16} Z" fill="url(#check)" {STROKE}/>')
    out.append(callout(cx, y0 + 22, cx + 150, y0 - 12, "Collar fall at CB 8 cm"))
    out.append(callout(cx + 20, yr - 20, cx + 150, yr - 2, "Back: intarsia tulips x4, same motif as front"))
    out.append(callout(cx - sh, ya, cx - 150, ya + 30, "No armhole shaping (straight)", "end"))
    out.append(label(cx, 246, "BACK VIEW · not to scale", 7, "middle", "#444"))
    out.append("</svg>")
    return "".join(out)

def cardigan_panels_svg():
    """Knit panel shapes with dimensions (S1 / S2)."""
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 330" width="760">']
    s = 2.2
    # ---- BACK panel
    x0, y0 = 75, 30
    w = 58 * s; L = 50 * s; rib = 6 * s; nh = 21 * s; slope = 2 * s; nd = 2 * s; ah = 24 * s
    cx = x0 + w / 2
    p = (f'M{x0},{y0+slope} L{cx-nh/2},{y0} Q{cx},{y0+nd*2} {cx+nh/2},{y0} L{x0+w},{y0+slope} '
         f'L{x0+w},{y0+L-rib} L{x0},{y0+L-rib} Z')
    out.append(f'<path d="{p}" fill="#fafafa" {STROKE}/>')
    out.append(f'<rect x="{x0}" y="{y0+L-rib}" width="{w}" height="{rib}" fill="url(#ribg)" {STROKE}/>')
    out.append(f'<line x1="{x0}" y1="{y0+slope+ah}" x2="{x0-6}" y2="{y0+slope+ah}" {THIN}/>')
    out.append(f'<line x1="{x0+w}" y1="{y0+slope+ah}" x2="{x0+w+6}" y2="{y0+slope+ah}" {THIN}/>')
    out.append(label(cx, y0 + L / 2, "BACK", 8, bold=True))
    out.append(label(cx, y0 + L / 2 + 10, "x1", 7))
    out.append(dim_h(x0, x0 + w, y0 + L + 12, "58 / 65", above=False))
    out.append(dim_v(x0 - 12, y0, y0 + L, "50 / 53"))
    out.append(dim_v(x0 + w + 12, y0 + slope, y0 + slope + ah, "24 / 26 armhole", left=False))
    out.append(dim_v(x0 + w + 12, y0 + L - rib, y0 + L, "rib 6", left=False))
    out.append(dim_h(cx - nh / 2, cx + nh / 2, y0 - 8, "neck 21 / 22"))
    out.append(dim_v(x0 - 12, y0, y0 + slope, "", left=True))
    out.append(label(x0 - 14, y0 + slope + 3, "slope 2", 6.5, "end", "#c00"))
    # ---- FRONT panel (left front as worn = right on page) with placket
    x1 = x0 + w + 70; fw = 27 * s; pw = 4 * s; fd = 9 * s
    fx = x1; fcx = fx + fw  # CF at right edge
    p = (f'M{fx},{y0+slope} L{fcx-nh/2},{y0} Q{fcx-nh/2},{y0+fd} {fcx},{y0+fd} L{fcx},{y0+L-rib} L{fx},{y0+L-rib} Z')
    out.append(f'<path d="{p}" fill="#fafafa" {STROKE}/>')
    out.append(f'<rect x="{fx}" y="{y0+L-rib}" width="{fw}" height="{rib}" fill="url(#ribg)" {STROKE}/>')
    out.append(f'<rect x="{fcx+4}" y="{y0+fd}" width="{pw}" height="{L-fd}" fill="url(#chkg)" {STROKE}/>')
    out.append(label(fx + fw / 2, y0 + L / 2, "FRONT", 8, bold=True))
    out.append(label(fx + fw / 2, y0 + L / 2 + 10, "x2 (mirror)", 7))
    out.append(label(fcx + 4 + pw / 2, y0 + L + 20, "PLACKET x2", 6.5, bold=True))
    out.append(label(fcx + 4 + pw / 2, y0 + L + 28, "(1 buttonhole, 1 button)", 6))
    out.append(dim_h(fx, fcx, y0 + L + 12, "27 / 30.5", above=False))
    out.append(dim_h(fcx + 4, fcx + 4 + pw, y0 + fd - 6, "4"))
    out.append(dim_v(fcx + 4 + pw + 10, y0 + fd, y0 + L, "41 / 43.5", left=False))
    out.append(dim_v(fx - 10, y0, y0 + fd, "9 / 9.5 neck drop", left=True))
    out.append(dim_h(fcx - nh / 2, fcx, y0 - 8, "10.5 / 11"))
    # ---- SLEEVE panel
    sx = x1 + fw + pw + 90; sy = 30
    tw = 48 * s; sl = 45 * s; cwid = 24 * s; crib = 19 * s
    scx = sx + tw / 2
    p = (f'M{sx},{sy} L{sx+tw},{sy} L{scx+cwid/2},{sy+sl-rib} L{scx-cwid/2},{sy+sl-rib} Z')
    out.append(f'<path d="{p}" fill="#fafafa" {STROKE}/>')
    out.append(f'<path d="M{scx-cwid/2},{sy+sl-rib} L{scx+cwid/2},{sy+sl-rib} L{scx+crib/2},{sy+sl} L{scx-crib/2},{sy+sl} Z" fill="url(#ribg)" {STROKE}/>')
    out.append(label(scx, sy + sl / 2, "SLEEVE", 8, bold=True))
    out.append(label(scx, sy + sl / 2 + 10, "x2", 7))
    out.append(dim_h(sx, sx + tw, sy - 8, "48 / 52 (straight top, no cap)"))
    out.append(dim_v(sx + tw + 12, sy, sy + sl, "45 / 46", left=False))
    out.append(dim_h(scx - cwid / 2, scx + cwid / 2, sy + sl - rib - 5, "24 / 26"))
    out.append(dim_h(scx - crib / 2, scx + crib / 2, sy + sl + 12, "19 / 21 rib relaxed", above=False))
    # ---- COLLAR
    cxx = sx; cyy = sy + sl + 50
    cl = 44 * s; chh = 8 * s
    p = f'M{cxx},{cyy} L{cxx+cl},{cyy} L{cxx+cl+14},{cyy+chh} L{cxx-14},{cyy+chh} Z'
    out.append(f'<path d="{p}" fill="url(#chkg)" {STROKE}/>')
    out.append(f'<line x1="{cxx+cl/2}" y1="{cyy}" x2="{cxx+cl/2}" y2="{cyy+chh}" {DASH}/>')
    out.append(label(cxx + cl / 2, cyy + chh + 20, "COLLAR x1 (one piece, jacquard check)", 7, bold=True))
    out.append(dim_h(cxx, cxx + cl, cyy - 6, "neck edge 44 / 46"))
    out.append(dim_v(cxx + cl + 24, cyy, cyy + chh, "8", left=False))
    out.append(label(cxx + cl / 2, cyy + chh + 29, "CB fold line dashed · outer edge 2-course white tipping", 6.5, "middle", "#444"))
    out.append("""<defs><pattern id="ribg" width="3" height="6" patternUnits="userSpaceOnUse"><rect width="3" height="6" fill="#fff"/><line x1="1.5" y1="0" x2="1.5" y2="6" stroke="#999" stroke-width="0.7"/></pattern>
    <pattern id="chkg" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="#fff"/><rect width="3" height="3" fill="#bbb"/></pattern></defs>""")
    out.append(label(380, 322, "KNIT PANEL SHAPES · finished measurements after steaming, cm · S1 = XS–M, S2 = L–2XL · factory converts to stitches/courses at approved gauge", 7, "middle", "#444"))
    out.append("</svg>")
    return "".join(out)

def cardigan_motif_svg():
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 180" width="520">', TULIP_DEF]
    out.append(f'<rect x="20" y="15" width="150" height="130" fill="{PINK}" {THIN}/>')
    out.append('<use href="#tulip" x="45" y="35" width="90" height="120"/>')
    out.append(dim_v(178, 40, 145, "approx. 22"))
    out.append(dim_h(50, 130, 152, "approx. 12", above=False))
    out.append(label(95, 172, "SINGLE MOTIF (repeat unit)", 7, bold=True))
    # colour key
    keys = [(PINK, "Col A · body ground (pink)"), (PETAL, "Col B · petal (off-white)"), (BLUSH, "Col C · petal shade (blush pink)"),
            (OLIVE, "Col D · stem + leaf (olive)"), (CHART, "Col E · leaf (chartreuse / ochre green)"),
            ("#fff", "Col F · check ground + tipping + stripes (white)"), (CHK_BLUE, "Col G · check (light blue)"), (CHK_GREEN, "Col H · check (green)")]
    for i, (c, t) in enumerate(keys):
        y = 25 + i * 16
        out.append(f'<rect x="215" y="{y-8}" width="14" height="10" fill="{c}" {THIN}/>')
        out.append(label(235, y, t, 7.5, "start"))
    out.append(f'<rect x="215" y="152" width="120" height="18" fill="url(#check)" {THIN}/>')
    out.append(label(340, 164, "Check placket / collar: 2-colour diamond check on white ground, cell approx. 1 cm", 7, "start"))
    out.append("</svg>")
    return "".join(out)

def placement_svg(kind="knit"):
    """Label placement diagram, inside view."""
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 440 200" width="440">']
    out.append(f'<path d="M60,40 L130,20 Q180,45 230,20 L300,40 L300,180 L60,180 Z" fill="#fafafa" {STROKE}/>')
    out.append(f'<path d="M130,20 Q180,45 230,20" fill="none" {STROKE}/>')
    # main label at CB neck
    out.append(f'<rect x="160" y="34" width="40" height="9" fill="#111"/>')
    out.append(f'<rect x="153" y="35" width="7" height="7" fill="#111"/><rect x="200" y="35" width="7" height="7" fill="#111"/>')
    out.append(label(180, 41, "INFINITY STORY", 4, "middle", "#fff"))
    out.append(label(156, 40, "XS", 3, "middle", "#fff")); out.append(label(203, 40, "M", 3, "middle", "#fff"))
    out.append(callout(200, 38, 250, 60, "1 · Main woven label, CB neck, centred,"))
    out.append(label(252, 69, "caught in neck seam / linked", 6.5, "start", "#333"))
    out.append(label(252, 77, "size flags at both ends (dual size)", 6.5, "start", "#333"))
    # care label at side seam
    out.append(f'<rect x="60" y="120" width="10" height="26" fill="#fff" {THIN}/>')
    out.append(callout(70, 130, 110, 110, "2 · Care / composition label, wearer's LEFT"))
    out.append(label(112, 119, "side seam, 10 cm above hem (top of rib)", 6.5, "start", "#333"))
    out.append(dim_v(50, 146, 180, "10"))
    out.append(label(180, 195, "INSIDE VIEW (back) · label placement", 7, "middle", "#444"))
    out.append("</svg>")
    return "".join(out)

# ----------------------------------------------------------------- BLOUSE drawings
CREAM = "#f6efe2"

def blouse_geom():
    s = 2.5; cx = 260; y0 = 40
    nh = 9 * s; fd = 8 * s; bd = 2 * s
    shoulder = 12 * s; sleeve = 15 * s; ah = 25 * s; L = 62 * s
    half = 26 * s; hemhalf = 26.5 * s
    ang = math.radians(20); d = (math.cos(ang), math.sin(ang)); n = (-d[1], d[0])
    return dict(s=s, cx=cx, y0=y0, nh=nh, fd=fd, bd=bd, shoulder=shoulder, sleeve=sleeve, ah=ah, L=L, half=half, hemhalf=hemhalf, d=d, n=n)

def blouse_body_paths(g, back=False):
    s, cx, y0, nh, d, n = g["s"], g["cx"], g["y0"], g["nh"], g["d"], g["n"]
    out = []
    ruff = 5 * s; sh_open = 18 * s
    for sign in (-1, 1):
        dd = (sign * d[0], d[1]); nn = (sign * n[0], n[1])
        H = (cx + sign * nh, y0)
        E = (H[0] + dd[0] * (g["shoulder"] + g["sleeve"]), H[1] + dd[1] * (g["shoulder"] + g["sleeve"]))
        Eu = (E[0] + nn[0] * sh_open, E[1] + nn[1] * sh_open)
        U = (cx + sign * g["half"], y0 + g["ah"])
        Hm = (cx + sign * g["hemhalf"], y0 + g["L"])
        body = (f'M{H[0]:.1f},{H[1]:.1f} L{E[0]:.1f},{E[1]:.1f} L{Eu[0]:.1f},{Eu[1]:.1f} '
                f'C{Eu[0]-sign*4:.1f},{Eu[1]+6:.1f} {U[0]+sign*9:.1f},{U[1]+5:.1f} {U[0]:.1f},{U[1]:.1f} L{Hm[0]:.1f},{Hm[1]:.1f} L{cx},{Hm[1]:.1f} L{cx},{H[1]+ (g["bd"] if back else g["fd"]):.1f} Z')
        out.append(f'<path d="{body}" fill="{CREAM}" {STROKE}/>')
        # sleeve ruffle: band along sleeve hem
        R1 = (E[0] + dd[0] * ruff, E[1] + dd[1] * ruff)
        R2 = (Eu[0] + dd[0] * ruff * 0.8, Eu[1] + dd[1] * ruff * 0.8)
        wave = wavy(R1[0], R1[1], R2[0], R2[1], amp=3.2, n=7)
        out.append(f'<path d="M{E[0]:.1f},{E[1]:.1f} L{R1[0]:.1f},{R1[1]:.1f} {wave[1:]} L{Eu[0]:.1f},{Eu[1]:.1f}" fill="{CREAM}" {STROKE}/>')
        out.append(gathers(E[0], E[1], Eu[0], Eu[1], 4 * sign * -1 if sign > 0 else 4, n=9, side=-1 if sign > 0 else 1))
    # hem line & neck
    out.append(f'<line x1="{cx - g["hemhalf"]+1}" y1="{y0+g["L"]-3}" x2="{cx+g["hemhalf"]-1}" y2="{y0+g["L"]-3}" {DASH}/>')
    return "".join(out)

def blouse_front_svg():
    g = blouse_geom(); s, cx, y0, nh, fd = g["s"], g["cx"], g["y0"], g["nh"], g["fd"]
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 260" width="680">']
    out.append(blouse_body_paths(g))
    # neckline + collar stand + ruffle
    yc = y0 + fd
    out.append(f'<path d="M{cx-nh},{y0} Q{cx-nh},{yc} {cx},{yc} Q{cx+nh},{yc} {cx+nh},{y0}" fill="#fff" {STROKE}/>')
    # collar stand band (2 cm) following neckline, front ends meet at CF
    st = 2 * s; rf = 2.5 * s
    neck = f'M{cx-nh},{y0} Q{cx-nh},{yc} {cx},{yc} Q{cx+nh},{yc} {cx+nh},{y0}'
    outer = f'M{cx-nh-1},{y0-st} Q{cx-nh-1},{yc-st} {cx},{yc-st} Q{cx+nh+1},{yc-st} {cx+nh+1},{y0-st}'
    out.append(f'<path d="{outer} Q{cx},{y0-st+6} {cx-nh-1},{y0-st} Z" fill="{CREAM}" {STROKE}/>')  # back of stand seen through neck
    out.append(f'<path d="{outer} L{cx+nh},{y0} Q{cx+nh},{yc} {cx},{yc} Q{cx-nh},{yc} {cx-nh},{y0} Z" fill="{CREAM}" {STROKE}/>')
    out.append(f'<path d="{neck}" fill="none" {STROKE}/>')
    out.append(f'<line x1="{cx}" y1="{yc-st}" x2="{cx}" y2="{yc}" {THIN}/>')  # CF split of stand
    # ruffle above stand: wavy edge offset by rf along the outer curve (approximate with translated copy)
    pts = []
    for i in range(0, 41):
        t = i / 40
        # quadratic bezier sampling of 'outer' left half then right half
        if t <= 0.5:
            u = t * 2; p0 = (cx-nh-1, y0-st); p1 = (cx-nh-1, yc-st); p2 = (cx, yc-st)
        else:
            u = (t - 0.5) * 2; p0 = (cx, yc-st); p1 = (cx+nh+1, yc-st); p2 = (cx+nh+1, y0-st)
        x = (1-u)**2*p0[0] + 2*(1-u)*u*p1[0] + u**2*p2[0]
        y = (1-u)**2*p0[1] + 2*(1-u)*u*p1[1] + u**2*p2[1]
        pts.append((x, y))
    d = ''
    for i, (x, y) in enumerate(pts):
        amp = rf + (2.4 if i % 2 else -0.6)
        d += ('M' if i == 0 else ' L') + f'{x:.1f},{y - amp:.1f}'
    out.append(f'<path d="{d}" fill="none" {STROKE}/>')
    out.append(f'<path d="M{cx-nh-1},{y0-st} L{cx-nh-1},{y0-st-rf:.1f}" {THIN}/>')
    out.append(f'<path d="M{cx+nh+1},{y0-st} L{cx+nh+1},{y0-st-rf:.1f}" {THIN}/>')
    out.append(gathers(cx-nh-1, yc-st, cx+nh+1, yc-st, -3, n=14) if False else '')
    # bib: pointed oval
    bw = 22 * s / 2; bl = 30 * s; pw = 2.5 * s; pl = 27 * s
    bib = f'M{cx-6},{yc-1} C{cx-bw-8},{yc+18} {cx-bw-2},{yc+60} {cx},{yc+bl} C{cx+bw+2},{yc+60} {cx+bw+8},{yc+18} {cx+6},{yc-1}'
    out.append(f'<path d="{bib}" fill="{CREAM}" {STROKE}/>')
    out.append(f'<path d="{bib}" fill="none" stroke="#8a9a6a" stroke-width="2.2" stroke-linejoin="round"/>')  # piping (self fabric)
    # placket
    out.append(f'<rect x="{cx-pw/2}" y="{yc-1}" width="{pw}" height="{pl}" fill="{CREAM}" {STROKE}/>')
    out.append(f'<line x1="{cx-pw/2}" y1="{yc}" x2="{cx-pw/2}" y2="{yc+pl}" stroke="#8a9a6a" stroke-width="1.8"/>')
    out.append(f'<line x1="{cx+pw/2}" y1="{yc}" x2="{cx+pw/2}" y2="{yc+pl}" stroke="#8a9a6a" stroke-width="1.8"/>')
    # placket ruffles on both sides, 3.5 cm
    rw = 3.5 * s
    out.append(f'<path d="{wavy(cx-pw/2-rw, yc+2, cx-pw/2-rw, yc+pl-1, amp=2.2, n=12)}" fill="none" {STROKE}/>')
    out.append(f'<path d="{wavy(cx+pw/2+rw, yc+2, cx+pw/2+rw, yc+pl-1, amp=2.2, n=12, phase=math.pi)}" fill="none" {STROKE}/>')
    out.append(f'<path d="M{cx-pw/2-rw},{yc+2} Q{cx-pw/2-rw/2},{yc-2} {cx-pw/2},{yc}" fill="none" {THIN}/><path d="M{cx+pw/2+rw},{yc+2} Q{cx+pw/2+rw/2},{yc-2} {cx+pw/2},{yc}" fill="none" {THIN}/>')
    out.append(f'<path d="M{cx-pw/2-rw},{yc+pl-1} Q{cx-pw/2-rw/2},{yc+pl+6} {cx-pw/2},{yc+pl}" fill="none" {THIN}/><path d="M{cx+pw/2+rw},{yc+pl-1} Q{cx+pw/2+rw/2},{yc+pl+6} {cx+pw/2},{yc+pl}" fill="none" {THIN}/>')
    out.append(gathers(cx - pw / 2, yc + 3, cx - pw / 2, yc + pl - 3, -4, n=16))
    out.append(gathers(cx + pw / 2, yc + 3, cx + pw / 2, yc + pl - 3, 4, n=16))
    # 7 buttons
    yb = yc + 1.5 * s; sp = (pl - 3 * s) / 6
    for i in range(7):
        yy = yb + i * sp
        out.append(f'<circle cx="{cx}" cy="{yy}" r="2.4" fill="#d5b45a" stroke="#8a6d1c" stroke-width="0.6"/>')
    # callouts
    out.append(callout(cx + nh + 2, y0 - st - 3, cx + 150, y0 - 22, "Stand collar 2 cm + single self ruffle 2.5 cm, piped top edge"))
    out.append(callout(cx + bw + 2, yc + 30, cx + 150, yc + 24, "Bib panel (inset), outer edge self-fabric piping 0.4 cm"))
    out.append(callout(cx + pw / 2 + rw, yc + 50, cx + 150, yc + 50, "Single ruffle 3.5 cm, gathered 1:2, set into placket seam"))
    out.append(callout(cx, yb + 3 * sp, cx + 150, yc + 76, "Placket 2.5 cm, piped both edges, 7 gold shank buttons (brand supplied)"))
    out.append(callout(cx + 88, y0 + 44, cx + 150, y0 + 108, "Cut-on (grown-on) short sleeve 15 cm + self ruffle 5 cm at hem"))
    out.append(callout(cx - 40, y0 + g["L"] - 3, cx - 150, y0 + g["L"] + 12, "Straight hem, 1 cm double-fold, edge-stitched", "end"))
    out.append(callout(cx - g["half"], y0 + g["ah"] + 30, cx - 150, y0 + g["ah"] + 40, "Side seam, 4-thread overlock", "end"))
    out.append(label(cx, 256, "FRONT VIEW · not to scale · all-over floral print not shown", 7, "middle", "#444"))
    out.append("</svg>")
    return "".join(out)

def blouse_back_svg():
    g = blouse_geom(); s, cx, y0, nh, bd = g["s"], g["cx"], g["y0"], g["nh"], g["bd"]
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 260" width="680">']
    out.append(blouse_body_paths(g, back=True))
    st = 2 * s; rf = 2.5 * s
    out.append(f'<path d="M{cx-nh},{y0} Q{cx},{y0+bd*2} {cx+nh},{y0} L{cx+nh+1},{y0-st} Q{cx},{y0-st+bd*2} {cx-nh-1},{y0-st} Z" fill="{CREAM}" {STROKE}/>')
    out.append(f'<path d="{wavy(cx-nh-2, y0-st-1, cx+nh+2, y0-st-1, amp=2, n=8)}" fill="none" {STROKE} transform="translate(0,{-rf+2})"/>')
    out.append(f'<path d="M{cx-nh-2},{y0-st-1} L{cx-nh-2},{y0-st-rf+1}" {THIN}/><path d="M{cx+nh+2},{y0-st-1} L{cx+nh+2},{y0-st-rf+1}" {THIN}/>')
    out.append(f'<line x1="{cx}" y1="{y0+bd*2}" x2="{cx}" y2="{y0+g["L"]}" {DASH}/>')
    out.append(callout(cx, y0 + 60, cx + 150, y0 + 40, "Back: plain, no CB seam (CB on fold)"))
    out.append(callout(cx + 60, y0 + 12, cx + 150, y0 - 16, "Shoulder / over-sleeve seam, one continuous seam"))
    out.append(label(cx, 256, "BACK VIEW · not to scale", 7, "middle", "#444"))
    out.append("</svg>")
    return "".join(out)

def bib_detail_svg():
    """Enlarged bib + section."""
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 250" width="520">']
    s = 5; cx = 130; yc = 30
    bw = 22 * s / 2; bl = 30 * s * 0.6; pw = 2.5 * s; pl = 27 * s * 0.6; rw = 3.5 * s
    bib = f'M{cx-8},{yc} C{cx-bw-10},{yc+30} {cx-bw-2},{yc+95} {cx},{yc+bl} C{cx+bw+2},{yc+95} {cx+bw+10},{yc+30} {cx+8},{yc}'
    out.append(f'<path d="{bib}" fill="{CREAM}" {STROKE}/>')
    out.append(f'<path d="{bib}" fill="none" stroke="#8a9a6a" stroke-width="3"/>')
    out.append(f'<rect x="{cx-pw/2}" y="{yc}" width="{pw}" height="{pl}" fill="{CREAM}" {STROKE}/>')
    out.append(f'<line x1="{cx-pw/2}" y1="{yc}" x2="{cx-pw/2}" y2="{yc+pl}" stroke="#8a9a6a" stroke-width="2.5"/>')
    out.append(f'<line x1="{cx+pw/2}" y1="{yc}" x2="{cx+pw/2}" y2="{yc+pl}" stroke="#8a9a6a" stroke-width="2.5"/>')
    out.append(f'<path d="{wavy(cx-pw/2-rw, yc+3, cx-pw/2-rw, yc+pl-2, amp=3, n=10)}" fill="none" {STROKE}/>')
    out.append(f'<path d="{wavy(cx+pw/2+rw, yc+3, cx+pw/2+rw, yc+pl-2, amp=3, n=10, phase=math.pi)}" fill="none" {STROKE}/>')
    out.append(f'<path d="M{cx-pw/2-rw},{yc+3} Q{cx-pw/2-rw/2},{yc-3} {cx-pw/2},{yc}" fill="none" {THIN}/><path d="M{cx+pw/2+rw},{yc+3} Q{cx+pw/2+rw/2},{yc-3} {cx+pw/2},{yc}" fill="none" {THIN}/>')
    out.append(f'<path d="M{cx-pw/2-rw},{yc+pl-2} Q{cx-pw/2-rw/2},{yc+pl+8} {cx-pw/2},{yc+pl}" fill="none" {THIN}/><path d="M{cx+pw/2+rw},{yc+pl-2} Q{cx+pw/2+rw/2},{yc+pl+8} {cx+pw/2},{yc+pl}" fill="none" {THIN}/>')
    out.append(gathers(cx - pw / 2, yc + 4, cx - pw / 2, yc + pl - 4, -6, n=14))
    out.append(gathers(cx + pw / 2, yc + 4, cx + pw / 2, yc + pl - 4, 6, n=14))
    yb = yc + 1.5 * s * 0.6; sp = (pl - 3 * s * 0.6) / 6
    for i in range(7):
        yy = yb + i * sp
        out.append(f'<circle cx="{cx}" cy="{yy}" r="3.2" fill="#d5b45a" stroke="#8a6d1c" stroke-width="0.7"/>')
        out.append(f'<line x1="{cx}" y1="{yy-4.5}" x2="{cx}" y2="{yy+4.5}" stroke="#111" stroke-width="0.5"/>')
    out.append(dim_h(cx - bw - 6, cx + bw + 6, yc + bl + 44, "22 (widest, piping to piping)", above=False))
    out.append(dim_v(cx + bw + 20, yc, yc + bl, "30 CF (collar seam to point)", left=False))
    out.append(dim_v(cx - bw - 18, yc, yc + pl, "27 placket", left=True))
    out.append(dim_h(cx - pw / 2, cx + pw / 2, yc - 8, "2.5"))
    out.append(dim_h(cx - pw / 2 - rw, cx - pw / 2, yc + pl + 14, "3.5", above=False))
    out.append(label(cx, yc + bl + 70, "BIB FRONT · enlarged", 7.5, "middle", "#444", True))
    # cross section (schematic, layers exaggerated)
    x = 300; y = 50
    out.append(label(x + 100, y - 20, "SECTION A–A through bib and placket (wearer's right side)", 7.5, "middle", "#111", True))
    base = y + 40
    out.append(f'<line x1="{x}" y1="{base}" x2="{x+70}" y2="{base}" stroke="#111" stroke-width="2.2"/>')                       # a body
    out.append(f'<circle cx="{x+72}" cy="{base-3}" r="3.5" fill="#8a9a6a" stroke="#111" stroke-width="0.7"/>')                  # b piping
    out.append(f'<line x1="{x+74}" y1="{base}" x2="{x+140}" y2="{base}" stroke="#111" stroke-width="2.2"/>')                    # c bib
    out.append(f'<path d="M{x+140},{base-2} q5,-22 10,0 q5,-22 10,0 q5,-22 10,0 q5,-22 10,0" fill="none" stroke="#111" stroke-width="1"/>')  # d ruffle
    out.append(f'<circle cx="{x+142}" cy="{base-4}" r="3.5" fill="#8a9a6a" stroke="#111" stroke-width="0.7"/>')                 # e piping
    out.append(f'<rect x="{x+142}" y="{base-1}" width="34" height="5" fill="#ccc" stroke="#111" stroke-width="0.8"/>')          # f placket
    out.append(f'<ellipse cx="{x+159}" cy="{base-6}" rx="5" ry="3" fill="#d5b45a" stroke="#8a6d1c" stroke-width="0.7"/>')
    out.append(f'<circle cx="{x+176}" cy="{base-4}" r="3.5" fill="#8a9a6a" stroke="#111" stroke-width="0.7"/>')                 # e piping
    out.append(f'<rect x="{x+146}" y="{base+7}" width="34" height="5" fill="#eee" stroke="#111" stroke-width="0.8" stroke-dasharray="2 1"/>')  # g under placket
    out.append(f'<line x1="{x+180}" y1="{base+12}" x2="{x+200}" y2="{base+12}" stroke="#111" stroke-width="2.2"/>')             # left front continues
    for lx, ly, lt in ((x + 35, base + 12, "a"), (x + 72, base - 10, "b"), (x + 107, base + 12, "c"), (x + 160, base - 26, "d"), (x + 142, base - 11, "e"), (x + 176, base - 11, "e"), (x + 190, base + 3, "f"), (x + 163, base + 22, "g")):
        out.append(label(lx, ly, lt, 7.5, "middle", "#c00", True))
    notes = ["a · Front body", "b · Self-fabric flat piping 0.4 cm in bib inset seam", "c · Bib panel", "d · Ruffle 3.5 cm gathered 1:2, caught in placket seam",
             "e · Piping on both placket edges", "f · Placket band 2.5 cm, fused, buttonholes (wearer's right)", "g · Under placket with buttons (wearer's left), overlap 2.5 cm"]
    for i, t in enumerate(notes):
        out.append(label(x, base + 40 + i * 11, t, 7, "start", "#333"))
    out.append(label(x + 100, base + 125, "Seam allowances: bib inset 1.0 · placket 1.0 · ruffle 0.7", 7, "middle", "#444"))
    out.append("</svg>")
    return "".join(out)

def collar_detail_svg():
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 660 130" width="660">']
    x, y = 30, 25
    # collar stand flat
    out.append(f'<path d="M{x},{y+40} L{x+200},{y+40} L{x+200},{y+20} L{x},{y+20} Z" fill="{CREAM}" {STROKE}/>')
    out.append(f'<path d="{wavy(x, y+19, x+200, y+19, amp=3, n=20)}" fill="none" {STROKE} transform="translate(0,-10)"/>')
    out.append(f'<line x1="{x}" y1="{y+19}" x2="{x}" y2="{y+9}" {THIN}/><line x1="{x+200}" y1="{y+19}" x2="{x+200}" y2="{y+9}" {THIN}/>')
    out.append(f'<line x1="{x}" y1="{y+20}" x2="{x+200}" y2="{y+20}" stroke="#8a9a6a" stroke-width="2.2"/>')
    out.append(gathers(x, y + 20, x + 200, y + 20, -6, n=30))
    out.append(f'<line x1="{x+100}" y1="{y+20}" x2="{x+100}" y2="{y+40}" {DASH}/>')
    out.append(f'<line x1="{x+4}" y1="{y+22}" x2="{x+4}" y2="{y+38}" {THIN}/>')  # buttonhole? no button on collar
    out.append(dim_v(x + 212, y + 20, y + 40, "2 stand", left=False))
    out.append(dim_v(x + 212, y + 6, y + 20, "2.5 ruffle", left=False))
    out.append(dim_h(x, x + 200, y + 52, "neck edge = 40 (XS–S), CB on fold, front ends straight", above=False))
    out.append(label(x + 100, y + 78, "COLLAR STAND WITH SINGLE RUFFLE · flat, outside", 7.5, "middle", "#444", True))
    # section
    sx, sy = 340, 22
    out.append(label(sx + 60, sy, "SECTION B–B collar stand", 7.5, "middle", "#111", True))
    out.append(f'<rect x="{sx}" y="{sy+40}" width="6" height="50" fill="#ccc" {THIN}/>')   # 1 outer stand fused
    out.append(f'<rect x="{sx+10}" y="{sy+40}" width="4" height="50" fill="#fff" {THIN}/>')  # 2 inner stand
    out.append(f'<circle cx="{sx+8}" cy="{sy+36}" r="3.5" fill="#8a9a6a" stroke="#111" stroke-width="0.7"/>')  # 3 piping
    out.append(f'<path d="M{sx+8},{sy+32} q-8,-10 0,-20 q8,-10 0,-12" fill="none" stroke="#111" stroke-width="1"/>')  # 4 ruffle
    out.append(f'<line x1="{sx-4}" y1="{sy+90}" x2="{sx+18}" y2="{sy+90}" stroke="#111" stroke-width="2"/>')  # 5 neck seam
    out.append(f'<line x1="{sx+18}" y1="{sy+90}" x2="{sx+70}" y2="{sy+100}" stroke="#111" stroke-width="2.2"/>')  # 6 body
    for lx, ly, lt in ((sx - 6, sy + 66, "1"), (sx + 22, sy + 66, "2"), (sx + 18, sy + 34, "3"), (sx + 18, sy + 12, "4"), (sx - 8, sy + 96, "5"), (sx + 50, sy + 108, "6")):
        out.append(label(lx, ly, lt, 7.5, "middle", "#c00", True))
    notes = ["1 · Outer stand, fused (light woven 40 g/m²)", "2 · Inner stand (facing), self fabric", "3 · Self piping 0.4 cm in top edge seam",
             "4 · Single ruffle 2.5 cm, gathered 1:2, narrow rolled hem", "5 · Neck seam 1 cm, inner stand closed with 0.1 edge-stitch", "6 · Body"]
    for i, t in enumerate(notes):
        out.append(label(sx + 90, sy + 40 + i * 11, t, 7, "start", "#333"))
    out.append("</svg>")
    return "".join(out)

def pattern_pieces_svg():
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 300" width="700">']
    # Front (half, on fold? no: CF has opening; front cut x1 on fold below bib? we draw half piece with CF)
    def piece(x, y, path, name, qty, grain_len=40, extra=""):
        out.append(f'<path d="{path}" fill="#fafafa" {STROKE} transform="translate({x},{y})"/>')
        out.append(f'<g transform="translate({x},{y})">{extra}</g>')
        out.append(label(x + 50, y - 6, name, 7.5, "middle", "#111", True))
        out.append(label(x + 50, y + 130, qty, 6.5, "middle", "#333"))
    # front body with cut-on sleeve & bib cut-out
    front = "M0,20 L60,8 L92,20 L88,45 Q66,50 60,66 L62,125 L0,125 Z"
    bibcut = f'<path d="M0,26 C-2,40 -1,60 0,78 C14,70 18,50 12,26 Z" fill="#fff" {DASH}/>'
    piece(60, 30, front, "1 · FRONT", "x2 (mirror) · CF opening · bib cut-out", extra=bibcut + f'<line x1="30" y1="70" x2="30" y2="115" {THIN}/><path d="M27,74 L30,70 L33,74" fill="none" {THIN}/>')
    out.append(label(110, 35 + 45, "CF", 6, "start", "#c00"))
    back = "M0,20 L60,8 L92,20 L88,45 Q66,50 60,66 L62,125 L0,125 Z"
    piece(200, 30, back, "2 · BACK", "x1 on fold (CB)", extra=f'<line x1="0" y1="20" x2="0" y2="125" stroke="#c00" stroke-width="1.2"/><line x1="30" y1="70" x2="30" y2="115" {THIN}/><path d="M27,74 L30,70 L33,74" fill="none" {THIN}/>')
    out.append(label(203, 35 + 100, "fold", 6, "start", "#c00"))
    bib = "M0,0 C-14,20 -12,55 0,80 C12,55 14,20 0,0 Z"
    piece(285, 30, bib, "3 · BIB PANEL", "x2 (mirror)", extra=f'<line x1="0" y1="15" x2="0" y2="65" {THIN}/>')
    out.append(f'<rect x="424" y="30" width="12" height="80" fill="#fafafa" {STROKE}/>')
    out.append(label(430, 24, "4 · PLACKET", 7.5, "middle", "#111", True)); out.append(label(430, 122, "x2 · fused", 6.5, "middle", "#333")); out.append(label(430, 130, "(1 BH side,", 6.5, "middle", "#333")); out.append(label(430, 138, "1 button side)", 6.5, "middle", "#333"))
    out.append(f'<rect x="480" y="30" width="110" height="12" fill="#fafafa" {STROKE}/>')
    out.append(label(535, 24, "5 · COLLAR STAND", 7.5, "middle", "#111", True)); out.append(label(535, 52, "x2 (outer fused + inner) · CB on fold", 6.5, "middle", "#333"))
    out.append(f'<rect x="480" y="70" width="140" height="10" fill="#fafafa" {STROKE}/>')
    out.append(label(550, 64, "6 · COLLAR RUFFLE", 7.5, "middle", "#111", True)); out.append(label(550, 92, "x1 · 2× neck edge length · straight grain", 6.5, "middle", "#333"))
    out.append(f'<rect x="480" y="110" width="150" height="16" fill="#fafafa" {STROKE}/>')
    out.append(label(555, 104, "7 · BIB / PLACKET RUFFLE", 7.5, "middle", "#111", True)); out.append(label(555, 138, "x2 · 2× placket length · straight grain", 6.5, "middle", "#333"))
    out.append(f'<rect x="480" y="160" width="130" height="18" fill="#fafafa" {STROKE}/>')
    out.append(label(545, 154, "8 · SLEEVE RUFFLE", 7.5, "middle", "#111", True)); out.append(label(545, 190, "x2 · 2× sleeve hem · straight grain", 6.5, "middle", "#333"))
    out.append(f'<path d="M480,215 L640,215 L650,225 L490,225 Z" fill="#fafafa" {STROKE}/>')
    out.append(label(565, 209, "9 · PIPING BIAS STRIP", 7.5, "middle", "#111", True)); out.append(label(565, 237, "true bias 45°, 2.2 cm wide, joined, total approx. 2.3 m", 6.5, "middle", "#333"))
    out.append(label(350, 290, "PATTERN PIECE LIST · schematic, not to scale · seam allowances per table 5", 7, "middle", "#444"))
    out.append("</svg>")
    return "".join(out)

def blouse_placement_svg():
    return placement_svg("woven").replace("(top of rib)", "")

def packaging_svg():
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 170" width="520">']
    out.append(f'<rect x="30" y="20" width="120" height="128" fill="#f4f4f4" stroke="#111" stroke-width="1.2"/>')
    out.append(f'<rect x="30" y="20" width="120" height="8" fill="#ddd" stroke="#111" stroke-width="0.8"/>')
    out.append(f'<rect x="110" y="18" width="8" height="12" fill="#fff" stroke="#111" stroke-width="0.8"/>')
    out.append(f'<rect x="52" y="45" width="76" height="70" fill="none" stroke="#111" stroke-width="2"/>')
    out.append(label(90, 76, "INFINITY", 9, "middle", "#111", True)); out.append(label(90, 90, "STORY", 9, "middle", "#111", True))
    out.append(f'<circle cx="42" cy="130" r="1.5" fill="none" stroke="#111" stroke-width="0.6"/>')
    out.append(dim_h(30, 150, 158, "approx. 30 (TBC)", above=False))
    out.append(dim_v(160, 20, 148, "approx. 32 (TBC)", left=False))
    out.append(callout(114, 22, 210, 22, "Zip-lock slider closure"))
    out.append(callout(42, 130, 210, 118, "Air vent hole, lower corner"))
    out.append(callout(52, 45, 210, 50, "Black logo print, front side only, brand artwork (supplied)"))
    out.append(label(90, 15, "POLYBAG · frosted PE, brand printed", 7, "middle", "#444", True))
    out.append(label(360, 150, "Fold garment to approx. 25 × 28 cm, print/logo side up", 7, "middle", "#444"))
    out.append("</svg>")
    return "".join(out)

# ----------------------------------------------------------------- shared text blocks
def labels_section(care_rows, comp_placeholder):
    return f"""
<h2>Labels &amp; packaging (brand supplied)</h2>
<div class="tbc"><span class="tag">TBC</span> Composition text on the care label will be updated by the brand once the final yarn / fabric composition is confirmed. Label artwork files will be sent separately. Factory quotes labels as brand-supplied (nominated supplier or shipped from Russia); confirm which in the quotation.</div>
<table>
<tr><th style="width:22%">Item</th><th style="width:38%">Specification</th><th>Placement</th></tr>
<tr><td>1 · Main woven label</td><td>Black woven satin label, white text "INFINITY STORY" + brand icon, approx. 7 × 1.5 cm, loop / end-fold. Dual-size range shown on separate size flags at each end (e.g. "XS" left, "M" right) per reference photo.</td><td>Centred at CB neck, inside, caught in neck seam (woven: under collar stand; knit: linked into neck seam).</td></tr>
<tr><td>2 · Care / composition label</td><td>White printed satin / nylon taffeta, approx. 4 × 9 cm folded (two-sided). Front: "INFINITY STORY / Infinity Story", composition in RU, EN, DE, CZ, ES, FR, IT, PL, PT, CN, TR, UA, SK. Back: care text in English + symbols + EAC mark.<br>{comp_placeholder}</td><td>Wearer's LEFT side seam, inside, 10 cm above hem edge. Loop-folded, caught in side seam / overlock.</td></tr>
<tr><td>3 · Hang tag</td><td>Brand hang tag with plastic tag pin. <span class="tag">TBC</span> artwork / size.</td><td>Attached through care label loop.</td></tr>
<tr><td>4 · Barcode / marketplace sticker</td><td>Brand supplies marketplace barcode stickers (Wildberries / Ozon format) per style-colour-size. <span class="tag">TBC</span></td><td>Outside of polybag, lower right corner, straight, fully readable.</td></tr>
<tr><td>5 · Polybag</td><td>Frosted transparent PE zip-lock bag with slider, black brand logo print in rectangular frame on front, air vent hole. Approx. 30 × 32 cm. <span class="tag">TBC</span> exact size and supplier.</td><td>One garment per bag, folded logo side up, size visible through bag. Size sticker on bag optional.</td></tr>
<tr><td>6 · Carton</td><td>5-ply export carton, max. 15 kg, marked: style / colour / size / qty / carton no. Solid-size or solid-colour packing per PO.</td><td>—</td></tr>
</table>
<h3>Care instructions (for label)</h3>
<table><tr><th style="width:30%">Symbol</th><th>Text</th></tr>{care_rows}</table>
<figure>{packaging_svg()}</figure>
"""

def signoff():
    return """
<h2>Sample &amp; approval process</h2>
<ol>
<li><b>Quotation</b> within 3 working days of receiving this pack: unit price FOB at 300 / 500 pcs per colour, MOQ per colour, sample cost and lead time.</li>
<li><b>Pre-production sample (PPS / fit sample)</b> 1 pc in sample size in available materials closest to reference. Send photos front / back / detail on dress form and flat before shipping. Sample ships with measurement chart filled in by factory QC.</li>
<li><b>Brand review</b>: measurements against tolerance table, construction, hand-feel. Comments returned within 5 working days. Second sample only if fit changes are required.</li>
<li><b>Colour approval</b>: lab-dips / yarn shade card swatches for 2 colourways approved before bulk material is ordered.</li>
<li><b>Bulk</b>: production only after written sample + colour approval. Size set (1 pc per size) photographed before bulk sewing. Inline and final inspection AQL 2.5.</li>
<li><b>Deviations</b>: any change of material, construction or measurement must be confirmed in writing by the brand before production.</li>
</ol>
<table class="kv"><tr><td>Brand contact</td><td>Infinity Story · Alena (owner) · e-mail / WeChat: <span class="tag">TBC</span></td></tr>
<tr><td>Approved by brand (name / date)</td><td>&nbsp;</td></tr>
<tr><td>Confirmed by factory (name / date / stamp)</td><td>&nbsp;</td></tr></table>
"""

BODY_TABLE = """
<table>
<tr><th class="num">RU size</th><th class="num">EU size</th><th class="num">Intl.</th><th class="num">Bust</th><th class="num">Waist</th><th class="num">Hip</th><th class="num">Height</th></tr>
<tr><td class="num">42</td><td class="num">34</td><td class="num">XS</td><td class="num">84</td><td class="num">66</td><td class="num">92</td><td class="num" rowspan="6">164–172</td></tr>
<tr><td class="num">44</td><td class="num">36</td><td class="num">S</td><td class="num">88</td><td class="num">70</td><td class="num">96</td></tr>
<tr><td class="num">46</td><td class="num">38</td><td class="num">M</td><td class="num">92</td><td class="num">74</td><td class="num">100</td></tr>
<tr><td class="num">48</td><td class="num">40</td><td class="num">L</td><td class="num">96</td><td class="num">78</td><td class="num">104</td></tr>
<tr><td class="num">50</td><td class="num">42</td><td class="num">XL</td><td class="num">100</td><td class="num">82</td><td class="num">108</td></tr>
<tr><td class="num">52</td><td class="num">44</td><td class="num">2XL</td><td class="num">104</td><td class="num">86</td><td class="num">112</td></tr>
</table>
<p class="small">Body measurements = EU standard + 1–2 cm (Russian standard grading, per brand instruction). <span class="tag">TBC</span> Brand to confirm against its own size chart.</p>
"""

# ================================================================= DOC 1: CARDIGAN
def doc_cardigan():
    care = """<tr><td>🌡 30 · hand wash</td><td>Hand wash 30 °C · Do not bleach · Do not tumble dry · Dry flat · Iron low (110 °C) with cloth · Dry clean P</td></tr>"""
    comp = 'Composition placeholder: "XX% Acrylic, XX% Nylon, 10% Wool" (final after yarn approval).'
    b = header("IS-KN-001", "TULIP INTARSIA CARDIGAN", "Knit Tech Pack (flat-knit factory)", "2 dual sizes: S1 = XS–M (RU 42–46), S2 = L–2XL (RU 48–52)", "S1 (XS–M)")
    b += f"""
<h2>1 · Style description</h2>
<div class="two"><div>
<p>Cropped, semi-relaxed fit fully-fashioned cardigan with drop shoulders. Knitted point collar and 4 cm button placket in a two-colour jacquard diamond check. All-over intarsia tulip motif on both fronts, back and sleeves. 1x1 rib hem and cuffs with two white stripes. 5 buttons.</p>
<ul>
<li><b>Fit:</b> semi-relaxed / slightly oversized, cropped to natural waist, drop shoulder, straight body.</li>
<li><b>Construction:</b> fully fashioned panels, linking on all seams (no cut-and-sew). Placket and collar knitted separately and linked on.</li>
<li><b>Motif:</b> tulips must be <u>knitted in (intarsia)</u>, clean back with no long floats. Embroidery, appliqué or print are NOT accepted.</li>
<li><b>Check placket/collar:</b> jacquard (2-colour + white) – float jacquard or ladder-back acceptable if reverse is neat; factory to reproduce the check from the reference photo and submit a swatch.</li>
<li><b>Reference:</b> photo attached (page 2). Reproduce silhouette, proportions and motif placement 1:1.</li>
</ul></div>
<div><figure><div style="height:70mm;border:1.5px dashed #999;display:flex;align-items:center;justify-content:center;color:#666;font-size:9pt;text-align:center;padding:4mm">REFERENCE PHOTO<br>ref_cardigan.jpg<br>(attached as separate image file with this pack)</div><figcaption>Reference photo (design intent)</figcaption></figure></div></div>

<div class="page"></div>
<h2>2 · Technical drawings</h2>
<figure>{cardigan_front_svg()}</figure>
<figure>{cardigan_back_svg()}</figure>

<h2>3 · Materials (BOM)</h2>
<table>
<tr><th style="width:18%">Component</th><th>Specification</th><th style="width:18%">Supplier</th><th style="width:12%">Qty / pc</th></tr>
<tr><td>Main yarn</td><td>Brushed / lightly raised blend, soft hand-feel, <b>wool content max. 10%</b> (must not be scratchy on bare skin). Proposed: 45% acrylic / 45% nylon / 10% wool, brushed; alternative 55% viscose / 35% nylon / 10% wool. Factory to propose 2 yarn options with price and hand-feel swatch. No mohair loose shedding.</td><td>Factory</td><td>approx. 420 g (S1) / 480 g (S2) <span class="tag">TBC</span></td></tr>
<tr><td>Gauge</td><td>Factory to propose (target 7 gg or 5 gg with 2-end yarn) to match reference density; garment must hold shape, not stretch out at hem/cuffs. Approve via 20 × 20 cm swatch.</td><td>Factory</td><td>—</td></tr>
<tr><td>Colours</td><td>8 colours per colourway (table 6). 2 colourways, to be selected by brand from factory yarn shade card. <span class="tag">TBC</span> Send shade card first; colour codes to be filled in and attached to this pack.</td><td>Factory</td><td>—</td></tr>
<tr><td>Buttons</td><td>5 pcs, 4-hole, approx. Ø 20 mm, natural horn / wood look. <b>Brand supplied</b>, shipped to factory before bulk. Factory to make sample with closest available button.</td><td>Brand</td><td>5 + 1 spare</td></tr>
<tr><td>Sewing thread</td><td>Linking yarn = main yarn; buttons sewn with matching polyester thread, shank wrapped.</td><td>Factory</td><td>—</td></tr>
<tr><td>Labels / packaging</td><td>See section 8.</td><td>Brand</td><td>—</td></tr>
</table>

<h2>4 · Size chart – body measurements (Russian sizing)</h2>
{BODY_TABLE}
<p>Dual-size logic: each knit size covers three body sizes. <b>S1 (XS–M)</b> is graded to fit bust 84–92, <b>S2 (L–2XL)</b> bust 96–104. Fit sample S1 to be checked on a size 44 (bust 88) fit model / form.</p>

<h2>5 · Garment measurement chart – finished, relaxed after steaming</h2>
<table>
<tr><th style="width:6%">POM</th><th>Point of measure</th><th class="num">S1 · XS–M</th><th class="num">S2 · L–2XL</th><th class="num">Tol. ±</th></tr>
<tr><td class="num">A</td><td>Body length from HPS to hem edge (incl. rib)</td><td class="num">50</td><td class="num">53</td><td class="num">1.0</td></tr>
<tr><td class="num">B</td><td>Chest width, 2 cm below underarm, half</td><td class="num">58</td><td class="num">65</td><td class="num">1.0</td></tr>
<tr><td class="num">C</td><td>Hem width at rib, relaxed, half</td><td class="num">50</td><td class="num">56</td><td class="num">1.0</td></tr>
<tr><td class="num">D</td><td>Hem rib height</td><td class="num">6</td><td class="num">6</td><td class="num">0.3</td></tr>
<tr><td class="num">E</td><td>Across shoulder, seam to seam (drop shoulder)</td><td class="num">58</td><td class="num">65</td><td class="num">1.0</td></tr>
<tr><td class="num">F</td><td>Sleeve length, shoulder seam to cuff edge</td><td class="num">45</td><td class="num">46</td><td class="num">1.0</td></tr>
<tr><td class="num">G</td><td>Upper sleeve width, 2 cm below underarm, half</td><td class="num">24</td><td class="num">26</td><td class="num">0.5</td></tr>
<tr><td class="num">H</td><td>Cuff width at rib, relaxed, half</td><td class="num">9.5</td><td class="num">10.5</td><td class="num">0.5</td></tr>
<tr><td class="num">I</td><td>Cuff rib height</td><td class="num">6</td><td class="num">6</td><td class="num">0.3</td></tr>
<tr><td class="num">J</td><td>Neck width, seam to seam at HPS</td><td class="num">21</td><td class="num">22</td><td class="num">0.5</td></tr>
<tr><td class="num">K</td><td>Front neck drop, HPS to collar seam at CF</td><td class="num">9</td><td class="num">9.5</td><td class="num">0.5</td></tr>
<tr><td class="num">L</td><td>Back neck drop, HPS to collar seam at CB</td><td class="num">2</td><td class="num">2</td><td class="num">0.3</td></tr>
<tr><td class="num">M</td><td>Collar height at CB (one-piece knitted, stand + fall)</td><td class="num">8</td><td class="num">8</td><td class="num">0.3</td></tr>
<tr><td class="num">N</td><td>Collar point length</td><td class="num">8.5</td><td class="num">8.5</td><td class="num">0.3</td></tr>
<tr><td class="num">O</td><td>Placket width, finished</td><td class="num">4</td><td class="num">4</td><td class="num">0.2</td></tr>
<tr><td class="num">P</td><td>Placket length, collar seam to hem edge</td><td class="num">41</td><td class="num">43.5</td><td class="num">0.5</td></tr>
<tr><td class="num">Q</td><td>Armhole depth, shoulder seam to underarm, straight</td><td class="num">24</td><td class="num">26</td><td class="num">0.5</td></tr>
<tr><td class="num">R</td><td>Shoulder slope (drop from HPS to shoulder seam end)</td><td class="num">2</td><td class="num">2</td><td class="num">0.3</td></tr>
<tr><td class="num">S</td><td>Buttons: 5 pcs · 1st button 1.5 cm below collar seam · spacing</td><td class="num">8.5</td><td class="num">9.0</td><td class="num">0.3</td></tr>
<tr><td class="num">T</td><td>Garment weight, g (target, after yarn approval)</td><td class="num">≈ 420</td><td class="num">≈ 480</td><td class="num">5%</td></tr>
</table>
<p class="small">Measure flat on a table, garment relaxed 24 h after steaming, ribs not stretched. Half measurements = one layer, seam to seam.</p>

<div class="page"></div>
<h2>6 · Knit panel specification (for knitting programme)</h2>
<figure>{cardigan_panels_svg()}</figure>
<table>
<tr><th style="width:16%">Panel</th><th>Knitting instruction</th></tr>
<tr><td>Body – back ×1</td><td>Start: closed tubular / 1x1 rib 6 cm with 2 white stripes (2 courses each, at 2.4 cm and 4.1 cm from bottom edge). Body single jersey (plain) with intarsia tulips ×4, motif base sits directly on top of the rib. Straight sides, no waist shaping. Straight armhole (no narrowing), start marker at 24/26 cm below shoulder. Shoulder: fashioned slope 2 cm over full shoulder width. Back neck: bind-off with 2 cm drop, width 21/22 cm.</td></tr>
<tr><td>Body – fronts ×2 (mirror)</td><td>As back, each 27 / 30.5 cm wide + linked placket. Intarsia tulips ×2 per front, mirrored. Front neck: fashioned curve from CF at 9 / 9.5 cm below HPS to shoulder.</td></tr>
<tr><td>Sleeves ×2</td><td>Start: 1x1 rib cuff 6 cm, 19/21 cm relaxed, 2 white stripes as hem. Body from 24/26 cm above cuff widening straight to 48/52 cm at top, <b>no sleeve cap</b> (straight top for drop shoulder). Intarsia tulips ×2 on outer sleeve, growing from the cuff (see front view). Fashioned edges.</td></tr>
<tr><td>Placket ×2</td><td>Jacquard check, 4 cm finished, full length 41 / 43.5 cm, both long edges finished with 2-wale white tipping. Wearer's RIGHT placket: 5 knitted horizontal buttonholes 2.2 cm, centred. Wearer's LEFT placket: buttons. Plackets fully overlap (right over left). Linked to front edges.</td></tr>
<tr><td>Collar ×1</td><td>One-piece pointed collar in jacquard check, 8 cm at CB, points 8.5 cm, neck edge 44 / 46 cm to match neckline + placket tops. Outer edge 2-course white tipping. Linked into neck seam with main label.</td></tr>
<tr><td>Finishing</td><td>All seams linked (side, sleeve, shoulder, armhole). Light steam finish, no press marks on motif. Wash test: no colour bleeding between intarsia colours (white petals must stay clean).</td></tr>
</table>

<h2>7 · Motif &amp; colour specification</h2>
<figure>{cardigan_motif_svg()}</figure>
<table>
<tr><th>Placement</th><th>Description</th></tr>
<tr><td>Front (each side)</td><td>2 tulips, mirrored, rising from hem rib, heads at approx. 16–24 cm above rib. Motif not cut by placket.</td></tr>
<tr><td>Back</td><td>4 tulips, evenly spaced across back panel, same height as front.</td></tr>
<tr><td>Sleeves</td><td>2 tulips per sleeve on outer sleeve, growing out of the cuff rib, one upright, one leaning outward (see front view).</td></tr>
<tr><td>Artwork</td><td>Factory to digitise the motif from the reference photo at the approved gauge and send the knit programme simulation (bitmap) for approval <b>before</b> knitting the sample. Petals off-white with a blush-pink centre; stem olive; leaves in olive + chartreuse.</td></tr>
</table>
<table>
<tr><th class="num">Col</th><th>Use</th><th>Reference shade</th><th class="num">Colourway 1</th><th class="num">Colourway 2</th></tr>
<tr><td class="num">A</td><td>Body ground</td><td>Dusty pink</td><td class="num">TBC</td><td class="num">TBC</td></tr>
<tr><td class="num">B</td><td>Petal main</td><td>Off-white</td><td class="num">TBC</td><td class="num">TBC</td></tr>
<tr><td class="num">C</td><td>Petal shade</td><td>Blush pink</td><td class="num">TBC</td><td class="num">TBC</td></tr>
<tr><td class="num">D</td><td>Stem, leaf 1</td><td>Olive green</td><td class="num">TBC</td><td class="num">TBC</td></tr>
<tr><td class="num">E</td><td>Leaf 2</td><td>Chartreuse / ochre green</td><td class="num">TBC</td><td class="num">TBC</td></tr>
<tr><td class="num">F</td><td>Check ground, tipping, rib stripes</td><td>White</td><td class="num">TBC</td><td class="num">TBC</td></tr>
<tr><td class="num">G</td><td>Check colour 1</td><td>Light blue</td><td class="num">TBC</td><td class="num">TBC</td></tr>
<tr><td class="num">H</td><td>Check colour 2</td><td>Green</td><td class="num">TBC</td><td class="num">TBC</td></tr>
</table>
<div class="tbc"><span class="tag">TBC</span> Colour codes will be filled in from the factory yarn shade card and this table re-issued as v1.1 together with the shade card. Sample to be knitted in the closest available shades to the reference.</div>

<div class="page"></div>
{labels_section(care, comp)}
<figure>{placement_svg()}</figure>

<h2>9 · Quality requirements</h2>
<ul>
<li>Measurements within tolerance (table 5); all 5 sizes of a size set measured and recorded.</li>
<li>Intarsia: no holes at colour changes, no floats longer than 1 cm on the reverse, ends secured and trimmed.</li>
<li>Rib: 1x1, even tension, must recover after 20% stretch; white stripes straight and continuous across seams.</li>
<li>Linking: no skipped stitches; shoulder and neck seams stabilised (tape or chain) to prevent stretching.</li>
<li>Collar and placket lie flat, no twisting; buttonholes aligned to buttons, no gaping at chest.</li>
<li>Hand-feel: soft, not scratchy; pilling test ≥ 3–4 (ISO 12945-2, 2000 rubs); no shedding.</li>
<li>Colour fastness to washing ≥ 4, no migration of pink into white petals.</li>
<li>Steamed, folded, no odour, no loose threads, metal-detector passed.</li>
</ul>
{signoff()}
"""
    return html_page("IS-KN-001 Tulip Cardigan – Knit Tech Pack", b)

# ================================================================= DOC 2: BLOUSE PATTERN BRIEF
BLOUSE_POM = [
    ("A", "Centre back length, collar seam to hem edge", "60", "1.0"),
    ("A2", "Front length, HPS to hem edge", "62", "1.0"),
    ("B", "Chest width, 2.5 cm below underarm, half", "52", "1.0"),
    ("C", "Waist width at 40 cm from HPS, half (straight body)", "52", "1.0"),
    ("D", "Hem width, half", "53", "1.0"),
    ("E", "Neck width at collar seam, HPS to HPS", "18", "0.5"),
    ("F", "Front neck drop, HPS to collar seam at CF", "8", "0.5"),
    ("G", "Back neck drop, HPS to collar seam at CB", "2", "0.3"),
    ("H", "Collar stand height, finished", "2", "0.2"),
    ("I", "Collar ruffle width, finished (above stand)", "2.5", "0.3"),
    ("J", "Underarm depth, HPS to underarm point (straight)", "25", "0.5"),
    ("K", "Cut-on sleeve: HPS along shoulder line to sleeve hem edge", "27", "0.7"),
    ("K2", "of which natural shoulder length (HPS to shoulder point)", "12", "0.5"),
    ("K3", "of which sleeve length beyond shoulder point", "15", "0.5"),
    ("L", "Sleeve hem opening, straight, half", "18", "0.5"),
    ("M", "Sleeve ruffle width, finished", "5", "0.3"),
    ("N", "Shoulder slope, HPS to shoulder point drop", "4", "0.3"),
    ("O", "Placket width, finished", "2.5", "0.2"),
    ("P", "Placket length, collar seam to bottom", "27", "0.5"),
    ("Q", "Bib length at CF, collar seam to bottom point", "30", "0.5"),
    ("R", "Bib width at widest, piping edge to piping edge", "22", "0.5"),
    ("S", "Bib ruffle width, finished", "3.5", "0.3"),
    ("T", "Piping, finished width (flat, no cord)", "0.4", "0.1"),
    ("U", "Buttons: 7 pcs · first 1.5 cm below collar seam · spacing", "3.8", "0.2"),
    ("V", "Hem depth, finished (double fold)", "1", "0.2"),
]

def pom_table(cols=("XS–S",)):
    rows = "".join(f'<tr><td class="num">{a}</td><td>{b}</td><td class="num">{c}</td><td class="num">{d}</td></tr>' for a, b, c, d in BLOUSE_POM)
    return f"""<table><tr><th style="width:6%">POM</th><th>Point of measure</th><th class="num">XS–S (RU 42–44)</th><th class="num">Tol. ±</th></tr>{rows}</table>"""

def doc_blouse_pattern():
    b = header("IS-WV-002", "FLORAL RUFFLE-BIB BLOUSE", "Pattern Brief (for pattern maker)", "Base size XS–S (RU 42–44); grading M–L / XL–2XL later", "XS–S, PDF pattern, 1:1")
    b += f"""
<h2>1 · Brief</h2>
<div class="two"><div>
<p>Develop a production-ready base pattern in size <b>XS–S (RU 42–44)</b> for a semi-relaxed short-sleeve blouse in printed woven fabric. Cut-on (grown-on) short sleeves, 2 cm stand collar with a single ruffle, front inset bib with self-fabric piping and a ruffled 7-button placket. Straight hem, 60 cm at centre back. Overlock construction.</p>
<p><b>Deliverables:</b></p>
<ul>
<li>PDF pattern 1:1, A4 tiled with registration marks <u>and</u> A0 sheet; both with seam allowances included and marked; piece name, size, grain, qty, notches, fold lines on every piece.</li>
<li>Pattern piece list with cut quantities and fusing plan (table 6).</li>
<li>Pattern measurements checked against table 4; report any point the pattern cannot meet.</li>
<li>Optional: DXF (AAMA) export for grading later.</li>
</ul>
<p><b>Fit target:</b> bust 84–88, waist 66–70, hip 92–96, height 164–172. Ease at chest approx. +16–20 cm, straight body, no darts, no waist shaping. Pull-over with placket buttoned open is not required: garment opens fully at placket to bib bottom; neck opening with placket unbuttoned must pass over head (≥ 60 cm opening circumference).</p>
</div><div><figure><div style="height:70mm;border:1.5px dashed #999;display:flex;align-items:center;justify-content:center;color:#666;font-size:9pt;text-align:center;padding:4mm">REFERENCE PHOTO<br>ref_blouse.jpg<br>(attached as separate image file with this pack)</div><figcaption>Reference photo (design intent). Note: reference has contrast piping; brand chose <b>self-fabric</b> piping.</figcaption></figure></div></div>

<div class="page"></div>
<h2>2 · Technical drawings</h2>
<figure>{blouse_front_svg()}</figure>
<figure>{blouse_back_svg()}</figure>

<h2>3 · Body measurements – Russian sizing</h2>
{BODY_TABLE}

<h2>4 · Finished garment measurements – base size</h2>
{pom_table()}
<p class="small">All measurements flat, garment buttoned, ruffles excluded unless stated. Pattern to be drafted so the sewn garment meets these figures with the seam allowances of table 5.</p>

<h2>5 · Construction notes for the pattern</h2>
<table>
<tr><th style="width:22%">Area</th><th>Instruction</th></tr>
<tr><td>Front body</td><td>Cut ×2 (mirror). CF opening from collar seam to bib bottom (27 cm placket). Bib shape removed from the front as an inset (recommended) so the bib seam carries piping and lies flat; alternative appliqué bib only if the fabric proves too light for an inset seam – pattern maker to advise. Below the bib the two fronts are joined at CF (seam or CF on fold below the bib – pattern maker's choice, mark on pattern).</td></tr>
<tr><td>Back body</td><td>Cut ×1 on fold at CB. No darts, no yoke, no CB seam.</td></tr>
<tr><td>Cut-on sleeve</td><td>Shoulder line extended 15 cm beyond shoulder point, sleeve angle approx. 20° below horizontal so the sleeve hangs without pulling; slight over-sleeve shaping allowed. Sleeve hem straight, 18 cm half opening. Underarm curve smooth into side seam at 25 cm below HPS; add 1 cm gusset-free ease in underarm curve for movement.</td></tr>
<tr><td>Bib panel</td><td>Cut ×2 (mirror), pointed oval, 30 cm at CF, 22 cm widest at 10–12 cm below collar seam, inner edge = placket seam line. Grain: straight grain parallel to CF.</td></tr>
<tr><td>Placket</td><td>Two-piece placket, each 2.5 cm finished, folded band (cut 2× width + SA), both outer edges piped. Wearer's right = buttonhole side, over wearer's left = button side, full overlap 2.5 cm. Bottom of placket closed and enclosed inside the bib seam / point.</td></tr>
<tr><td>Ruffles</td><td>All single-layer, straight grain, gathering ratio 1:2, finished widths: collar 2.5, bib/placket 3.5, sleeve 5. Add 0.7 cm SA on attachment edge and 0.6 cm for narrow rolled hem on free edge. Bib ruffle inserted into placket seam (between placket and bib), running full placket length and meeting at the bib point.</td></tr>
<tr><td>Collar</td><td>Stand collar 2 cm finished, front ends straight (no button on stand), CB on fold. Cut outer + inner stand; ruffle and piping in top edge seam. Neck edge length = neckline of body (approx. 40 cm) + 2 × placket width at CF.</td></tr>
<tr><td>Piping</td><td>Flat self-fabric piping, 0.4 cm finished, no cord; bias strip 2.2 cm. Applied in: bib inset seam, both placket edges, collar top edge.</td></tr>
<tr><td>Hem</td><td>Straight, 1 cm finished double fold (cut 2 cm allowance).</td></tr>
</table>

<h3>Seam allowances to include in the pattern</h3>
<table>
<tr><th>Seam</th><th class="num">SA, cm</th><th>Finish</th></tr>
<tr><td>Shoulder / over-sleeve, side / underarm</td><td class="num">1.0</td><td>4-thread overlock, pressed to back</td></tr>
<tr><td>Bib inset seam, placket seams, collar to neck</td><td class="num">1.0</td><td>Overlock 3-thread after seaming / enclosed</td></tr>
<tr><td>Collar top edge, placket band fold edges</td><td class="num">0.7</td><td>Enclosed</td></tr>
<tr><td>Ruffle attachment edge</td><td class="num">0.7</td><td>Caught in seam</td></tr>
<tr><td>Ruffle free edge, sleeve hem ruffle join</td><td class="num">0.6</td><td>Rolled hem (3-thread) / overlock</td></tr>
<tr><td>Hem</td><td class="num">2.0</td><td>1 cm double fold, edge-stitch 0.1</td></tr>
</table>

<h2>6 · Pattern piece list</h2>
<figure>{pattern_pieces_svg()}</figure>
<table>
<tr><th class="num">#</th><th>Piece</th><th class="num">Cut</th><th>Grain</th><th>Fusing</th></tr>
<tr><td class="num">1</td><td>Front with cut-on sleeve</td><td class="num">2 (mirror)</td><td>Straight, parallel CF</td><td>—</td></tr>
<tr><td class="num">2</td><td>Back with cut-on sleeve</td><td class="num">1 on fold</td><td>Straight, CB fold</td><td>—</td></tr>
<tr><td class="num">3</td><td>Bib panel</td><td class="num">2 (mirror)</td><td>Straight</td><td>Optional light fuse if fabric &lt; 120 g/m²</td></tr>
<tr><td class="num">4</td><td>Placket band</td><td class="num">2 (1 BH side, 1 button side)</td><td>Straight</td><td>Full fuse, light woven 40 g/m²</td></tr>
<tr><td class="num">5</td><td>Collar stand outer / inner</td><td class="num">1 + 1 on fold</td><td>Straight</td><td>Outer fused</td></tr>
<tr><td class="num">6</td><td>Collar ruffle</td><td class="num">1</td><td>Straight</td><td>—</td></tr>
<tr><td class="num">7</td><td>Bib / placket ruffle</td><td class="num">2</td><td>Straight</td><td>—</td></tr>
<tr><td class="num">8</td><td>Sleeve ruffle</td><td class="num">2</td><td>Straight</td><td>—</td></tr>
<tr><td class="num">9</td><td>Piping bias strip 2.2 cm</td><td class="num">approx. 2.3 m joined</td><td>True bias 45°</td><td>—</td></tr>
</table>
<p class="small">Add notches: sleeve hem ruffle quarter points, bib widest point, placket bottom, collar CB and shoulder match points, gather start/stop.</p>

<h2>7 · Fabric information for the pattern maker</h2>
<p>Printed viscose / cotton-viscose jacquard, approx. 130–150 g/m², width 140–145 cm, non-stretch, <b>brand supplied</b>. Directional floral print: mark pattern pieces "one-way" and note print matching is not required, but avoid cutting a large flower head on the bib centre. Pre-wash shrinkage to be tested by brand and reported; pattern to include shrinkage allowance if &gt; 2%. <span class="tag">TBC</span> Final fabric to be confirmed before grading.</p>
<p><b>Toile:</b> first fit in a mock-up (calico or similar-weight fabric) on a size 44 form; photos front / back / side + measurement check before releasing the PDF.</p>
"""
    return html_page("IS-WV-002 Floral Blouse – Pattern Brief", b)

# ================================================================= DOC 3: BLOUSE PRODUCTION
def doc_blouse_production():
    care = """<tr><td>30 · gentle</td><td>Machine wash 30 °C gentle cycle · Do not bleach · Do not tumble dry · Iron low (110 °C) on reverse · Dry clean P · Wash inside out</td></tr>"""
    comp = 'Composition placeholder: "XX% Viscose, XX% Cotton" (final after fabric confirmation).'
    b = header("IS-WV-002", "FLORAL RUFFLE-BIB BLOUSE", "Production Tech Pack (sewing factory)", "XS–S (RU 42–44) sample; full range M–L, XL–2XL after fit approval", "XS–S", extra=[("Pattern", "Supplied by brand: PDF 1:1 (A0 + A4 tiled), size XS–S")])
    b += f"""
<h2>1 · Style description</h2>
<div class="two"><div>
<p>Semi-relaxed short-sleeve blouse in printed woven fabric. Cut-on (grown-on) sleeves finished with a 5 cm self ruffle. 2 cm stand collar with a single 2.5 cm ruffle and self piping. Front inset bib outlined with self-fabric flat piping; 2.5 cm piped button placket with a 3.5 cm gathered ruffle on each side; 7 gold shank buttons. Straight hem 60 cm at CB. Overlock construction.</p>
<ul>
<li><b>Fabric:</b> supplied by brand (printed viscose / cotton-viscose jacquard). Factory supplies interlining, thread, packing materials.</li>
<li><b>Pattern:</b> supplied by brand in PDF 1:1 – print on A0 or tile A4, verify 10 cm test square before cutting.</li>
<li><b>Buttons:</b> supplied by brand.</li>
<li><b>Sample:</b> 1 pc XS–S in bulk fabric (brand ships 2.5 m) with all trims.</li>
</ul></div>
<div><figure><div style="height:70mm;border:1.5px dashed #999;display:flex;align-items:center;justify-content:center;color:#666;font-size:9pt;text-align:center;padding:4mm">REFERENCE PHOTO<br>ref_blouse.jpg<br>(attached as separate image file with this pack)</div><figcaption>Reference photo. Reference shows contrast piping; production uses <b>self-fabric</b> piping.</figcaption></figure></div></div>

<div class="page"></div>
<h2>2 · Technical drawings</h2>
<figure>{blouse_front_svg()}</figure>
<figure>{blouse_back_svg()}</figure>
<h2>3 · Detail drawings</h2>
<figure>{bib_detail_svg()}</figure>
<figure>{collar_detail_svg()}</figure>

<h2>4 · Bill of materials</h2>
<table>
<tr><th style="width:18%">Component</th><th>Specification</th><th style="width:14%">Supplier</th><th style="width:16%">Consumption / pc</th></tr>
<tr><td>Shell fabric</td><td>Printed viscose / cotton-viscose jacquard, approx. 130–150 g/m², 140–145 cm wide, floral print on cream ground. <span class="tag">TBC</span> final article.</td><td>Brand</td><td>approx. 1.7 m (XS–S, incl. ruffles + bias) – factory to confirm marker yield</td></tr>
<tr><td>Interlining</td><td>Light woven fusible, 40 g/m², white, low-temp (viscose safe). Collar outer stand, both placket bands.</td><td>Factory</td><td>0.15 m</td></tr>
<tr><td>Sewing thread</td><td>100% polyester spun 40/2 (Tex 27), colour matched to cream ground; overlock thread same colour.</td><td>Factory</td><td>—</td></tr>
<tr><td>Buttons</td><td>7 pcs gold-tone metal shank buttons, domed / textured, Ø 15 mm.</td><td>Brand</td><td>7 + 1 spare (sewn inside at care label)</td></tr>
<tr><td>Labels, hang tag, polybag, barcode</td><td>See section 7.</td><td>Brand</td><td>1 set</td></tr>
</table>

<h2>5 · Finished garment measurements</h2>
{pom_table()}
<p class="small">Measure flat on table, buttoned, after final pressing. Ruffles excluded from body measurements. Grading rules for M–L and XL–2XL will follow with the graded pattern (chest +8 cm per dual size, length +2 cm).</p>

<h2>6 · Sewing construction sequence</h2>
<table>
<tr><th class="num">Op</th><th>Operation</th><th style="width:30%">Machine / stitch / SA</th></tr>
<tr><td class="num">1</td><td>Cut per marker, one-way. Fuse collar outer stand and both placket bands. Cut bias strips 2.2 cm, join on straight grain, press.</td><td>Fusing press, viscose-safe temperature (test on scrap first)</td></tr>
<tr><td class="num">2</td><td>Prepare flat piping: fold bias strip in half, press; finished 0.4 cm visible. Approx. 2.3 m per piece.</td><td>—</td></tr>
<tr><td class="num">3</td><td>Prepare ruffles (collar ×1, bib ×2, sleeve ×2): narrow rolled hem on free edge; two rows of gathering stitch at 0.5 / 0.9 cm; gather to 1:2 evenly, no pleating.</td><td>3-thread rolled hem overlock; lockstitch 4 spi gathering</td></tr>
<tr><td class="num">4</td><td>Placket bands: attach piping to both long edges of each band; fold band, press. Attach bib ruffle to inner edge of each band (ruffle between band and bib), then join band + ruffle unit to bib panel. Press seam toward bib; edge-stitch 0.1 on bib side to hold ruffle down.</td><td>Lockstitch 12 spi, SA 1.0 / 0.7, zipper foot for piping</td></tr>
<tr><td class="num">5</td><td>Attach piping to outer edge of assembled bib. Set bib into front cut-out (inset seam), matching notches; clip curves. Overlock seam allowance together, press toward body, stitch-in-ditch beside piping to keep flat. Close CF below bib.</td><td>Lockstitch SA 1.0; 3-thread overlock</td></tr>
<tr><td class="num">6</td><td>Shoulder / over-sleeve seams: front to back, one continuous seam from neck to sleeve hem. Overlock, press to back.</td><td>4-thread overlock / lockstitch + overlock, SA 1.0</td></tr>
<tr><td class="num">7</td><td>Sleeve ruffles: join ruffle ends, attach to sleeve hem right sides together, gather even; overlock SA, press toward body, edge-stitch 0.1 on body.</td><td>Lockstitch SA 0.7 + 3-thread overlock</td></tr>
<tr><td class="num">8</td><td>Side / underarm seams in one pass, matching sleeve ruffle seam and hem. Insert care label at wearer's left side seam 10 cm above hem. Overlock, press to back.</td><td>4-thread overlock, SA 1.0</td></tr>
<tr><td class="num">9</td><td>Collar: piping + collar ruffle sandwiched between outer (fused) and inner stand along top edge; stitch, trim, turn, press. Attach outer stand to neckline with main label at CB; turn inner stand in, edge-stitch 0.1 all round.</td><td>Lockstitch 12 spi, SA 1.0 / 0.7</td></tr>
<tr><td class="num">10</td><td>Hem: 1 cm double-fold, edge-stitch 0.1, seam allowances turned toward back.</td><td>Lockstitch 12 spi</td></tr>
<tr><td class="num">11</td><td>Buttonholes ×7 on wearer's right placket, vertical, 1.7 cm, centred, first 1.5 cm below collar seam, spacing 3.8 cm. Buttons ×7 on left placket, shank sewn with thread shank wrap. Spare button inside at care label.</td><td>Buttonhole machine, button-sew</td></tr>
<tr><td class="num">12</td><td>Trim threads, final press (low temperature, reverse side, ruffles steamed not flattened), QC, fold, polybag with barcode sticker.</td><td>—</td></tr>
</table>
<p class="small">Stitch density 12 spi lockstitch, 14 spi overlock. Needle size 70/10 (SES) to avoid pulled threads in viscose. No topstitching except 0.1 edge-stitches listed.</p>

<div class="page"></div>
{labels_section(care, comp)}
<figure>{blouse_placement_svg()}</figure>

<h2>8 · Quality requirements &amp; QC points</h2>
<ul>
<li>Measurements within tolerance (section 5). Both fronts identical: bib and ruffle mirror symmetrically; check at CF – max. difference 0.3 cm.</li>
<li>Ruffles evenly gathered, no flat or bunched sections; gathers steamed, not pressed flat.</li>
<li>Piping uniform 0.4 cm, no wobble; corners at bib point neat and mitred.</li>
<li>Collar stand sits flat, ends level at CF, no twist.</li>
<li>Buttonholes clean, matched to buttons, no gaping between buttons when worn.</li>
<li>Print: no visible flaws, no large flower head cut through at bib centre; one-way direction on all pieces.</li>
<li>Seams: no puckering, no pulled threads (needle 70/10), all overlock ends secured.</li>
<li>Pressing: no shine, no crushed ruffles; garment free of odour, threads, marks; metal detection passed.</li>
<li>Inspection AQL 2.5 major / 4.0 minor; size set and 3 pcs from bulk photographed before shipment.</li>
</ul>
{signoff()}
"""
    return html_page("IS-WV-002 Floral Blouse – Production Tech Pack", b)

# ================================================================= write
docs = {
    "IS-KN-001_Tulip-Cardigan_Knit-Tech-Pack.html": doc_cardigan(),
    "IS-WV-002_Floral-Blouse_Pattern-Brief.html": doc_blouse_pattern(),
    "IS-WV-002_Floral-Blouse_Production-Tech-Pack.html": doc_blouse_production(),
}
for name, content in docs.items():
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", name)
