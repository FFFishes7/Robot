import json, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from robot06 import robot, on_handle, at_y
CX, BY = 236, 80
D = {}
def base(**k):
    p = dict(cx=CX, by=BY, face="front", eye=("open", 0, 0), ant=(0, 0), legs="stand"); p.update(k); return p
def sgn(v): return (v > 0) - (v < 0)
# ---- sweep cycle: broom arcs L->R (push) and returns lifted; body counter-leans, head bobs/tilts, antenna lags
xs = [-10, -7, -2, 3, 8, 6, 1, -5]; lift = [0, 0, 0, 0, 0, -1, -1, -1]
# dust kicked up at the end of each stroke: a few pale motes that drift and fade over two drawings
PUFF = {0: [(CX - 15, BY - 2, "#e8d4b0"), (CX - 16, BY - 4, "#d8c0a0"), (CX - 13, BY - 3, "#f0e0c4")],
        1: [(CX - 16, BY - 5, "#c8b090"), (CX - 18, BY - 6, "#b8a080")],
        4: [(CX + 12, BY - 2, "#e8d4b0"), (CX + 13, BY - 4, "#d8c0a0"), (CX + 14, BY - 2, "#f0e0c4")],
        5: [(CX + 14, BY - 5, "#c8b090"), (CX + 16, BY - 6, "#b8a080")]}
for i, xo in enumerate(xs):
    v = xo - xs[i - 1]
    Cc = (CX + xo, BY - 5 + lift[i]); T = (CX + 11 - round(xo / 4), BY - 19 + (1 if abs(xo) >= 8 else 0))
    bdx = 1 if xo <= -6 else (-1 if xo >= 6 else 0)
    face = "ql" if i == 0 else ("qr" if i == 4 else "front")
    D[f"sweep{i+1}"] = base(face=face, bdx=bdx, hdy=1 if i in (0, 4) else 0, tilt=(-1 if xo < -3 else (1 if xo > 3 else 0)),
        eye=("open", sgn(xo), 1), ant=(-sgn(v) * (2 if abs(v) >= 4 else 1), 0), legs="wide" if i in (0, 4) else "stand",
        broom=(T, Cc), hands={"R": at_y(T, Cc, BY - 8 + (1 if i in (0, 4) else 0)), "L": at_y(T, Cc, BY - 5)},
        puff=PUFF.get(i, []))
# ---- stop and look up at the sunset (window is up-right), broom drifts
Cs = (CX + 4, BY - 5); T0 = (CX + 10, BY - 19)
def held(T, both=True):
    h = {"R": at_y(T, Cs, BY - 8)}
    if both: h["L"] = at_y(T, Cs, BY - 5)
    return h
