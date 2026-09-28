"""All v07 robot drawings (old room coords). Run to write frames/*.png + frames/drawings.json."""
import json, sys, math
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from robot07 import robot, at_y, turn_path, DIRS
CX, BY = 236, 80
D = {}
def base(**k):
    p = dict(cx=CX, by=BY, face="front", eye=("open", 0, 0), ant=(0, 0), legs="stand"); p.update(k); return p
def sgn(v): return (v > 0) - (v < 0)
Tw, Cw = (CX + 16, BY - 27), (CX + 19, BY - 8)                  # broom leaning on the wainscot, right of him
LEAN = dict(broom=(Tw, Cw), broom_behind=True)
# ---------------- standby -> wake (start of each day)
D["standby"] = base(hdy=1, eye=("off", 0, 0), bulb=False, ant=(0, 1), **LEAN)
D["wake1"] = base(hdy=1, eye=("dim", 0, 1), ant=(0, 1), **LEAN)
D["wake2"] = base(eye=("blink", 0, 0), ant=(0, -1), **LEAN)
D["wake3"] = base(eye=("open", 0, 0), ant=(0, -2), **LEAN)
D["wake_look"] = base(eye=("open", -2, 0), ant=(1, 0), **LEAN)            # glances at the reminder
D["wake_nod"] = base(hdy=1, eye=("happy", -1, 0), ant=(0, 1), **LEAN)
for f in ("qr",): D[f"toBroom_{f}"] = base(face=f, eye=("open", 2, 0), ant=(-1, 0), **LEAN)
D["grab"] = base(face="qr", eye=("open", 2, 0), ant=(-1, 0), hands={"R": (Tw[0] - 1, Tw[1] + 6)}, **LEAN)
# ---------------- sweep cycle: broom arcs, body counter-leans, head bobs/tilts, antenna lags, eyes follow
xs = [-13, -9, -3, 4, 10, 8, 1, -7]; lift = [0, 0, 0, 0, 0, -1, -1, -1]
PUFF = {0: [(CX - 19, BY - 2, "#e8d4b0"), (CX - 20, BY - 4, "#d8c0a0"), (CX - 17, BY - 3, "#f0e0c4")],
        1: [(CX - 20, BY - 6, "#c8b090"), (CX - 22, BY - 7, "#b8a080")],
        4: [(CX + 16, BY - 2, "#e8d4b0"), (CX + 17, BY - 4, "#d8c0a0"), (CX + 18, BY - 2, "#f0e0c4")],
        5: [(CX + 18, BY - 6, "#c8b090"), (CX + 20, BY - 7, "#b8a080")]}
def sweep_T(xo): return (CX + 13 - round(xo / 4), BY - 24 + (1 if abs(xo) >= 10 else 0))
for i, xo in enumerate(xs):
    v = xo - xs[i - 1]
    Cc = (CX + xo, BY - 8 + lift[i]); T = sweep_T(xo)
    bdx = 1 if xo <= -8 else (-1 if xo >= 8 else 0)
    face = "ql" if i == 0 else ("qr" if i == 4 else "front")
    D[f"sweep{i+1}"] = base(face=face, bdx=bdx, hdy=1 if i in (0, 4) else 0, tilt=(-1 if xo < -4 else (1 if xo > 4 else 0)),
        eye=("open", 2 * sgn(xo), 1), ant=(-sgn(v) * (2 if abs(v) >= 5 else 1), 0), legs="wide" if i in (0, 4) else "stand",
        broom=(T, Cc), hands={"R": at_y(T, Cc, BY - 17 + (1 if i in (0, 4) else 0)), "L": at_y(T, Cc, BY - 11)}, puff=PUFF.get(i, []))
# ---------------- stop and look up at the sunset (window is up-right), broom drifts
Cs = (CX + 5, BY - 8); T0 = (CX + 12, BY - 24)
def held(T, both=True):
    h = {"R": at_y(T, Cs, BY - 17)}
    if both: h["L"] = at_y(T, Cs, BY - 11)
    return h
