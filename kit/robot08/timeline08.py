"""v08 film: wide timeline (Godot) + edit list (close-up inserts) + sound events (wide-frame or clip-local)."""
import json, math, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
dj = json.load(open("frames/drawings.json")); wk = json.load(open("frames/walk.json"))
K = {k: [] for k in ("robot", "alarm", "btn", "cal", "dust", "sun", "beam", "day", "dusk", "night", "dawn", "lamps", "amb")}
cur = dict(robot="standby", alarm="idle", btn=0, cal="12", dust=0, sun=0.45, beam=0.6, day=0.75, dusk=0.0, night=0.0, dawn=0.0, lamps=0.12, amb=1.45)
marks, EV = {}, []                    # EV: (wide frame, sound, gain)
def n(): return len(K["robot"])
def mark(m): marks[m] = n()
def ev(s, g=1.0, off=0): EV.append((n() + off, s, g))
def hold(r, k, **st):
    cur.update(st); cur["robot"] = r
    for _ in range(k):
        for key in K: K[key].append(cur[key])
def seq(lst, **st):
    for r, k in lst: hold(r, k, **st)
def flash(nf, **st):                  # device beeps: task on 5 / off 3
    for j in range(nf):
        on = (j % 8) < 5
        if j % 8 == 0: ev("beep", 0.9)
        hold(cur["robot"], 1, alarm="task" if on else "idle", **st)
def sweeps(start, cnt, holds=None, d0=0, d1=7):
    for j in range(cnt):
        i = (start + j) % 8; k = 3 if holds is None else holds[j]
        if i in (0, 4): ev("swish", 0.8 if holds is None else 0.8 - 0.4 * j / cnt)
        hold(f"sweep{i+1}", k, dust=round(d0 + (d1 - d0) * j / max(1, cnt - 1)))
def ramp(key, a, b, f0, f1):
    for f in range(f0, f1):
        t = (f - f0) / max(1, f1 - f0 - 1); t = t * t * (3 - 2 * t); K[key][f] = a + (b - a) * t
