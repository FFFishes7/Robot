"""All v08 robot drawings (old room coords). Run to write frames/*.png + frames/drawings.json.
v08: broom leans on the window sill (visible contact + wall shadow), mechanical boot/attention start, lively hesitation,
arced reach with anticipation + follow-through, longing lean with sagging broom, lean action, climb onto the seat."""
import json, sys, math
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from robot08 import robot, at_y, DIRS
CX, BY = 236, 80
D = {}
def base(**k):
    p = dict(cx=CX, by=BY, face="front", eye=("open", 0, 0), ant=(0, 0), legs="stand"); p.update(k); return p
def sgn(v): return (v > 0) - (v < 0)
def shifted(p, dx):
    q = dict(p); q["cx"] = p.get("cx", CX) + dx
    if "hands" in q: q["hands"] = {k: (v[0] + dx, v[1]) for k, v in q["hands"].items()}
    if "broom" in q and not q.get("broom_fixed"): q["broom"] = tuple((a[0] + dx, a[1]) for a in q["broom"])
    return q
# ---- the broom's resting place: bristles on the floor at the wall base, handle top resting on the window-sill lip
Tw, Cw = (251, 57), (247, 73)
def lean_shadow(T, C):
    sh = [(x - 1, y + 1) for (x, y) in __import__("robot08").line(T[0], T[1], C[0], C[1]) if y >= 62]
    sh += [(x, C[1] + 8) for x in range(C[0] - 4, C[0] + 6)] + [(x, C[1] + 9) for x in range(C[0] - 3, C[0] + 5)]
    return sh
LEAN = dict(broom=(Tw, Cw), broom_behind=True, broom_fixed=True, extra_sh=lean_shadow(Tw, Cw))
T0, Cs = (CX + 12, BY - 24), (CX + 5, BY - 8)          # held broom
def held(T, C=Cs, both=True):
    h = {"R": at_y(T, C, BY - 17)}
    if both: h["L"] = at_y(T, C, BY - 11)
    return h
# ---------------- day start: standby -> boot flicker -> SNAP to attention (stiff, mechanical) -> check device -> pivot -> take broom
D["standby"] = base(hdy=1, eye=("off", 0, 0), bulb=False, ant=(0, 1), **LEAN)
D["boot_a"] = base(hdy=1, eye=("dim", 0, 1), ant=(0, 1), **LEAN)
D["boot_b"] = base(hdy=1, eye=("off", 0, 0), ant=(0, 1), **LEAN)
D["snap_up"] = base(bdy=-1, hdy=-1, eye=("wide", 0, 0), ant=(0, -2), **LEAN)
D["attention"] = base(eye=("open", 0, 0), ant=(0, -1), **LEAN)
D["att_left"] = base(eye=("open", -2, 0), ant=(0, -1), **LEAN)
D["att_nod"] = base(hdy=1, eye=("open", -2, 1), ant=(0, 0), **LEAN)
D["att_qr"] = base(face="qr", eye=("open", 2, 0), ant=(0, -1), **LEAN)
D["grab"] = base(face="qr", eye=("open", 2, 0), ant=(-1, 0), hands={"R": at_y(Tw, Cw, 63)}, **LEAN)
Tg, Cg = (250, 56), (244, 72)
D["grab2"] = base(face="qr", eye=("open", 2, 1), ant=(1, 0), broom=(Tg, Cg), hands=held(Tg, Cg))
D["grab3"] = base(face="qr", eye=("open", 2, 1), ant=(0, 0), broom=(T0, Cs), hands=held(T0))
# ---------------- sweep cycle (as v07)
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
# ---------------- finish: stop, nod at the check
D["stop"] = base(eye=("open", 0, 1), ant=(1, 0), broom=(T0, Cs), hands=held(T0))
D["done_look"] = base(eye=("open", -2, 0), ant=(0, 0), broom=(T0, Cs), hands=held(T0))
D["done_nod"] = base(hdy=1, eye=("happy", -1, 0), ant=(0, 1), broom=(T0, Cs), hands=held(T0))
D["done_up"] = base(eye=("happy", 0, 0), ant=(0, -1), broom=(T0, Cs), hands=held(T0))
# ---------------- dusk: notice, look up, LONGING (lean toward the window, head tilted up, broom sags)
D["notice"] = base(eye=("open", 2, 0), ant=(0, -1), broom=(T0, Cs), hands=held(T0))
D["antic"] = base(hdy=1, eye=("blink", 2, 0), ant=(-1, 0), broom=(T0, Cs), hands=held(T0))
D["look1"] = base(face="qr", hdy=-1, tilt=-1, eye=("wide", 2, -2), ant=(-2, 0), broom=(T0, Cs), hands=held(T0))
D["look2"] = base(face="qr", hdy=-1, tilt=-1, eye=("open", 2, -2), ant=(1, 0), broom=(T0, Cs), hands=held(T0))
Td1 = (CX + 14, BY - 23); Td2 = (CX + 16, BY - 22); Td3 = (CX + 18, BY - 21); Td4 = (CX + 20, BY - 19)
D["look3"] = base(face="qr", hdy=-1, tilt=-1, eye=("soft", 2, -2), ant=(0, 0), broom=(Td1, Cs), hands=held(Td1, both=False))
D["look4"] = base(face="qr", hdy=-1, tilt=-1, eye=("soft", 2, -2), ant=(0, 0), broom=(Td2, Cs), hands=held(Td2, both=False))
D["long_r"] = base(face="r", hdy=-1, tilt=-1, eye=("soft", 0, -1), ant=(-1, 0), broom=(Td2, Cs), hands={"R": at_y(Td2, Cs, BY - 15)})
# turned toward the window behind him (back three-quarter), head up, leaning in, the broom sagging away in a loose hand
for k, (T, bdx, bdy, ant, hdx) in enumerate([(Td2, 1, 0, (0, 0), 0), (Td3, 1, 0, (1, 0), 0), (Td3, 1, -1, (1, -1), 0),
                                             (Td4, 1, 0, (0, 0), 1), (Td4, 1, 0, (-1, 0), 1), (Td4, 1, 0, (0, 1), 1)]):
    D[f"long{k}"] = base(face="br", hdy=-1, tilt=-1, bdx=bdx, bdy=bdy, hdx=hdx, ant=ant, broom=(T, Cs), broom_behind=True,
                         hands={"R": at_y(T, Cs, BY - 14 + (k >= 3))})