D["stop"] = base(eye=("open", 0, 1), ant=(1, 0), broom=(T0, Cs), hands=held(T0))
D["notice"] = base(eye=("open", 2, 0), ant=(0, -1), broom=(T0, Cs), hands=held(T0))
D["antic"] = base(hdy=1, eye=("blink", 2, 0), ant=(-1, 0), broom=(T0, Cs), hands=held(T0))
D["look1"] = base(face="qr", hdy=-1, tilt=-1, eye=("wide", 2, -2), ant=(-2, 0), broom=(T0, Cs), hands=held(T0))
D["look2"] = base(face="qr", hdy=-1, tilt=-1, eye=("open", 2, -2), ant=(1, 0), broom=(T0, Cs), hands=held(T0))
Td1 = (CX + 14, BY - 23); Td2 = (CX + 16, BY - 22)
D["look3"] = base(face="qr", hdy=-1, tilt=-1, eye=("soft", 2, -2), ant=(0, 0), broom=(Td1, Cs), hands=held(Td1, False))
D["look4"] = base(face="qr", hdy=-1, tilt=-1, eye=("soft", 2, -2), ant=(0, 0), broom=(Td2, Cs), hands=held(Td2, False))
D["look4_blink"] = dict(D["look4"], eye=("blink", 2, -2))
D["look4_sway"] = dict(D["look4"], ant=(1, 0))
# ---------------- alarm: startle, hesitate (alarm -> window -> alarm), reach with anticipation, press, release, look back
Ta = (CX + 15, BY - 23)
RH = {"R": at_y(Ta, Cs, BY - 17)}
D["startle1"] = base(hdx=-1, bdy=-1, eye=("wide", -2, 0), ant=(2, 0), broom=(Ta, Cs), hands=dict(RH, L=(CX - 10, BY - 15)))
D["startle2"] = base(hdx=0, bdy=0, eye=("wide", -2, 0), ant=(-1, -1), broom=(Ta, Cs), hands=dict(RH, L=(CX - 10, BY - 14)))
D["hes_alarm"] = base(face="ql", eye=("open", -2, 0), ant=(1, 0), broom=(Ta, Cs), hands=RH)
D["hes_front"] = base(face="front", eye=("open", 0, -1), ant=(0, 0), broom=(Ta, Cs), hands=RH)
D["hes_window"] = base(face="qr", hdy=-1, tilt=-1, eye=("soft", 2, -2), ant=(-1, 0), broom=(Ta, Cs), hands=RH)
D["hes_window_b"] = dict(D["hes_window"], eye=("blink", 2, -2))
D["hes_alarm2"] = base(face="ql", eye=("squint", -2, 0), ant=(1, 0), broom=(Ta, Cs), hands=RH)
D["hes_alarm2_nod"] = base(face="ql", hdy=1, eye=("squint", -2, 1), ant=(0, 1), broom=(Ta, Cs), hands=RH)
def shifted(p, dx):
    q = dict(p); q["cx"] = p.get("cx", CX) + dx
    if "hands" in q: q["hands"] = {k: (v[0] + dx, v[1]) for k, v in q["hands"].items()}
    if "broom" in q: q["broom"] = tuple((a[0] + dx, a[1]) for a in q["broom"])
    return q
# side-shuffle 6 px toward the device (2 px per drawing, wide/stand alternating), then the press beat at cx-6
SH = -6
for k, (dx, lg) in enumerate([(-2, "wide"), (-4, "stand"), (-5, "wide"), (-6, "stand")]):
    D[f"shuf{k+1}"] = shifted(base(face="ql", legs=lg, bdy=0 if lg == "stand" else 1, eye=("squint", -2, 0), ant=((1, 0) if k % 2 else (2, 0)), broom=(Ta, Cs), hands=RH), dx)
    D[f"shufb{k+1}"] = shifted(base(face="qr", legs=lg, bdy=0 if lg == "stand" else 1, eye=("soft", 2, -1), ant=((-1, 0) if k % 2 else (-2, 0)), broom=(Ta, Cs), hands=RH), SH - dx)
