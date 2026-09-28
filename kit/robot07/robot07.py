"""Robot v07: redrawn at ~1.3x (head 19x14, body 13x9, 3px legs, 2px arms, 3x3 mittens; ~28px tall + antenna).
8 facings (front, qr, r, br, back, bl, l, ql) so turns never snap; screen-eyes with 7 shapes; broom held in both mittens;
part-wise coloured outlines + a darker exterior silhouette; optional backlit rim. Authored in the original room coords,
saved into the 448x288 world (albedo / emit / shadow per drawing)."""
from PIL import Image
import os
OUT = os.path.dirname(os.path.abspath(__file__)) + "/frames/"
os.makedirs(OUT, exist_ok=True)
W, H = 448, 288
OX, OY = 56, 26
C = dict(
  W="#fffdf2", w="#f3eada", g="#d8cab4", G="#a8927a", GG="#6e5a4c",
  P="#f7a47e", p="#d8704f", q="#b0503a", Q="#7e3322",
  s0="#0c0814", s1="#15101f", s2="#1d1c34", s3="#3a4070", s4="#57609a",
  eh="#fdf0d8", ec="#ffffff", el="#fcc794", ed="#8a6a58",
  au="#f0a830", aU="#ffd24a", b1="#fc773a", b2="#fed6b2", b3="#b0503a", bo="#6a3a2a",
  led="#e46e4a", ledo="#5a2a22",
  h5="#e0a462", h4="#c9824a", h3="#ad6436",
  k4="#c2604a", k3="#9c3c3e",
  t5="#ecca84", t4="#d2a664", t3="#b28248", t2="#8e5e32",
)
OUTL = dict(white="#3e2833", peach="#46181a", wood="#2e1410", straw="#43261c", bind="#2a0c1c", gold="#40240e")
DIRS = ["front", "qr", "r", "br", "back", "bl", "l", "ql"]

class Part:
    def __init__(s, mat): s.mat = mat; s.px = {}
    def set(s, x, y, c): s.px[(x, y)] = C.get(c, c)
    def rect(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.set(x, y, c)
    def shift(s, dx, dy):
        p = Part(s.mat); p.px = {(x + dx, y + dy): c for (x, y), c in s.px.items()}; return p
    def shear(s, pivot_y, t):
        p = Part(s.mat); p.px = {(x + (t if y <= pivot_y else 0), y): c for (x, y), c in s.px.items()}; return p
    def mirror(s, w):
        p = Part(s.mat); p.px = {(w - 1 - x, y): c for (x, y), c in s.px.items()}; return p

def line(x0, y0, x1, y1):
    pts = []; dx = abs(x1 - x0); dy = -abs(y1 - y0); sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1; e = dx + dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1: break
        e2 = 2 * e
        if e2 >= dy: e += dy; x0 += sx
        if e2 <= dx: e += dx; y0 += sy
    return pts

def hexrgb(c): return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))