# ================= DAY 1 (page 12)
mark("day1"); hold("standby", 72)
mark("flash1"); flash(24)
mark("task_cut")                                   # device close-up (beep, beep... robot boots, snaps up)
ev("clunk", 1.0)
seq([("snap_up", 3), ("attention", 10)], alarm="task")
ev("servo", 0.6); seq([("att_left", 8)]); ev("servo", 0.5, 0); seq([("att_nod", 4), ("att_left", 4)]); ev("servo", 0.6); seq([("attention", 4)])
ev("servo", 0.7); seq([("att_qr", 6), ("grab", 6)]); ev("cloth", 0.5); seq([("grab2", 3), ("grab3", 3)])
sweeps(4, 16)
hold("sweep4", 3); ev("chime", 0.9); seq([("stop", 6)], alarm="off"); seq([("done_look", 10), ("done_nod", 8), ("done_up", 12)])
ev("cloth", 0.4); seq([("lean1", 3), ("lean2", 3)]); ev("tock", 0.8); seq([("lean3", 4), ("lean_wob", 2), ("lean3", 2), ("lean_let", 5)])
ev("servo", 0.5); seq([("stand_front", 6)], alarm="idle"); ev("powerdown", 0.7); seq([("pd1", 10), ("standby", 8)])
# ---- time pass: evening -> night (window deep blue, stars), calendar close-up, dawn -> morning
N0 = n(); hold("standby", 56); N1 = n()
ramp("sun", 0.45, 0.0, N0, N1); ramp("beam", 0.6, 0.4, N0, N1); ramp("day", 0.75, 0.0, N0, N0 + 30); ramp("dusk", 0.0, 0.6, N0, N0 + 36)
ramp("night", 0.0, 1.0, N0 + 16, N1); ramp("amb", 1.45, 0.32, N0, N1); ramp("lamps", 0.12, 0.16, N0, N1)
for k in ("sun", "beam", "day", "dusk", "night", "amb", "lamps"): cur[k] = K[k][-1]
hold("standby", 14)
mark("cal_cut")                                    # calendar close-up (night -> dawn, 12 tears off -> 13)
D0 = n(); hold("standby", 44, cal="13", dust=0); D1 = n()
ramp("night", 0.0, 0.0, D0, D1); ramp("dawn", 1.0, 0.0, D0, D1); ramp("dusk", 0.0, 0.0, D0, D1); ramp("day", 0.0, 0.75, D0, D1)
ramp("amb", 0.7, 1.45, D0, D1); ramp("sun", 0.1, 0.45, D0, D1); ramp("beam", 0.45, 0.6, D0, D1); ramp("lamps", 0.14, 0.12, D0, D1)
for k in ("sun", "beam", "day", "dusk", "night", "dawn", "amb", "lamps"): cur[k] = K[k][-1]
cur["night"] = 0.0; cur["dawn"] = 0.0; cur["dusk"] = 0.0
# ================= DAY 2 (page 13): the same program
mark("day2"); flash(16)
ev("glitch", 0.5); seq([("boot_a", 2), ("boot_b", 2), ("boot_a", 2)]); ev("clunk", 0.9)
seq([("snap_up", 3), ("attention", 6)], alarm="task"); ev("servo", 0.5); seq([("att_left", 5)]); ev("servo", 0.6)
seq([("att_qr", 4), ("grab", 5)]); ev("cloth", 0.5); seq([("grab2", 3), ("grab3", 3)])
sweeps(4, 16, d0=0, d1=3)
# ================= DUSK: the light arrives over ~2.75 s, the sweep slows, he stops
mark("dusk"); DK = n()
holds = [3, 3, 3, 3, 4, 4, 4, 5, 5, 6, 7, 8]
sweeps(4, len(holds), holds=holds, d0=3, d1=4)
seq([("stop", 10), ("notice", 12), ("antic", 5)])
mark("face_cut")                                   # face close-up
seq([("look3", 4), ("long_r", 4), ("long0", 8), ("long1", 8), ("long2", 8), ("long1", 8), ("long3", 10), ("long4", 8), ("long5", 3), ("long3", 10), ("long4", 10)])
# ================= ALARM + a lively hesitation
mark("ring"); RG = n(); ev("ring_start", 1.0)
seq([("tb_r", 1), ("tb_qr", 1), ("startle1", 2), ("startle2", 5)], alarm="ring")
HZ = [("hz_al", 6), ("hz_al_tw", 3), ("hz_al", 5), ("hz_al_worry", 8), ("hz_al_tw", 2), ("hz_al_worry", 4),
      ("hz_al_mid", 3), ("hz_fr", 3), ("hz_win_mid", 2), ("hz_win", 8), ("hz_win_s", 6), ("hz_win_b", 3), ("hz_win", 5),
      ("hz_win_mid", 2), ("hz_fr_l", 2), ("hz_al_w", 6), ("hz_al_tw", 3), ("hz_al", 4),
      ("hz_step1", 4), ("hz_step2", 6), ("hz_step2_doubt", 8), ("hz_back1", 4), ("hz_al", 3), ("hz_fr", 3), ("hz_win", 6), ("hz_sigh", 10), ("hz_win_s", 4),
      ("hz_fr_l", 3), ("hz_dec", 10), ("hz_dec_nod", 5), ("hz_dec", 4)]
for r, k in HZ:
    if r in ("hz_step1", "hz_back1"): ev("step", 0.5)
    if r in ("hz_fr", "hz_win_mid", "hz_fr_l", "hz_al_mid"): ev("servo", 0.35)
    hold(r, k)
for k_, r in enumerate(["shuf1", "shuf2", "shuf3", "shuf4"]):
    if k_ % 2 == 0: ev("step", 0.45)
    hold(r, 3 if k_ < 3 else 4)
seq([("reach_antic1", 4), ("reach_antic", 6)]); ev("whoosh", 0.4)
seq([("reach_arc0", 2), ("reach_arc1", 2), ("reach_arc2", 2), ("reach_arc3", 2), ("reach_over", 3), ("hover", 5)])
mark("press_cut")                                  # press close-up (ring stops at contact inside the clip)
seq([("press_hold", 4)], alarm="off", btn=1)
seq([("rel1", 3)], btn=0); seq([("rel2", 3), ("rel3", 3), ("rel4", 5)])
seq([("after_front", 8)], alarm="idle")
for k_, r in enumerate(["shufb1", "shufb2", "shufb3", "shufb4"]):
    if k_ % 2 == 0: ev("step", 0.4)
    hold(r, 3 if k_ < 3 else 4)