# button at x 216-217 y 60-62 (sticks out of the device's right side); mitten (3x3, centre) pushes it leftward
def A(**k): return shifted(base(**{"face": "ql", "broom": (Ta, Cs), **k}), SH)
RHs = RH
D["reach_antic"] = A(tilt=1, legs="crouch", bdy=1, eye=("squint", -2, -1), ant=(1, 1), hands=dict(RHs, L=(CX - 8, BY - 9)))
D["reach"] = A(tilt=1, legs="tiptoe", bdy=-1, bdx=-1, eye=("wide", -2, -1), ant=(1, 0), hands=dict(RHs, L=(CX - 7, BY - 21)), shadow_w=7)
D["hover"] = A(tilt=1, legs="tiptoe", bdy=-1, bdx=-1, eye=("open", -2, -1), ant=(0, 0), hands=dict(RHs, L=(CX - 9, BY - 20)), shadow_w=7)
D["contact"] = A(tilt=1, legs="tiptoe", bdy=-1, bdx=-1, eye=("open", -2, -1), ant=(-1, 0), hands=dict(RHs, L=(CX - 11, BY - 19)), shadow_w=7)
D["press"] = A(tilt=1, legs="tiptoe", bdy=-1, bdx=-1, eye=("squint", -2, -1), ant=(-2, 0), hands=dict(RHs, L=(CX - 12, BY - 19)), shadow_w=7)
D["press_hold"] = dict(D["press"], eye=("blink", -2, -1), ant=(-1, 0))
D["release"] = A(eye=("soft", -1, 0), ant=(1, 0), hands=dict(RHs, L=(CX - 8, BY - 17)))
D["release2"] = A(eye=("soft", -1, 0), ant=(0, 0), hands=dict(RHs, L=(CX - 6, BY - 11)))
D["after_front"] = A(face="front", eye=("open", 0, -1), ant=(0, 0), hands=RHs)
Tb = (CX + 14, BY - 23)
D["lookback_front"] = base(face="front", eye=("open", 1, -1), ant=(-1, 0), broom=(Tb, Cs), hands={"R": at_y(Tb, Cs, BY - 17)})
D["lookback"] = base(face="qr", tilt=-1, hdy=-1, eye=("happy", 2, -2), ant=(0, 0), broom=(Tb, Cs), hands={"R": at_y(Tb, Cs, BY - 17)})
D["lookback2"] = dict(D["lookback"], ant=(-1, 0), hdy=0)
# ---------------- epilogue: lean the broom, turn, walk to the window seat, hop up, sit
D["place1"] = base(face="qr", eye=("open", 2, 0), ant=(-1, 0), hands={"R": (Tw[0] - 1, Tw[1] + 3), "L": (CX - 8, BY - 8)}, **LEAN)
D["place2"] = base(face="qr", eye=("happy", 2, 0), ant=(1, 0), hdy=1, hands={"R": (CX + 9, BY - 9)}, **LEAN)
for f in DIRS: D[f"stand_{f}"] = base(face=f, eye=("soft", {"ql": -2, "l": -2, "qr": 2, "r": 2}.get(f, 0), -1), ant=(0, 0), **LEAN)
SW = [(7, 0), (5, 1), (2, 2), (0, 1)]; ST = [(-1, 0), (1, 0), (3, 0), (5, 0)]
FOOT = SW + ST
PATH = [(CX, BY), (CX - 10, BY + 9), (204, 102), (112, 102), (112, 84)]
def walk_points(step=2.0):
    pts = []; carry = 0.0
    for (x0, y0), (x1, y1) in zip(PATH, PATH[1:]):
        L = math.hypot(x1 - x0, y1 - y0); d = step - carry
        while d <= L: pts.append((x0 + (x1 - x0) * d / L, y0 + (y1 - y0) * d / L)); d += step
        carry = L - (d - step)
    return pts
WP = walk_points(); WALK_N = len(WP); WALK_FACE = []
for i, (wx, wy) in enumerate(WP):
    cx, by = round(wx), round(wy); ph = i % 8
    fL = FOOT[(ph + 4) % 8]; fR = FOOT[ph]
    stance = fL if (ph + 4) % 8 >= 4 else fR
    up = stance[0] in (1, 3)
    bdy = -1 if up else 0; x0 = cx - 6; btop = by - 14 + bdy
    vertical = i > 0 and abs(wx - WP[i - 1][0]) < 0.5
    if vertical:
        D[f"walk{i:02d}"] = base(cx=cx, by=by, face="back", bdy=bdy, ant=(0, 1 if up else 0), feet={"L": (1, fL[1]), "R": (7, fR[1])},
            hands={"L": (x0 - 2, btop + 7 + (fR[1] > 0)), "R": (x0 + 14, btop + 7 + (fL[1] > 0))}, **LEAN)
        WALK_FACE.append("back"); continue
    hL = x0 + 5 - round((fL[0] - 3) * 4 / 6)
    D[f"walk{i:02d}"] = base(cx=cx, by=by, face="l", bdy=bdy, eye=("soft", 0, -1) if i % 40 != 21 else ("blink", 0, -1),
        ant=(1 if up else 2, 0), feet={"L": fL, "R": fR}, hands={"L": (hL, btop + 8), "R": (x0 + 5 + round((fL[0] - 3) * 3 / 6), btop + 7)}, **LEAN)
    WALK_FACE.append("l")
