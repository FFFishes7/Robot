"""Robot v06: hand-authored pixel rules for a 15x22 game sprite (front, 3/4 L, 3/4 R, back) with
part-wise coloured outlines, hue-shifted ramps, tilt by 1px shear, antenna secondary motion, eye shapes,
a held broom (handle + red binding + straw bristles). Writes per-drawing albedo / emit / shadow layers on
the 384x216 room canvas plus drawings.json. Sheet + timeline use these."""
from PIL import Image
import json, os
OUT = os.path.dirname(os.path.abspath(__file__)) + "/frames/"
os.makedirs(OUT, exist_ok=True)
W, H = 448, 288
OX, OY = 56, 26      # v06 world offset: drawings are authored in the original room coords
C = dict(
  W="#fffdf2", w="#f3eada", g="#d8cab4", G="#a8927a", GG="#6e5a4c",           # robot white ramp (warm light -> cool shade)
  P="#f39a78", p="#d8704f", q="#b0503a", Q="#7e3322", PP="#fed6b2",           # robot peach ramp (hue-shifted to red in shade)
  s0="#0c0814", s1="#15101f", s2="#1d1c34", s3="#3a4070",                      # screen
  eh="#fdf0d8", ec="#ffffff", el="#fcc794",                                    # eye glow
  au="#f0a830", aU="#ffd24a", b1="#fc773a", b2="#fed6b2", b3="#b0503a",       # antenna gold + bulb
  led="#e46e4a",
  h5="#e0a462", h4="#c9824a", h3="#ad6436",                                    # broom handle wood
  k4="#c2604a", k3="#9c3c3e",                                                  # binding
  t5="#ecca84", t4="#d2a664", t3="#b28248", t2="#8e5e32",                      # straw
)
OUTL = dict(white="#3e2833", peach="#46181a", wood="#2e1410", straw="#43261c", bind="#2a0c1c", gold="#40240e")

class Part:
    def __init__(s, mat): s.mat = mat; s.px = {}
    def set(s, x, y, c): s.px[(x, y)] = C.get(c, c)
    def rect(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): s.set(x, y, c)
    def shift(s, dx, dy):
        p = Part(s.mat); p.px = {(x + dx, y + dy): c for (x, y), c in s.px.items()}; return p
    def shear(s, pivot_y, t):      # head tilt cue: rows above pivot_y slide 1px sideways (screen stays intact)
        p = Part(s.mat); p.px = {(x + (t if y <= pivot_y else 0), y): c for (x, y), c in s.px.items()}; return p