D["tb_r"] = base(face="r", eye=("wide", 0, 0), ant=(-2, 0), broom=(Td2, Cs), hands={"R": at_y(Td2, Cs, BY - 16)})
D["tb_qr"] = base(face="qr", eye=("wide", 0, 0), ant=(-2, -1), broom=(Ta := (CX + 15, BY - 23), Cs), hands={"R": at_y((CX + 15, BY - 23), Cs, BY - 17)})
# ---------------- alarm: startle + a LIVELY hesitation (eye darts, head turns, antenna twitches, a step toward the alarm and back)
Ta = (CX + 15, BY - 23); RH = {"R": at_y(Ta, Cs, BY - 17)}
D["startle1"] = base(hdx=-1, bdy=-1, eye=("wide", -2, 0), ant=(2, 0), broom=(Ta, Cs), hands=dict(RH, L=(CX - 10, BY - 15)))
D["startle2"] = base(eye=("wide", -2, 0), ant=(-1, -1), broom=(Ta, Cs), hands=dict(RH, L=(CX - 10, BY - 14)))
def HZ(name, face, eye, ex, ey, ant, dx=0, legs="stand", hdy=0, tilt=0, bdy=0):
    p = base(face=face, eye=(eye, ex, ey), ant=ant, legs=legs, hdy=hdy, tilt=tilt, bdy=bdy, broom=(Ta, Cs), hands=RH,
             broom_behind=face in ("ql", "l"))
    D[name] = shifted(p, dx)