seq([("lookback", 16), ("lookback2", 10)])
# ================= EPILOGUE: lean the broom, walk to the seat, climb up, glance back, sit; sunset fades, lights glow
mark("epi"); EP = n()
ev("cloth", 0.4); seq([("lean1", 4), ("lean2", 3)]); ev("tock", 0.9); seq([("lean3", 3), ("lean_wob", 2), ("lean3", 3), ("lean_let", 5), ("lean_pat", 6), ("lean_look", 10)])
ev("servo", 0.4); seq([("stand_qr", 5), ("stand_front", 4), ("stand_ql", 4), ("stand_l", 5)])
W0 = n()
for i in range(wk["WALK_N"]):
    if i == 66: hold("corner_bl", 2)
    if i in wk["STEPS"]: ev("step", 0.55)
    hold(f"walk{i:02d}", 1)
W1 = n()
seq([("arrive_back", 8), ("arrive_look", 14)]); ev("cloth", 0.5); seq([("cl_hands", 6), ("cl_crouch", 5)])
ev("climb", 0.7); seq([("cl_knee", 4), ("cl_pull", 4)]); ev("thump", 0.5); seq([("cl_kneel", 6), ("cl_stand", 8)])
ev("servo", 0.35); seq([("cl_glance", 5), ("cl_glance2", 16), ("cl_glance", 4), ("cl_stand", 5)])
seq([("cl_sitdown", 4)]); ev("thump", 0.7); seq([("land", 3), ("land2", 3), ("sit", 6)])
SIT0 = n()
def idle(nf, breath_at=()):
    for j in range(nf): hold("sit_breath" if any(b <= j < b + 6 for b in breath_at) else f"sit_idle{(j // 8) % 4}", 1)
idle(40, (22,)); hold("sit_lean", 20); idle(60, (18, 44))
N = n()
# ---- light: dusk arrives gradually at DK (66 f), then the sun sinks from the ring to the end; lamps rise as the sky dims
def ss(t): t = min(1.0, max(0.0, t)); return t * t * (3 - 2 * t)
for f in range(DK, N):
    h = ss((f - DK) / 66); e = ss((f - RG) / (N - 1 - RG)); e2 = ss((f - EP) / (N - 1 - EP))
    K["sun"][f] = 0.45 + 0.55 * h - 0.7 * (0.35 * e + 0.65 * e2)
    K["beam"][f] = 0.6 + 0.4 * h - 0.45 * (0.3 * e + 0.7 * e2)
    K["day"][f] = 0.75 * (1 - h); K["dusk"][f] = 0.15 * e + 0.85 * e2
    K["lamps"][f] = 0.12 + 0.28 * h + 1.35 * (0.25 * e + 0.75 * e2)
    K["amb"][f] = 1.45 - 0.45 * h - 0.12 * e2
    K["night"][f] = 0.0; K["dawn"][f] = 0.0
# ---- camera
def keyed(f, keys):
    for (a, pa), (b, pb) in zip(keys, keys[1:]):
        if f <= b:
            t = ss((f - a) / max(1, b - a)); return [pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t]
    return list(keys[-1][1])
KEYS = [(0, (0, 72)), (10, (0, 72)), (80, (50, 8)), (DK, (52, 6)), (DK + 80, (58, 4)), (RG, (58, 4)), (RG + 30, (50, 6)), (EP, (50, 6))]
cam = []; c = [50.0, 6.0]; v = [0.0, 0.0]
for f in range(N):
    if f <= EP: cam.append(keyed(f, KEYS)); c = cam[-1][:]; continue
    r = K["robot"][f]
    if W0 - 10 <= f < W1 + 20: tx, ty = min(64, max(0, dj[r]["cx"] + 56 - 222)), min(72, max(0, dj[r]["by"] + 26 - 126))
    elif f < W0 - 10: tx, ty = 50, 6
    else: tx, ty = 0, 0
    w = 2 * math.pi / 44.0
    for k, t in ((0, tx), (1, ty)):
        a = w * w * (t - c[k]) - 2 * w * v[k]; v[k] += a; c[k] += v[k]
    cam.append([min(64, max(0, c[0])), min(72, max(0, c[1]))])
out = dict(K); out["fps"] = 24; out["cam"] = cam
json.dump(out, open("frames/timeline08.json", "w"))
json.dump({"marks": marks, "N": N, "events": EV, "ring": [RG]}, open("frames/marks08.json", "w"))
print(N, "wide frames", round(N / 24, 1), "s", marks)