D["stop"] = base(eye=("open", 0, 1), ant=(1, 0), broom=(T0, Cs), hands=held(T0))
D["notice"] = base(eye=("open", 1, 0), ant=(0, -1), broom=(T0, Cs), hands=held(T0))
D["antic"] = base(hdy=1, eye=("blink", 1, 0), ant=(-1, 0), broom=(T0, Cs), hands=held(T0))
D["look1"] = base(face="qr", hdy=-1, tilt=-1, eye=("wide", 1, -1), ant=(-2, 0), broom=(T0, Cs), hands=held(T0))
D["look2"] = base(face="qr", hdy=-1, tilt=-1, eye=("open", 1, -1), ant=(1, 0), broom=(T0, Cs), hands=held(T0))
Td1 = (CX + 12, BY - 18); Td2 = (CX + 14, BY - 17)
D["look3"] = base(face="qr", hdy=-1, tilt=-1, eye=("soft", 1, -1), ant=(0, 0), broom=(Td1, Cs), hands=held(Td1, False))
D["look4"] = base(face="qr", hdy=-1, tilt=-1, eye=("soft", 1, -1), ant=(0, 0), broom=(Td2, Cs), hands=held(Td2, False))
D["look4_blink"] = dict(D["look4"], eye=("blink", 1, -1))
# ---- alarm rings (device is up-left on the wainscot): startle, turn, anticipation, reach, press, release, look back
Ta = (CX + 13, BY - 18)
D["startle1"] = base(hdx=-1, bdy=-1, eye=("wide", -1, 0), ant=(2, 0), broom=(Ta, Cs), hands={"R": at_y(Ta, Cs, BY - 8), "L": (CX - 8, BY - 11)})
D["startle2"] = base(hdx=0, bdy=0, eye=("wide", -1, 0), ant=(-1, -1), broom=(Ta, Cs), hands={"R": at_y(Ta, Cs, BY - 8), "L": (CX - 8, BY - 10)})
D["turn"] = base(face="ql", tilt=1, hdy=-1, eye=("open", -1, -1), ant=(1, 0), broom=(Ta, Cs), hands={"R": at_y(Ta, Cs, BY - 8)})
D["reach_antic"] = base(face="ql", tilt=1, legs="crouch", bdy=1, eye=("squint", -1, -1), ant=(1, 1), broom=(Ta, Cs), hands={"R": at_y(Ta, Cs, BY - 8), "L": (CX - 9, BY - 6)})
D["reach"] = base(face="ql", tilt=1, legs="tiptoe", bdy=-1, bdx=-1, eye=("wide", -1, -1), ant=(1, 0), broom=(Ta, Cs), hands={"R": at_y(Ta, Cs, BY - 8), "L": (CX - 13, BY - 17)}, shadow_w=5)
D["press"] = base(face="ql", tilt=1, legs="tiptoe", bdy=-1, bdx=-1, eye=("blink", -1, -1), ant=(-1, 0), broom=(Ta, Cs), hands={"R": at_y(Ta, Cs, BY - 8), "L": (CX - 14, BY - 18)}, shadow_w=5)
D["release"] = base(face="ql", eye=("soft", 0, 0), ant=(1, 0), broom=(Ta, Cs), hands={"R": at_y(Ta, Cs, BY - 8), "L": (CX - 8, BY - 8)})
Tb = (CX + 12, BY - 18)
D["lookback"] = base(face="qr", tilt=-1, hdy=-1, eye=("happy", 1, -1), ant=(0, 0), broom=(Tb, Cs), hands={"R": at_y(Tb, Cs, BY - 8)})
D["lookback2"] = dict(D["lookback"], ant=(-1, 0), hdy=0)
# ---- turnaround + expressions (no broom)
for f in ("front", "qr", "ql", "back"): D[f"turn_{f}"] = base(face=f)
for e in ("open", "blink", "wide", "happy", "soft", "squint"): D[f"expr_{e}"] = base(eye=(e, 0, 0))
for n, (dx, dy) in {"lookL": (-1, 0), "lookR": (1, 0), "lookU": (0, -1)}.items(): D[f"expr_{n}"] = base(eye=("open", dx, dy))
# ---- sitting on the window seat, back to camera, watching the sunset (drawn in FRONT of the glass)
D["sit"] = dict(cx=108, by=69, face="back", sit=True, rim=True, ant=(0, 0), shadow_w=0, hands={"L": (101, 63), "R": (114, 63)})
D["sit_lookup"] = dict(D["sit"], hdy=-1, ant=(-1, 0))
D["sit_lean"] = dict(D["sit"], tilt=1, hdx=1, ant=(1, 0))
# ---- epilogue (full story cut): lean the broom on the wall, walk left to the window seat, hop up, sit and watch
Tw, Cw = (CX + 12, BY - 23), (CX + 15, BY - 7)           # broom leaning on the wainscot
D["place1"] = base(face="qr", eye=("open", 1, 0), ant=(-1, 0), broom=(Tw, Cw), broom_behind=True, hands={"R": (CX + 11, BY - 22), "L": (CX - 7, BY - 7)})
D["place2"] = base(face="qr", eye=("happy", 1, 0), ant=(1, 0), hdy=1, broom=(Tw, Cw), broom_behind=True, hands={"R": (CX + 8, BY - 8), "L": (CX - 7, BY - 7)})
D["turnL"] = base(face="ql", eye=("happy", -1, -1), ant=(1, 0), broom=(Tw, Cw), broom_behind=True)
SW = [(6, 0), (4, 1), (1, 2), (-1, 1)]; ST = [(-2, 0), (0, 0), (2, 0), (4, 0)]
FOOT = SW + ST                                       # 8-phase foot path (rel. body-left x, lift)
import math
PATH = [(CX, BY), (CX - 8, BY + 8), (206, 101), (116, 101), (116, 84)]   # around the dustpan, in front of clock + tripod, then up to the seat
def walk_points(step=2.0):
    pts = []; carry = 0.0
    for (x0, y0), (x1, y1) in zip(PATH, PATH[1:]):
        L = math.hypot(x1 - x0, y1 - y0); d = step - carry
        while d <= L: pts.append((x0 + (x1 - x0) * d / L, y0 + (y1 - y0) * d / L)); d += step
        carry = L - (d - step)
    return pts