HZ("hz_al", "ql", "open", -2, 0, (1, 0)); HZ("hz_al_tw", "ql", "open", -2, 0, (2, -1)); HZ("hz_al_w", "ql", "wide", -2, 0, (-1, -1))
HZ("hz_al_worry", "ql", "squint", -2, 1, (1, 1)); HZ("hz_al_mid", "ql", "open", 0, -1, (0, 0))
HZ("hz_fr", "front", "open", 1, -1, (0, 0)); HZ("hz_fr_l", "front", "open", -1, 0, (1, 0))
HZ("hz_win", "qr", "soft", 2, -2, (-1, 0), hdy=-1, tilt=-1); HZ("hz_win_s", "qr", "soft", 2, -2, (0, 0), hdy=-1, tilt=-1)
HZ("hz_win_b", "qr", "blink", 2, -2, (0, 0), hdy=-1, tilt=-1); HZ("hz_win_mid", "qr", "open", 0, 0, (1, 0))
HZ("hz_step1", "ql", "open", -2, 0, (2, 0), dx=-2, legs="wide", bdy=1); HZ("hz_step2", "ql", "open", -2, 0, (1, 0), dx=-3)
HZ("hz_step2_doubt", "ql", "open", 0, -1, (0, 1), dx=-3); HZ("hz_back1", "ql", "open", 1, -1, (-1, 0), dx=-1, legs="wide", bdy=1)
HZ("hz_sigh", "qr", "soft", 2, -1, (0, 1), hdy=0); HZ("hz_dec", "ql", "squint", -2, 0, (1, 0)); HZ("hz_dec_nod", "ql", "squint", -2, 1, (0, 1), hdy=1)
SH = -6
for k, (dx, lg) in enumerate([(-2, "wide"), (-4, "stand"), (-5, "wide"), (-6, "stand")]):
    D[f"shuf{k+1}"] = shifted(base(face="ql", legs=lg, bdy=0 if lg == "stand" else 1, eye=("squint", -2, 0), ant=((1, 0) if k % 2 else (2, 0)), broom=(Ta, Cs), hands=RH, broom_behind=True), dx)
    D[f"shufb{k+1}"] = shifted(base(face="qr", legs=lg, bdy=0 if lg == "stand" else 1, eye=("soft", 2, -1), ant=((-1, 0) if k % 2 else (-2, 0)), broom=(Ta, Cs), hands=RH), SH - dx)