class Frame:
    def __init__(s): s.a = {}; s.e = {}; s.sh = set(); s.fx = {}
    def add(s, part, outline=True):
        if outline and part.mat in OUTL:
            oc = OUTL[part.mat]
            for (x, y) in part.px:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (x + dx, y + dy)
                    if q not in part.px: s.a[q] = oc
        s.a.update(part.px)
    def emit(s, x, y, c): s.e[(x, y)] = C.get(c, c)
    def silhouette(s):
        out = {}
        for (x, y), c in s.a.items():
            if any((x + dx, y + dy) not in s.a for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                r, g, b = hexrgb(c); k = 0.55
                out[(x, y)] = "#%02x%02x%02x" % (int(r * (1 - k) + 28 * k), int(g * (1 - k) + 10 * k), int(b * (1 - k) + 22 * k))
        s.a.update(out)
    def save(s, name):
        s.silhouette()
        for q, c in s.fx.items(): s.a.setdefault(q, c)
        for suf, d in (("a", s.a), ("e", s.e)):
            im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            for (x, y), c in d.items():
                x += OX; y += OY
                if 0 <= x < W and 0 <= y < H: im.putpixel((x, y), hexrgb(c) + (255,))
            im.save(OUT + f"{name}_{suf}.png")
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for (x, y) in s.sh:
            x += OX; y += OY
            if 0 <= x < W and 0 <= y < H: im.putpixel((x, y), (0, 0, 0, 255))
        im.save(OUT + f"{name}_s.png")

# ---------------------------------------------------------------- head (19 x 14)
HW, HH = 19, 14
HEAD_ROWS = {0: (3, 15), 1: (1, 17), 12: (1, 17), 13: (3, 15)}
def head_mask():
    for y in range(HH):
        a, b = HEAD_ROWS.get(y, (0, 18))
        for x in range(a, b + 1): yield x, y

def _screen(h, sx, sy, sw, shh=8):
    for y in range(shh):
        for x in range(sw):
            c = "s1"
            if y == 0: c = "s2"
            if y == shh - 1: c = "s0"
            if (x == 0 or x == sw - 1) and (y == 0 or y == shh - 1): continue      # rounded screen corners
            h.set(sx + x, sy + y, c)
    h.set(sx + 1, sy + 1, "s4"); h.set(sx + 2, sy + 1, "s3"); h.set(sx + 1, sy + 2, "s3")      # glass glint

def _bolt(h, x, y, lit=True):
    h.rect(x, y, x + 1, y + 3, "p" if lit else "q"); h.set(x, y, "P" if lit else "p"); h.set(x + 1, y + 3, "q" if lit else "Q")

def head_side():
    """profile head: 15 deep (narrower than the 19-wide front), placed at +2 so it stays centred on the body"""
    h = Part("white"); ears = Part("peach")
    rows = {0: (3, 11), 1: (1, 13), 12: (1, 13), 13: (3, 11)}
    for y in range(HH):
        a, b = rows.get(y, (0, 14))
        for x in range(a, b + 1): h.set(x, y, "w")
    for x in range(3, 12): h.set(x, 0, "W")
    for x in range(1, 10): h.set(x, 1, "W")
    for y in range(2, 11): h.set(0, y, "W")
    for x in range(1, 14): h.set(x, 12, "g")
    for x in range(3, 12): h.set(x, 13, "G")
    for y in range(2, 12): h.set(14, y, "g")
    h.set(13, 1, "g"); h.set(14, 11, "G")
    _bolt(h, 5, 5); h.set(7, 6, "p"); h.set(7, 7, "q")            # ear bolt with its washer
    h.rect(12, 4, 13, 9, "s1"); h.set(12, 4, "s3"); h.set(13, 4, "s2"); h.set(12, 9, "s0"); h.set(13, 9, "s0")
    for y in range(3, 11): h.set(11, y, "g")                     # bevel where the side meets the screen frame
    return h.shift(2, 0), ears, (14, 3, 2)

def head(face):
    """-> (head part, ears part, screen (sx, sy, w) or None) in head-local coords"""
    mir = face in ("ql", "l", "bl")
    base = {"ql": "qr", "l": "r", "bl": "br"}.get(face, face)
    if base == "r":
        h, ears, scr = head_side()
        if mir:
            h = h.mirror(HW)
            for x in range(5, 14): h.set(x, 0, "W")
            for x in range(7, 15): h.set(x, 1, "W")
            for y in range(2, 11): h.set(2, y, "W")
            h.set(16, 3, "w"); h.set(16, 11, "g")
            for y in range(4, 11):
                if h.px.get((16, y)) == C["W"]: h.set(16, y, "g")
            scr = (HW - scr[0] - scr[2], scr[1], scr[2])
        return h, ears, scr
    h = Part("white"); ears = Part("peach")
    for x, y in head_mask(): h.set(x, y, "w")
    for x in range(3, 16): h.set(x, 0, "W")
    for x in range(1, 13): h.set(x, 1, "W")
    for y in range(2, 11): h.set(0, y, "W")
    for x in range(1, 18): h.set(x, 12, "g")
    for x in range(3, 16): h.set(x, 13, "G")
    scr = None
    if base == "front":
        for y in range(2, 12): h.set(17, y, "g"); h.set(18, y, "g")
        h.set(18, 11, "G"); h.set(17, 12, "G"); h.set(16, 1, "g"); h.set(17, 1, "g")
        scr = (3, 3, 13)
        ears.rect(-2, 5, -1, 8, "p"); ears.set(-2, 5, "P"); ears.set(-1, 5, "P"); ears.set(-2, 8, "q")
        ears.rect(19, 5, 20, 8, "q"); ears.set(19, 5, "p"); ears.set(20, 8, "Q")
    elif base == "qr":                                         # face turned to viewer's right; side plane on the left
        for y in range(2, 12): h.set(18, y, "g")
        h.set(18, 11, "G"); h.set(17, 12, "G")
        for y in range(2, 12): h.set(4, y, "g")                # crease
        for y in range(2, 11): h.set(1, y, "W")
        _bolt(h, 1, 5)
        scr = (6, 3, 11)
        ears.rect(19, 6, 19, 8, "q"); ears.set(19, 8, "Q")
    elif base == "r":                                          # profile, facing right: whole side plane + front edge sliver
        for y in range(2, 12): h.set(17, y, "g"); h.set(18, y, "G")
        _bolt(h, 7, 5); h.set(9, 6, "p"); h.set(9, 7, "q")
        h.rect(15, 4, 16, 9, "s1"); h.set(15, 4, "s3"); h.set(16, 9, "s0")      # the screen seen edge-on
        scr = (15, 3, 2)
    elif base == "br":                                         # back three-quarter, facing up-right: back + left side plane... mirrored below
        for y in range(2, 12): h.set(17, y, "g"); h.set(18, y, "g")
        h.rect(15, 4, 16, 9, "G")                               # side plane in shade toward the face
        _bolt(h, 12, 5, lit=False)
        h.rect(3, 3, 9, 8, "g"); h.set(3, 3, "w"); h.set(9, 3, "w"); h.set(3, 8, "w"); h.set(9, 8, "w")
        for x in (4, 6, 8): h.rect(x, 4, x, 7, "G")
        ears.rect(-2, 5, -1, 8, "p"); ears.set(-2, 5, "P")
    else:                                                      # back
        for y in range(2, 12): h.set(17, y, "g"); h.set(18, y, "g")
        h.rect(5, 3, 13, 8, "g"); h.set(5, 3, "w"); h.set(13, 3, "w"); h.set(5, 8, "w"); h.set(13, 8, "w")
        for x in (6, 8, 10, 12): h.rect(x, 4, x, 7, "G")
        h.set(2, 10, "G"); h.set(16, 10, "G")
        ears.rect(-2, 5, -1, 8, "p"); ears.set(-2, 5, "P"); ears.set(-1, 5, "P")
        ears.rect(19, 5, 20, 8, "q"); ears.set(20, 8, "Q")
    if scr and base != "r":
        _screen(h, *scr)
    if mir:                                                    # mirror: keep light from the upper-left (re-shade the edges)
        h = h.mirror(HW); ears = ears.mirror(HW)
        for x in range(3, 16): h.set(x, 0, "W")
        for x in range(6, 18): h.set(x, 1, "W")
        for y in range(2, 11):
            if h.px.get((0, y)) in (C["g"], C["G"]): h.set(0, y, "w")
        if scr: scr = (HW - scr[0] - scr[2], scr[1], scr[2])
    return h, ears, scr

def eyes(shape, dx, dy, sw):
    """eye pixels in screen-local coords for a screen sw wide (8 tall)"""
    if sw <= 3:                                                # profile: one eye glowing on the edge-on screen
        if shape in ("blink", "off"): return [] if shape == "off" else [(0, 4, "el")]
        top = {"wide": 2, "open": 3, "soft": 4, "happy": 4, "squint": 4, "dim": 3}.get(shape, 3)
        return [(0, y, "eh" if y > top else "ec") for y in range(top, 6)]
    out = []
    ax = {"L": sw // 2 - 3, "R": sw // 2 + 2}
    for side in ("L", "R"):
        x, y = ax[side] + dx, 2 + dy
        if shape == "open":   out += [(x, y, "ec"), (x + 1, y, "eh"), (x, y + 1, "eh"), (x + 1, y + 1, "eh"), (x, y + 2, "eh"), (x + 1, y + 2, "el")]
        elif shape == "dim":  out += [(x, y + 1, "ed"), (x + 1, y + 1, "ed"), (x, y + 2, "ed"), (x + 1, y + 2, "ed")]
        elif shape == "blink": out += [(x - (side == "L"), y + 2, "el"), (x, y + 2, "eh"), (x + 1, y + 2, "eh"), (x + 1 + (side == "R"), y + 2, "el")]
        elif shape == "wide": out += [(x, y - 1, "ec"), (x + 1, y - 1, "eh"), (x, y, "eh"), (x + 1, y, "eh"), (x, y + 1, "eh"), (x + 1, y + 1, "eh"), (x, y + 2, "eh"), (x + 1, y + 2, "el")]
        elif shape == "soft": out += [(x, y + 1, "eh"), (x + 1, y + 1, "eh"), (x, y + 2, "eh"), (x + 1, y + 2, "el"), ((x + 1, y, "el") if side == "L" else (x, y, "el"))]
        elif shape == "happy":
            b = x - 1
            out += [(b, y + 2, "eh"), (b + 1, y + 1, "ec"), (b + 2, y + 1, "ec"), (b + 3, y + 2, "eh")]
        elif shape == "squint":
            if side == "L": out += [(x, y + 1, "eh"), (x + 1, y + 1, "eh"), (x, y + 2, "eh"), (x + 1, y + 2, "eh"), (x + 1, y, "el")]
            else: out += [(x, y + 1, "eh"), (x + 1, y + 1, "eh"), (x, y + 2, "eh"), (x + 1, y + 2, "eh"), (x, y, "el")]
    return out

# ---------------------------------------------------------------- body (13 x 9)
BW, BHt = 13, 9
def body(face):
    mir = face in ("ql", "l", "bl"); base = {"ql": "qr", "l": "r", "bl": "br"}.get(face, face)
    b = Part("peach")
    for y in range(BHt):
        a, c = (1, 11) if y in (0, BHt - 1) else (0, 12)
        for x in range(a, c + 1): b.set(x, y, "p")
    for x in range(1, 12): b.set(x, 0, "P")
    for y in range(1, 7): b.set(0, y, "P")
    b.set(1, 1, "P")
    for y in range(1, 8): b.set(11, y, "q"); b.set(12, y, "q")
    for x in range(1, 12): b.set(x, 6, "q"); b.set(x, 7, "p"); b.set(x, 8, "Q")     # waist band, hem
    b.set(0, 7, "p"); b.set(12, 7, "Q"); b.set(12, 6, "Q")
    panel = None
    if base in ("front", "qr"):
        px = 4 if base == "front" else 6
        panel = Part("white")
        panel.rect(px, 1, px + 4, 4, "w"); panel.rect(px, 1, px + 4, 1, "W"); panel.set(px, 2, "W")
        panel.rect(px, 4, px + 4, 4, "g"); panel.set(px + 4, 2, "g"); panel.set(px + 4, 3, "g")
        panel.set(px + 2, 2, "led"); panel.set(px + 3, 3, "ledo")
        if base == "qr":
            for y in range(1, 6): b.set(1, y, "P"); b.set(2, y, "p")
    elif base == "r":                                        # profile body: 10 deep, centred
        b = Part("peach")
        for y in range(BHt):
            a, c = (2, 10) if y in (0, BHt - 1) else (1, 11)
            for x in range(a, c + 1): b.set(x, y, "p")
        for x in range(2, 11): b.set(x, 0, "P")
        for y in range(1, 7): b.set(1, y, "P")
        for y in range(1, 8): b.set(10, y, "q"); b.set(11, y, "q")
        for x in range(2, 11): b.set(x, 6, "q"); b.set(x, 7, "p"); b.set(x, 8, "Q")
        b.rect(4, 2, 6, 4, "q"); b.set(4, 2, "p"); b.set(5, 2, "p"); b.set(6, 4, "Q")          # side hatch
    else:                                                    # back / br
        px = 4 if base == "back" else 2
        b.rect(px, 1, px + 4, 4, "q"); b.set(px, 1, "p"); b.set(px + 4, 4, "Q")
        for x in range(px + 1, px + 4, 2): b.set(x, 2, "Q"); b.set(x, 3, "Q")
    if mir:
        b = b.mirror(BW); panel = panel.mirror(BW) if panel else None
        for x in range(1, 12): b.set(x, 0, "P")
        for y in range(1, 6):
            if b.px.get((0, y)) == C["q"]: b.set(0, y, "p")
    return b, panel

# ---------------------------------------------------------------- legs (4 rows, 3px wide) + feet (5x2)
def legs(kind, x0, top, by, face, lean=0):
    lg = Part("peach"); ft = Part("white")
    Lx, Rx = x0 + 2, x0 + 8
    side = face in ("l", "r")
    fl, fr = (x0 + 1, x0 + 5), (x0 + 7, x0 + 11)
    if side:
        s = -1 if face == "l" else 1
        Lx, Rx = x0 + 3, x0 + 7; fl, fr = (x0 + 2 + s, x0 + 6 + s), (x0 + 6 + s, x0 + 10 + s)
    if kind in ("wide", "crouch"): fl, fr = (fl[0] - 1, fl[1] - 1), (fr[0] + 1, fr[1] + 1)
    for y in range(top, by - 1):
        s_ = lean if y == top else 0
        lg.set(Lx + s_, y, "P"); lg.set(Lx + 1 + s_, y, "p"); lg.set(Lx + 2 + s_, y, "q")
        lg.set(Rx + s_, y, "p"); lg.set(Rx + 1 + s_, y, "q"); lg.set(Rx + 2 + s_, y, "Q")
    if kind == "tiptoe":
        ft.rect(Lx, by - 1, Lx + 2, by, "w"); ft.set(Lx, by - 1, "W"); ft.rect(Lx, by, Lx + 2, by, "g")
        ft.rect(Rx, by - 1, Rx + 2, by, "g"); ft.rect(Rx, by, Rx + 2, by, "G")
    else:
        for (a, c), dark in ((fl, False), (fr, True)):
            for x in range(a, c + 1): ft.set(x, by - 1, "g" if dark else "w"); ft.set(x, by, "G" if dark else "g")
            ft.set(a, by - 1, "w" if dark else "W")
    return lg, ft

def legs_walk(x0, top, by, feet, far):
    lg = Part("peach"); ftf = Part("white"); ftn = Part("white")
    hips = {"L": x0 + 3, "R": x0 + 7}
    order = (far, "L" if far == "R" else "R") if far else ("L", "R")
    for side in order:
        fx, lift = feet[side]; fx += x0; hip = hips[side]; fc = fx + 1
        bot = by - 1 - lift; farside = (side == far)
        for y in range(top, bot):
            t = (y - top + 1) / max(1, bot - top)
            x = round(hip + (fc - hip) * t)
            cols = ("q", "Q", "Q") if farside else ("P", "p", "q")
            for k in range(3): lg.set(x + k, y, cols[k])
        ft = ftf if farside else ftn
        for x in range(fx, fx + 5):
            ft.set(x, bot, "g" if farside else "w"); ft.set(x, bot + 1, "G" if farside else "g")
        ft.set(fx, bot, "w" if farside else "W")
    return lg, ftf, ftn

def mitten(x, y, far=False):
    """3x3 mitten, (x, y) = top-left; rounded bottom-right"""
    m = Part("white")
    cols = [["W", "w", "w"], ["w", "w", "g"], ["g", "g", "G"]] if not far else [["w", "g", "g"], ["g", "g", "G"], ["G", "G", "GG"]]
    for j in range(3):
        for i in range(3): m.set(x + i, y + j, cols[j][i])
    return m

def arm(sx, sy, hx, hy, near=True):
    """2px arm from shoulder to the mitten centre"""
    a = Part("peach"); pts = line(sx, sy, hx, hy)
    steep = abs(hy - sy) >= abs(hx - sx)
    for (x, y) in pts:
        a.set(x, y, "P" if near else "q")
        if steep: a.set(x + 1, y, "p" if near else "Q")
        else: a.set(x, y + 1, "p" if near else "Q")
    return a

def broom(T, Cc):
    hd = Part("wood"); pts = line(T[0], T[1], Cc[0], Cc[1])
    steep = abs(Cc[1] - T[1]) >= abs(Cc[0] - T[0])
    for (x, y) in pts:
        hd.set(x, y, "h5")
        if steep: hd.set(x + 1, y, "h3")
        else: hd.set(x, y + 1, "h3")
    hd.set(T[0], T[1], "h4")
    k = (Cc[0] - T[0]) / max(1, Cc[1] - T[1]); k = max(-1.2, min(1.2, k))
    bd = Part("bind"); cx, cy = Cc
    bd.rect(cx - 1, cy + 1, cx + 2, cy + 2, "k3"); bd.set(cx - 1, cy + 1, "k4"); bd.set(cx, cy + 1, "k4"); bd.set(cx + 1, cy + 1, "k4")
    br = Part("straw")
    widths = [(-3, 3), (-3, 4), (-4, 4), (-4, 5), (-4, 5)]
    for r, (a, b) in enumerate(widths):
        y = cy + 3 + r; off = round(k * (r + 1))
        for x in range(a, b + 1):
            c = "t4" if x < 0 else ("t3" if x < b else "t2")
            if x == a: c = "t5"
            if (x + r) % 3 == 0 and a < x < b: c = "t3" if c == "t4" else "t2"
            if r == 4 and (x % 2 == 1): c = "t3"
            br.set(cx + x + off, y, c)
    return hd, bd, br

def robot(P):
    """P: cx, by, face, bdx, bdy, hdx, hdy, tilt, eye=(shape,dx,dy), ant=(dx,dy), legs, feet, hands {L,R}: mitten centre,
       broom (T, C), broom_behind, sit, rim, puff, bulb (False = antenna light off), shadow_w"""
    f = Frame()
    cx, by = P["cx"], P["by"]; bdx, bdy = P.get("bdx", 0), P.get("bdy", 0)
    face = P.get("face", "front"); tilt = P.get("tilt", 0)
    x0 = cx - 6 + bdx; btop = by - 14 + bdy
    hx = cx - 9 + bdx + P.get("hdx", 0); hy = btop - 13 + P.get("hdy", 0)
    sw = P.get("shadow_w", 9)
    for y in ((by, by + 1) if sw > 0 else ()):
        for x in range(cx - sw + (1 if y == by + 1 else 0), cx + sw + 1 - (1 if y == by + 1 else 0)): f.sh.add((x, y))
    br = broom(*P["broom"]) if P.get("broom") else None
    sit = P.get("sit", False)
    if br and P.get("broom_behind"): f.add(br[0]); f.add(br[1]); f.add(br[2])
    far = {"qr": "L", "ql": "R", "r": "L", "l": "R", "br": "R", "bl": "L"}.get(face)
    if not sit and P.get("feet"):
        lg, ftf, ftn = legs_walk(x0, btop + 9, by, P["feet"], far if face not in ("back", "front") else None)
        f.add(ftf); f.add(lg); f.add(ftn)
    elif not sit:
        lg, ft = legs(P.get("legs", "stand"), x0, btop + 9, by, face, bdx)
        f.add(lg); f.add(ft)
    shL = (x0 - 1, btop + 2); shR = (x0 + 12, btop + 2)
    if face in ("l", "r"): shL = shR = (x0 + 5, btop + 2)
    hands = P.get("hands", {})
    def hand_of(side):
        h = hands.get(side)
        if h is None:
            sh = shL if side == "L" else shR
            h = (sh[0] + (-1 if side == "L" else 1) * (0 if face not in ("l", "r") else 0), sh[1] + 6)
        return h
    def do_arm(side, near):
        sh = shL if side == "L" else shR; h = hand_of(side)
        f.add(arm(sh[0], sh[1], h[0], h[1], near=near))
        f.add(mitten(h[0] - 1, h[1] - 1, far=not near))
    back = face in ("back", "br", "bl")
    if far: do_arm(far, False)
    b, panel = body(face)
    f.add(b.shift(x0, btop))
    if panel: f.add(panel.shift(x0, btop), outline=False)
    if br and not P.get("broom_behind"): f.add(br[0])
    hp, ears, scr = head(face)
    ant = P.get("ant", (0, 0)); an = Part("gold")
    ax = 9 + ant[0]; ay = -4 + ant[1] - (1 if abs(ant[0]) > 1 else 0)
    for i, (x, y) in enumerate(line(9, -1, ax, ay + 1)): an.set(x, y, "au" if i == 0 else "aU")
    an.set(ax, ay, "b3"); an.set(ax + 1, ay, "b3"); an.set(ax, ay - 1, "b3"); an.set(ax + 1, ay - 1, "b3")
    for part in (ears, an): f.add(part.shear(1, tilt).shift(hx, hy))
    f.add(hp.shear(1, tilt).shift(hx, hy))
    bx_, by_ = hx + ax + tilt, hy + ay
    if P.get("bulb", True):
        f.emit(bx_, by_ - 1, "b2"); f.emit(bx_ + 1, by_ - 1, "b1"); f.emit(bx_, by_, "b1"); f.emit(bx_ + 1, by_, "b3")
    else:
        for q in ((0, -1), (1, -1), (0, 0), (1, 0)): f.a[(bx_ + q[0], by_ + q[1])] = C["bo"]
    if scr:
        shape, edx, edy = P.get("eye", ("open", 0, 0))
        if shape != "off":
            ep = eyes(shape, edx, edy, scr[2])
            if ep:
                miny = min(y for _, y, _ in ep); maxy = max(y for _, y, _ in ep)
                minx = min(x for x, _, _ in ep); maxx = max(x for x, _, _ in ep)
                sy_ = (1 - miny) if miny < 1 else ((6 - maxy) if maxy > 6 else 0)
                sx_ = (1 - minx) if minx < 1 else (((scr[2] - 2) - maxx) if maxx > scr[2] - 2 else 0)
                if scr[2] <= 3: sx_ = 0 if face == "r" else 1
                for (x, y, c) in ep: f.emit(hx + scr[0] + x + sx_, hy + scr[1] + y + sy_, c)
    for side in ("L", "R"):
        if side != far: do_arm(side, not back or True)
    if br and not P.get("broom_behind"): f.add(br[1]); f.add(br[2])
    for side in ("L", "R"):                                   # mittens on the handle are drawn over it
        if side != far and br and not P.get("broom_behind"):
            h = hand_of(side); f.add(mitten(h[0] - 1, h[1] - 1))
    for (x, y, c) in P.get("puff", []): f.fx[(x, y)] = C.get(c, c)
    if P.get("rim"):
        pts = {q for q in f.a if abs(q[0] - cx) <= 13}
        edge = {(x, y) for (x, y) in pts if any((x + dx, y + dy) not in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        for (x, y) in pts - edge:
            if y < hy or (x, y) in f.e: continue
            if (x, y - 1) in edge: f.emit(x, y, "#ffd6a0")
            elif ((x - 1, y) in edge or (x + 1, y) in edge) and y < hy + 11: f.emit(x, y, "#e8a070")
    return f

def at_y(T, Cc, y):
    """mitten centre for a hand gripping the handle at row y"""
    if Cc[1] == T[1]: return (T[0], y)
    t = (y - T[1]) / (Cc[1] - T[1]); t = max(0.0, min(1.0, t))
    return (round(T[0] + (Cc[0] - T[0]) * t), y)

def turn_path(a, b):
    """facings stepped through when turning from a to b (shortest way round the 8-direction ring), excluding a"""
    i, j = DIRS.index(a), DIRS.index(b); n = len(DIRS)
    d = (j - i) % n
    step = 1 if d <= n // 2 else -1
    out = []; k = i
    while k != j: k = (k + step) % n; out.append(DIRS[k])
    return out