def line(x0, y0, x1, y1):
    pts = []; dx = abs(x1 - x0); dy = -abs(y1 - y0); sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1; e = dx + dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1: break
        e2 = 2 * e
        if e2 >= dy: e += dy; x0 += sx
        if e2 <= dx: e += dx; y0 += sy
    return pts

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
        """exterior outline pass: boundary pixels of the whole sprite get pulled toward a deep plum so the
        robot reads against the bright dusk shaft (interior part-outlines keep their own colours)"""
        out = {}
        for (x, y), c in s.a.items():
            if any((x + dx, y + dy) not in s.a for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
                k = 0.55
                out[(x, y)] = "#%02x%02x%02x" % (int(r * (1 - k) + 28 * k), int(g * (1 - k) + 10 * k), int(b * (1 - k) + 22 * k))
        s.a.update(out)
    def save(s, name):
        s.silhouette()
        for q, c in s.fx.items(): s.a.setdefault(q, c)       # loose fx pixels (dust puffs) skip the outline pass
        for suf, d in (("a", s.a), ("e", s.e)):
            im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            for (x, y), c in d.items():
                x += OX; y += OY
                if 0 <= x < W and 0 <= y < H: im.putpixel((x, y), tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (255,))
            im.save(OUT + f"{name}_{suf}.png")
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for (x, y) in s.sh:
            x += OX; y += OY
            if 0 <= x < W and 0 <= y < H: im.putpixel((x, y), (0, 0, 0, 255))
        im.save(OUT + f"{name}_s.png")

HEAD_ROWS = {0: (2, 12), 1: (1, 13), 9: (1, 13), 10: (2, 12)}
def head_mask():
    for y in range(11):
        a, b = HEAD_ROWS.get(y, (0, 14))
        for x in range(a, b + 1): yield x, y

def head(face):
    """returns (head part, ears part, screen origin or None) in head-local coords (15x11)"""
    h = Part("white"); ears = Part("peach")
    for x, y in head_mask(): h.set(x, y, "w")
    for x in range(2, 13): h.set(x, 0, "W")
    for x in range(1, 11): h.set(x, 1, "W")
    for y in range(2, 9): h.set(0, y, "W")
    for x in range(1, 14): h.set(x, 9, "g")
    for x in range(2, 13): h.set(x, 10, "G")
    scr = None
    if face == "front":
        for y in range(2, 9): h.set(13, y, "g"); h.set(14, y, "g")
        h.set(14, 8, "G"); h.set(13, 9, "G"); h.set(13, 1, "g")
        scr = (3, 3)
        ears.rect(-1, 4, -1, 6, "p"); ears.set(-1, 4, "P"); ears.rect(15, 4, 15, 6, "q"); ears.set(15, 6, "Q")
    elif face == "qr":             # turned toward viewer's right: side plane on the left
        for y in range(2, 9): h.set(14, y, "g")
        h.set(14, 8, "G"); h.set(13, 9, "G")
        for y in range(2, 9): h.set(3, y, "g")                    # crease between side plane and face
        h.set(1, 1, "W"); h.set(2, 1, "W")
        h.rect(1, 4, 2, 6, "p"); h.set(1, 4, "P"); h.set(2, 6, "q")   # ear bolt on the side plane
        scr = (5, 3)
        ears.rect(15, 5, 15, 6, "q")
    elif face == "ql":             # turned toward viewer's left: side plane on the right (shade side)
        for y in range(2, 9): h.set(11, y, "G"); h.set(12, y, "g"); h.set(13, y, "g"); h.set(14, y, "G")
        h.set(13, 9, "G"); h.set(12, 1, "g"); h.set(13, 1, "g")
        h.rect(12, 4, 13, 6, "q"); h.set(12, 4, "p"); h.set(13, 6, "Q")
        scr = (1, 3)
        ears.rect(-1, 5, -1, 6, "p")
    else:                          # back
        for y in range(2, 9): h.set(13, y, "g"); h.set(14, y, "g")
        h.rect(4, 3, 10, 7, "g"); h.set(4, 3, "w"); h.set(10, 3, "w"); h.set(4, 7, "w"); h.set(10, 7, "w")
        for x in (5, 7, 9): h.set(x, 4, "G"); h.set(x, 5, "G"); h.set(x, 6, "G")
        h.set(2, 8, "G"); h.set(12, 8, "G")
        ears.rect(-1, 4, -1, 6, "p"); ears.set(-1, 4, "P"); ears.rect(15, 4, 15, 6, "q")
    if scr:
        sx, sy = scr
        for y in range(6):
            for x in range(9):
                c = "s1"
                if y == 0: c = "s2"
                if y == 5: c = "s0"
                h.set(sx + x, sy + y, c)
        h.set(sx + 1, sy + 1, "s3")
    return h, ears, scr

EYE_L, EYE_R = (1, 2), (6, 2)       # screen-local anchors (2x2 eyes, wide set)
def eyes(shape, dx, dy):
    out = []
    for side, (ax, ay) in (("L", EYE_L), ("R", EYE_R)):
        x, y = ax + dx, ay + dy
        if shape == "open":   out += [(x, y, "ec"), (x + 1, y, "eh"), (x, y + 1, "eh"), (x + 1, y + 1, "eh")]
        elif shape == "blink": out += [(x, y + 1, "el"), (x + 1, y + 1, "el")]
        elif shape == "wide": out += [(x, y - 1, "ec"), (x + 1, y - 1, "eh"), (x, y, "eh"), (x + 1, y, "eh"), (x, y + 1, "eh"), (x + 1, y + 1, "eh")]
        elif shape == "soft": out += [(x, y + 1, "eh"), (x + 1, y + 1, "eh"), (x, y, "el") if side == "R" else (x + 1, y, "el")]
        elif shape == "happy":  # ^ ^
            b = x - 1 if side == "L" else x
            out += [(b, y + 1, "eh"), (b + 1, y, "ec"), (b + 2, y + 1, "eh")]
        elif shape == "squint":  # determined: lid slants toward the centre
            if side == "L": out += [(x, y + 1, "eh"), (x + 1, y + 1, "eh"), (x, y, "el")]
            else: out += [(x, y + 1, "eh"), (x + 1, y + 1, "eh"), (x + 1, y, "el")]
    return out

def body(face):
    b = Part("peach")
    rows = {0: (1, 9), 6: (1, 9)}
    for y in range(7):
        a, c = rows.get(y, (0, 10))
        for x in range(a, c + 1): b.set(x, y, "p")
    for x in range(1, 10): b.set(x, 0, "P")
    for y in range(1, 6): b.set(0, y, "P")
    b.set(1, 1, "P")
    for y in range(1, 6): b.set(9, y, "q"); b.set(10, y, "q")
    for x in range(1, 10): b.set(x, 5, "q"); b.set(x, 6, "Q")      # waist band + hem in shade
    b.set(10, 5, "Q")
    if face == "back":
        b.rect(3, 2, 7, 3, "q"); b.set(3, 2, "Q"); b.set(7, 3, "Q"); b.set(5, 2, "Q")
        return b, None
    px = {"front": 3, "qr": 5, "ql": 1}[face]
    panel = Part("white")
    panel.rect(px, 1, px + 4, 3, "w"); panel.set(px, 1, "W"); panel.set(px + 1, 1, "W")
    for x in range(px, px + 5): panel.set(x, 3, "g")
    panel.set(px + 2, 2, "led")
    if face == "qr":
        for y in range(1, 5): b.set(1, y, "P")
    if face == "ql":
        for y in range(1, 5): b.set(8, y, "q")
    return b, panel

def legs_walk(x0, top, by, feet, far):
    """walk/step legs: feet = {"L": (foot_left_x_rel, lift), "R": ...}; far foot drawn first and darker"""
    lg = Part("peach"); ftf = Part("white"); ftn = Part("white")
    hips = {"L": x0 + 3, "R": x0 + 6}
    order = (far, "L" if far == "R" else "R") if far else ("L", "R")
    for side in order:
        fx, lift = feet[side]; fx += x0; hip = hips[side]; fc = fx + 1
        bot = by - 1 - lift
        for y in range(top, bot):
            t = (y - top + 1) / max(1, bot - top)
            x = round(hip + (fc - hip) * t)
            lg.set(x, y, "q" if side == far else "P"); lg.set(x + 1, y, "Q" if side == far else "p")
        ft = ftf if side == far else ftn
        for x in range(fx, fx + 4):
            ft.set(x, bot, "g" if side == far else "w"); ft.set(x, bot + 1, "G" if side == far else "g")
        ft.set(fx, bot, "w" if side == far else "W")
    return lg, ftf, ftn

def legs(kind, x0, top, by, lean):
    """legs from body bottom (top) to feet (by); x0 = body left; feet planted"""
    lg = Part("peach"); ft = Part("white")
    L, R = x0 + 3, x0 + 6
    fl, fr = (x0 + 1, x0 + 4), (x0 + 6, x0 + 9)
    if kind == "wide": fl, fr = (x0, x0 + 3), (x0 + 7, x0 + 10)
    if kind == "crouch": fl, fr = (x0, x0 + 3), (x0 + 7, x0 + 10)
    for y in range(top, by - 1):
        s = lean if y == top else 0
        lg.set(L + s, y, "P"); lg.set(L + 1 + s, y, "p"); lg.set(R + s, y, "p"); lg.set(R + 1 + s, y, "q")
    if kind == "tiptoe":
        ft.rect(L, by - 1, L + 1, by, "w"); ft.rect(R, by - 1, R + 1, by, "g"); ft.set(L, by - 1, "W")
    else:
        for x in range(fl[0], fl[1] + 1): ft.set(x, by - 1, "w"); ft.set(x, by, "g")
        for x in range(fr[0], fr[1] + 1): ft.set(x, by - 1, "w"); ft.set(x, by, "G")
        ft.set(fl[0], by - 1, "W"); ft.set(fr[0], by - 1, "W"); ft.set(fl[1], by, "G")
    return lg, ft

def mitten(x, y):
    m = Part("white"); m.set(x, y, "W"); m.set(x + 1, y, "w"); m.set(x, y + 1, "w"); m.set(x + 1, y + 1, "g"); return m

def arm(sx, sy, hx, hy, near=True):
    a = Part("peach")
    for (x, y) in line(sx, sy, hx, hy): a.set(x, y, "p" if near else "q")
    return a

def broom(T, Cc):
    """handle from T to collar top Cc; returns (handle, binding, bristles)"""
    hd = Part("wood")
    pts = line(T[0], T[1], Cc[0], Cc[1])
    steep = abs(Cc[1] - T[1]) >= abs(Cc[0] - T[0])
    for i, (x, y) in enumerate(pts):
        hd.set(x, y, "h5")
        if steep: hd.set(x + 1, y, "h3")      # 2px handle: lit edge + shade edge
        else: hd.set(x, y + 1, "h3")
    hd.set(T[0], T[1], "h4")
    k = (Cc[0] - T[0]) / max(1, Cc[1] - T[1]); k = max(-1.2, min(1.2, k))
    bd = Part("bind"); cx, cy = Cc
    bd.rect(cx - 1, cy + 1, cx + 1, cy + 2, "k3"); bd.set(cx - 1, cy + 1, "k4"); bd.set(cx, cy + 1, "k4")
    br = Part("straw")
    widths = [(-2, 2), (-2, 2), (-3, 3), (-3, 3)]
    for r, (a, b) in enumerate(widths):
        y = cy + 3 + r; off = round(k * (r + 1))
        for x in range(a, b + 1):
            c = "t4" if x < 0 else ("t3" if x < b else "t2")
            if x == a: c = "t5"
            if (x + r) % 3 == 0 and a < x < b: c = "t3" if c == "t4" else "t2"
            if r == 3 and (x % 2 == 1): c = "t3"
            br.set(cx + x + off, y, c)
    return hd, bd, br

def robot(P):
    """P: cx, by, face, bdx, bdy, hdx, hdy, tilt, eye=(shape,dx,dy), ant=(dx,dy), legs, hands: dict L/R -> (x,y) abs or None,
       broom: (T, C) abs or None, broom_hands: which hands are on the handle (drawn over it)"""
    f = Frame()
    cx, by = P["cx"], P["by"]; bdx, bdy = P.get("bdx", 0), P.get("bdy", 0)
    face = P.get("face", "front"); tilt = P.get("tilt", 0)
    x0 = cx - 5 + bdx; btop = by - 10 + bdy
    hx = cx - 7 + bdx + P.get("hdx", 0); hy = by - 21 + bdy + P.get("hdy", 0)
    # shadow
    sw = P.get("shadow_w", 7)
    for y in ((by, by + 1) if sw > 0 else ()):
        for x in range(cx - sw + (1 if y == by + 1 else 0), cx + sw + 1 - (1 if y == by + 1 else 0)): f.sh.add((x, y))
    br = None
    if P.get("broom"):
        T, Cc = P["broom"]; br = broom(T, Cc)
    sit = P.get("sit", False)
    if br and P.get("broom_behind"): f.add(br[0]); f.add(br[1]); f.add(br[2])
    if not sit and P.get("feet"):
        lg, ftf, ftn = legs_walk(cx - 5, btop + 7, by, P["feet"], {"qr": "L", "ql": "R"}.get(face))
        f.add(ftf); f.add(lg); f.add(ftn)
    elif not sit:
        lg, ft = legs(P.get("legs", "stand"), cx - 5, btop + 7, by, bdx)
        f.add(lg); f.add(ft)
    shL = (x0 - 1, btop + 2); shR = (x0 + 11, btop + 2)
    hands = P.get("hands", {})
    # far arm (3/4 views) goes behind the body
    far = {"qr": "L", "ql": "R"}.get(face)
    def do_arm(side):
        h = hands.get(side)
        sh = shL if side == "L" else shR
        if h is None: h = (sh[0] - (1 if side == "L" else -1) * 0, sh[1] + 4)
        f.add(arm(sh[0], sh[1], h[0], h[1], near=(side != far and not (face == "front" and side == "R"))))
        return h
    hand_pos = {}
    if far: hand_pos[far] = do_arm(far); f.add(mitten(*hand_pos[far]))
    b, panel = body(face)
    f.add(b.shift(x0, btop))
    if panel: f.add(panel.shift(x0, btop), outline=False)
    if br and not P.get("broom_behind"): f.add(br[0])
    hp, ears, scr = head(face)
    ant = P.get("ant", (0, 0))
    an = Part("gold")
    ax = 7 + ant[0]; ay = -3 + ant[1] - (1 if abs(ant[0]) > 1 else 0)
    for i, (x, y) in enumerate(line(7, -1, ax, ay + 1)): an.set(x, y, "au" if i == 0 else "aU")
    an.set(ax, ay, "b3")
    for part in (ears, an):
        f.add(part.shear(1, tilt).shift(hx, hy))
    f.add(hp.shear(1, tilt).shift(hx, hy))
    # emit: bulb + eyes
    bx_, by_ = hx + ax + tilt, hy + ay
    f.emit(bx_, by_, "b1"); f.emit(bx_, by_ - 1, "b2"); f.emit(bx_ - 1, by_, "b3"); f.emit(bx_ + 1, by_, "b3")
    if scr:
        shape, edx, edy = P.get("eye", ("open", 0, 0))
        ep = eyes(shape, edx, edy)
        miny = min(y for _, y, _ in ep); maxy = max(y for _, y, _ in ep)
        minx = min(x for x, _, _ in ep); maxx = max(x for x, _, _ in ep)
        sy_ = (1 - miny) if miny < 1 else ((4 - maxy) if maxy > 4 else 0)
        sx_ = (0 - minx) if minx < 0 else ((8 - maxx) if maxx > 8 else 0)
        for (x, y, c) in ep:
            lx, ly = scr[0] + x + sx_, scr[1] + y + sy_
            f.emit(hx + lx, hy + ly, c)
    for side in ("L", "R"):
        if side != far: hand_pos[side] = do_arm(side)
    if br and not P.get("broom_behind"): f.add(br[1]); f.add(br[2])
    for side in ("L", "R"):
        if side != far: f.add(mitten(*hand_pos[side]))
    for (x, y, c) in P.get("puff", []): f.fx[(x, y)] = C.get(c, c)
    if P.get("rim"):          # backlit by the sunset: warm rim just inside the dark outline on the top/outer edges (emissive)
        pts = {q for q in f.a if abs(q[0] - cx) <= 11}
        edge = {(x, y) for (x, y) in pts if any((x + dx, y + dy) not in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        for (x, y) in pts - edge:
            if y < hy or (x, y) in f.e: continue
            if (x, y - 1) in edge: f.emit(x, y, "#ffd6a0")
            elif ((x - 1, y) in edge or (x + 1, y) in edge) and y < hy + 9: f.emit(x, y, "#e8a070")
    return f

def on_handle(T, Cc, t):
    return (round(T[0] + (Cc[0] - T[0]) * t) - 1, round(T[1] + (Cc[1] - T[1]) * t) - 1)

def at_y(T, Cc, y):
    """mitten top-left for a hand gripping the handle at row y"""
    if Cc[1] == T[1]: return (T[0] - 1, y - 1)
    t = (y - T[1]) / (Cc[1] - T[1]); t = max(0.0, min(1.0, t))
    return (round(T[0] + (Cc[0] - T[0]) * t) - 1, y - 1)