# ---------------- reach: anticipation (crouch, hand winds back), arced reach, overshoot, settle on hover; release with follow-through
def A(**k): return shifted(base(**{"face": "ql", "broom": (Ta, Cs), "broom_behind": True, **k}), SH)
def bez(p0, p1, p2, t): return (round((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]), round((1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
# (pre-shift coords: final x = value - 6)
P_rest, P_back, P_ctrl, P_hover = (CX - 7, BY - 6), (CX - 4, BY - 6), (CX - 14, BY - 9), (CX - 9, BY - 20)
D["reach_antic1"] = A(legs="crouch", bdy=1, eye=("squint", -2, 0), ant=(0, 1), hands=dict(RH, L=(CX - 6, BY - 6)))
D["reach_antic"] = A(tilt=1, legs="crouch", bdy=1, eye=("squint", -2, -1), ant=(1, 1), hands=dict(RH, L=P_back))
arc = [0.2, 0.45, 0.72, 0.92]
for k, t in enumerate(arc):
    bdy = [1, 0, -1, -1][k]; lg = ["crouch", "stand", "tiptoe", "tiptoe"][k]
    D[f"reach_arc{k}"] = A(tilt=1, legs=lg, bdy=bdy, bdx=0 if k < 2 else -1, eye=("wide", -2, -1), ant=[(2, 1), (2, 0), (2, -1), (1, -1)][k],
                           hands=dict(RH, L=bez(P_back, P_ctrl, P_hover, t)), shadow_w=8 if k < 2 else 7)
D["reach_over"] = A(tilt=1, legs="tiptoe", bdy=-1, bdx=-1, eye=("wide", -2, -1), ant=(-1, 0), hands=dict(RH, L=(CX - 11, BY - 21)), shadow_w=7)
D["hover"] = A(tilt=1, legs="tiptoe", bdy=-1, bdx=-1, eye=("open", -2, -1), ant=(0, 0), hands=dict(RH, L=P_hover), shadow_w=7)
D["contact"] = A(tilt=1, legs="tiptoe", bdy=-1, bdx=-1, eye=("open", -2, -1), ant=(-1, 0), hands=dict(RH, L=(CX - 11, BY - 19)), shadow_w=7)
D["press"] = A(tilt=1, legs="tiptoe", bdy=-1, bdx=-1, eye=("squint", -2, -1), ant=(-2, 0), hands=dict(RH, L=(CX - 12, BY - 19)), shadow_w=7)
D["press_hold"] = dict(D["press"], eye=("blink", -2, -1), ant=(-1, 0))
D["rel1"] = A(tilt=1, legs="tiptoe", bdy=-1, eye=("soft", -2, -1), ant=(2, 0), hands=dict(RH, L=(CX - 7, BY - 19)), shadow_w=7)
D["rel2"] = A(legs="stand", bdy=0, eye=("soft", -1, 0), ant=(2, -1), hands=dict(RH, L=(CX - 5, BY - 16)))
D["rel3"] = A(legs="crouch", bdy=1, eye=("soft", -1, 0), ant=(-1, 1), hands=dict(RH, L=(CX - 6, BY - 12)))
D["rel4"] = A(legs="stand", eye=("soft", -1, 0), ant=(0, 0), hands=dict(RH, L=(CX - 7, BY - 8)))
D["after_front"] = A(face="front", eye=("open", 0, -1), ant=(0, 0), broom_behind=False, hands=RH)
Tb = (CX + 14, BY - 23)
D["lookback"] = base(face="qr", tilt=-1, hdy=-1, eye=("happy", 2, -2), ant=(0, 0), broom=(Tb, Cs), hands={"R": at_y(Tb, Cs, BY - 17)})
D["lookback2"] = dict(D["lookback"], ant=(-1, 0), hdy=0)
# ---------------- lean action: tilt the broom onto the sill (tock), a small settle wobble, let go, a pat, look at it
for k, (T, C) in enumerate([((250, 57), (243, 73)), ((251, 57), (245, 73)), (Tw, Cw)]):
    D[f"lean{k+1}"] = base(face="qr", eye=("open", 2, 0), ant=[(1, 0), (0, 0), (-1, 0)][k], broom=(T, C), broom_behind=True, hands={"R": at_y(T, C, 63)})
D["lean_wob"] = base(face="qr", eye=("open", 2, 0), ant=(1, 0), broom=((252, 57), Cw), broom_behind=True, hands={"R": (251, 63)}, extra_sh=lean_shadow((252, 57), Cw))
D["lean_let"] = base(face="qr", eye=("open", 2, 1), ant=(0, 0), hands={"R": (250, 65)}, **LEAN)
D["lean_pat"] = base(face="qr", eye=("happy", 2, 0), ant=(0, 1), hdy=1, hands={"R": (247, 68)}, **LEAN)
D["lean_look"] = base(face="qr", eye=("soft", 2, 1), ant=(0, 0), **LEAN)
for f in DIRS: D[f"stand_{f}"] = base(face=f, eye=("soft", {"ql": -2, "l": -2, "qr": 2, "r": 2}.get(f, 0), -1), ant=(0, 0), **LEAN)
# evening power-down (day 1 end)
D["pd1"] = base(eye=("dim", 0, 1), hdy=1, ant=(0, 1), **LEAN)
# ---------------- walk (as v07)
SW = [(7, 0), (5, 1), (2, 2), (0, 1)]; ST = [(-1, 0), (1, 0), (3, 0), (5, 0)]; FOOT = SW + ST
PATH = [(CX, BY), (CX - 10, BY + 9), (204, 102), (112, 102), (112, 84)]
def walk_points(step=2.0):
    pts = []; carry = 0.0
    for (x0, y0), (x1, y1) in zip(PATH, PATH[1:]):
        L = math.hypot(x1 - x0, y1 - y0); d = step - carry
        while d <= L: pts.append((x0 + (x1 - x0) * d / L, y0 + (y1 - y0) * d / L)); d += step
        carry = L - (d - step)
    return pts
WP = walk_points(); WALK_N = len(WP); WALK_FACE = []; STEPS = []
for i, (wx, wy) in enumerate(WP):
    cx, by = round(wx), round(wy); ph = i % 8
    fL = FOOT[(ph + 4) % 8]; fR = FOOT[ph]
    stance = fL if (ph + 4) % 8 >= 4 else fR
    up = stance[0] in (1, 3)
    if ph in (4, 0): STEPS.append(i)              # a foot plants (footstep sound)
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
# ---------------- climb onto the window seat (back view): look up, hands on the cushion, crouch, knee up, pull up, kneel, stand,
#                  glance back at the room, turn to the window, sit down with a settle bounce
ex, ey = PATH[-1]
D["arrive_back"] = base(cx=ex, by=ey, face="back", ant=(0, 0), **LEAN)
D["arrive_look"] = base(cx=ex, by=ey, face="back", hdy=-1, ant=(-1, 0), **LEAN)
D["cl_hands"] = base(cx=ex, by=ey, face="back", ant=(0, 0), hands={"L": (ex - 8, 71), "R": (ex + 8, 71)}, **LEAN)
D["cl_crouch"] = base(cx=ex, by=ey, face="back", legs="crouch", bdy=1, ant=(0, 1), hands={"L": (ex - 8, 71), "R": (ex + 8, 71)}, **LEAN)
D["cl_knee"] = base(cx=ex, by=ey - 3, face="back", ant=(0, 2), feet={"L": (1, 4), "R": (7, 0)}, hands={"L": (ex - 8, 70), "R": (ex + 8, 70)}, shadow_w=7, **LEAN)
D["cl_pull"] = base(cx=ex, by=ey - 7, face="back", ant=(0, 2), feet={"L": (1, 1), "R": (7, 3)}, hands={"L": (ex - 9, 70), "R": (ex + 9, 70)}, shadow_w=5, front=True, **LEAN)
D["cl_kneel"] = base(cx=ex, by=ey - 12, face="back", legs="crouch", bdy=1, ant=(0, -1), hands={"L": (ex - 9, 68), "R": (ex + 9, 68)}, shadow_w=0, front=True, rim=True, **LEAN)
D["cl_stand"] = base(cx=ex, by=ey - 13, face="back", ant=(0, 0), shadow_w=0, front=True, rim=True, **LEAN)
D["cl_glance"] = base(cx=ex, by=ey - 13, face="br", eye=("soft", 1, 0), ant=(-1, 0), shadow_w=0, front=True, rim=True, **LEAN)
D["cl_glance2"] = base(cx=ex, by=ey - 13, face="r", eye=("soft", 0, 0), ant=(-1, 0), shadow_w=0, front=True, rim=True, **LEAN)
D["cl_sitdown"] = base(cx=ex - 2, by=ey - 13, face="back", legs="crouch", bdy=1, ant=(0, -1), shadow_w=0, front=True, rim=True, **LEAN)
SIT = dict(cx=108, by=69, face="back", sit=True, rim=True, ant=(0, 0), shadow_w=0, hands={"L": (100, 63), "R": (117, 63)}, front=True, **LEAN)
D["land"] = dict(SIT, hdy=1, ant=(0, -2))
D["land2"] = dict(SIT, hdy=0, ant=(0, 1))
D["sit"] = dict(SIT)
D["sit_lookup"] = dict(SIT, hdy=-1, ant=(-1, 0))
D["sit_lean"] = dict(SIT, tilt=1, hdx=1, ant=(1, 0))
for k, a in enumerate([(-1, 0), (0, 0), (1, 0), (0, 0)]): D[f"sit_idle{k}"] = dict(D["sit_lookup"], ant=a)
D["sit_breath"] = dict(D["sit_lookup"], hdy=0, ant=(0, -1))
# ---------------- sheet extras
for f in DIRS: D[f"turn_{f}"] = base(face=f)
for e in ("open", "blink", "wide", "soft", "happy", "squint", "dim", "off"): D[f"expr_{e}"] = base(eye=(e, 0, 0), bulb=(e != "off"))
for n, (dx, dy) in {"lookL": (-2, 0), "lookR": (2, 0), "lookU": (0, -2)}.items(): D[f"expr_{n}"] = base(eye=("open", dx, dy))
if __name__ == "__main__":
    only = sys.argv[1:]
    for n, p in D.items():
        if not only or n in only:
            q = {k: v for k, v in p.items() if k != "broom_fixed"}; robot(q).save(n)
    json.dump({n: {"front": bool(p.get("sit") or p.get("front")), "cx": p.get("cx", CX), "by": p.get("by", BY), "face": p.get("face", "front")} for n, p in D.items()},
              open(__file__.rsplit('/', 1)[0] + "/frames/drawings.json", "w"), indent=0)
    json.dump({"WALK_N": WALK_N, "STEPS": STEPS, "WALK_FACE": WALK_FACE}, open(__file__.rsplit('/', 1)[0] + "/frames/walk.json", "w"))
    print(len(D), "drawings, walk", WALK_N)