WP = walk_points()
WALK_N = len(WP)
for i, (wx, wy) in enumerate(WP):
    cx, by = round(wx), round(wy); ph = i % 8
    fL = FOOT[(ph + 4) % 8]; fR = FOOT[ph]           # L planted while R swings, and vice versa
    stance = fL if (ph + 4) % 8 >= 4 else fR
    up = stance[0] in (0, 2)
    bdy = -1 if up else 0; x0 = cx - 5; btop = by - 10 + bdy
    hLx = x0 + 2 - round((fL[0] + 2) * 5 / 8)
    hRx = x0 + 11 - round((6 - fR[0]) * 3 / 8)
    if i > 0 and abs(wx - WP[i - 1][0]) < 0.5:        # walking straight up to the seat: back view, feet alternate in place
        fLb = (1, fL[1]); fRb = (6, fR[1])
        D[f"walk{i:02d}"] = base(cx=cx, by=by, face="back", bdy=bdy, ant=(0, 1 if up else 0), feet={"L": fLb, "R": fRb},
            broom=(Tw, Cw), broom_behind=True, hands={"L": (x0 - 2, btop + 5 + (fR[1] > 0)), "R": (x0 + 11, btop + 5 + (fL[1] > 0))})
        continue
    D[f"walk{i:02d}"] = base(cx=cx, by=by, face="ql", bdy=bdy, eye=("soft", -1, -1) if i % 40 != 21 else ("blink", -1, -1),
        ant=(1 if up else 2, 0), feet={"L": fL, "R": fR}, broom=(Tw, Cw), broom_behind=True,
        hands={"L": (hLx, btop + 5 + (1 if hLx > x0 else 0)), "R": (hRx, btop + 6)})
ex, ey = PATH[-1]
D["arrive"] = base(cx=ex, by=ey, face="ql", eye=("soft", -1, -1), ant=(-1, 0), broom=(Tw, Cw), broom_behind=True)
D["arrive_up"] = base(cx=ex, by=ey, face="back", ant=(0, 0), broom=(Tw, Cw), broom_behind=True)
D["hop_antic"] = base(cx=ex, by=ey, face="back", legs="crouch", bdy=1, ant=(0, 1), broom=(Tw, Cw), broom_behind=True, hands={"L": (ex - 8, ey - 6), "R": (ex + 7, ey - 6)})
D["hop"] = base(cx=ex - 3, by=74, face="back", rim=True, legs="tiptoe", bdy=-1, ant=(0, 2), broom=(Tw, Cw), broom_behind=True, front=True, shadow_w=0, hands={"L": (ex - 12, 55), "R": (ex + 4, 55)})
D["land"] = dict(D["sit"], hdy=1, ant=(0, -2), broom=(Tw, Cw), broom_behind=True)
for n in ("sit", "sit_lookup", "sit_lean"): D[n + "_e"] = dict(D[n], broom=(Tw, Cw), broom_behind=True)
for k, a in enumerate([(-1, 0), (0, 0), (1, 0), (0, 0)]):
    D[f"sit_idle{k}"] = dict(D["sit_lookup_e"], ant=a)
D["sit_breath"] = dict(D["sit_lookup_e"], hdy=0, ant=(0, -1))
if __name__ == "__main__":
    for n, p in D.items(): robot(p).save(n)
    json.dump({n: {"front": bool(p.get("sit") or p.get("front")), "cx": p.get("cx", CX), "by": p.get("by", BY)} for n, p in D.items()}, open(__file__.rsplit('/', 1)[0] + "/frames/drawings.json", "w"), indent=1)
    print(len(D), "drawings")