cx3, by3 = PATH[3]
D["corner_bl"] = base(cx=cx3, by=by3, face="bl", ant=(1, 0), hands={"L": (cx3 - 9, by3 - 7), "R": (cx3 + 8, by3 - 7)}, **LEAN)
ex, ey = PATH[-1]
D["arrive_back"] = base(cx=ex, by=ey, face="back", ant=(0, 0), **LEAN)
D["arrive_look"] = base(cx=ex, by=ey, face="back", hdy=-1, ant=(-1, 0), **LEAN)
D["hop_antic"] = base(cx=ex, by=ey, face="back", legs="crouch", bdy=1, ant=(0, 1), hands={"L": (ex - 9, ey - 7), "R": (ex + 9, ey - 7)}, **LEAN)
D["hop"] = base(cx=ex - 2, by=76, face="back", legs="tiptoe", bdy=-1, ant=(0, 2), front=True, shadow_w=0, rim=True, hands={"L": (ex - 12, 52), "R": (ex + 8, 52)}, **LEAN)
SIT = dict(cx=108, by=69, face="back", sit=True, rim=True, ant=(0, 0), shadow_w=0, hands={"L": (100, 63), "R": (117, 63)}, **LEAN)
D["land"] = dict(SIT, hdy=1, ant=(0, -2))
D["sit"] = dict(SIT)
D["sit_lookup"] = dict(SIT, hdy=-1, ant=(-1, 0))
D["sit_lean"] = dict(SIT, tilt=1, hdx=1, ant=(1, 0))
for k, a in enumerate([(-1, 0), (0, 0), (1, 0), (0, 0)]): D[f"sit_idle{k}"] = dict(D["sit_lookup"], ant=a)
D["sit_breath"] = dict(D["sit_lookup"], hdy=0, ant=(0, -1))
# ---- v07 extra in-betweens
Tg = (Tw[0] - 3, Tw[1] + 3); Cg = (CX + 11, BY - 8)
D["grab2"] = base(face="qr", eye=("open", 2, 1), ant=(1, 0), broom=(Tg, Cg), hands={"R": at_y(Tg, Cg, BY - 17), "L": at_y(Tg, Cg, BY - 11)})
D["done_nod"] = base(hdy=1, eye=("happy", 0, 0), ant=(0, 1), broom=(T0, Cs), hands=held(T0))
D["done_up"] = base(eye=("happy", 0, 0), ant=(0, -1), broom=(T0, Cs), hands=held(T0))
# ---------------- sheet extras: turnaround + expressions
for f in DIRS: D[f"turn_{f}"] = base(face=f)
for e in ("open", "blink", "wide", "soft", "happy", "squint", "dim", "off"): D[f"expr_{e}"] = base(eye=(e, 0, 0), bulb=(e != "off"))
for n, (dx, dy) in {"lookL": (-2, 0), "lookR": (2, 0), "lookU": (0, -2)}.items(): D[f"expr_{n}"] = base(eye=("open", dx, dy))
if __name__ == "__main__":
    only = sys.argv[1:]
    for n, p in D.items():
        if not only or n in only: robot(p).save(n)
    json.dump({n: {"front": bool(p.get("sit") or p.get("front")), "cx": p.get("cx", CX), "by": p.get("by", BY), "face": p.get("face", "front")} for n, p in D.items()},
              open(__file__.rsplit('/', 1)[0] + "/frames/drawings.json", "w"), indent=0)
    print(len(D), "drawings, walk", WALK_N)
