"""v07 full-film timeline: wide-shot frames (rendered by Godot) + edit list with close-up inserts and fades."""
import json, math, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import drawings07 as d
dj = json.load(open("frames/drawings.json"))
K = {k: [] for k in ("robot", "alarm", "btn", "cal", "dust", "sun", "beam", "day", "dusk", "lamps", "amb")}
cur = dict(robot="standby", alarm="", btn=0, cal="12", dust=0, sun=0.45, beam=0.6, day=0.75, dusk=0.0, lamps=0.12, amb=1.45)
marks = {}
def mark(n): marks[n] = len(K["robot"])
def hold(n, k, **st):
    cur.update(st); cur["robot"] = n
    for _ in range(k):
        for key in K: K[key].append(cur[key])
def seq(lst, **st):
    for n, k in lst: hold(n, k, **st)
def sweep_cycles(start_i, n_draw, per=3, dust0=0, dust1=7, slow=None):
    tot = n_draw
    for j in range(n_draw):
        i = (start_i + j) % 8; k = per if slow is None else slow(j)
        hold(f"sweep{i+1}", k, dust=round(dust0 + (dust1 - dust0) * j / max(1, tot - 1)))
# ---------------- BEAT 1a: day 12, establishing + routine
mark("day1")
hold("standby", 64, alarm="")
mark("task1"); hold("standby", 16, alarm="task")
seq([("wake1", 6), ("wake2", 4), ("wake3", 8), ("wake_look", 14), ("wake_nod", 10), ("wake3", 5), ("toBroom_qr", 7), ("grab", 6), ("grab2", 3)])
sweep_cycles(4, 24, dust0=0, dust1=7)
hold("sweep4", 3); hold("stop", 8, alarm="off"); seq([("done_nod", 10), ("done_up", 22)])
mark("day1_end")
# ---------------- BEAT 1b: day 13, same program again (shorter)
mark("day2")
hold("standby", 16, alarm="", cal="13", dust=0)
hold("standby", 12, alarm="task")
seq([("wake1", 4), ("wake2", 3), ("wake3", 6), ("wake_look", 10), ("toBroom_qr", 6), ("grab", 5), ("grab2", 3)])
sweep_cycles(4, 16, dust0=0, dust1=3)
# ---------------- BEAT 2: dusk light hits, sweep slows, he stops and looks up
mark("dusk")
DUSK0 = len(K["robot"])
slow = [3, 4, 4, 5, 6, 7]
sweep_cycles(4, 6, dust0=3, dust1=4, slow=lambda j: slow[j])
seq([("sweep2", 6), ("stop", 10), ("notice", 12), ("antic", 5)])
mark("face_cut")                     # face close-up insert (eyes: open -> wide -> blink -> soft) replaces look1/look2
seq([("look3", 6), ("look4", 30), ("look4_blink", 3), ("look4", 14), ("look4_sway", 12), ("look4", 10)])
# ---------------- BEAT 3: alarm rings, hesitation, press
mark("ring")
RING0 = len(K["robot"])
seq([("look4", 3)], alarm="ring")
seq([("startle1", 3), ("startle2", 8), ("hes_alarm", 22), ("hes_front", 5), ("hes_window", 22), ("hes_window_b", 3), ("hes_window", 10),
     ("hes_front", 5), ("hes_alarm2", 16), ("hes_alarm2_nod", 8), ("hes_alarm2", 6),
     ("shuf1", 3), ("shuf2", 3), ("shuf3", 3), ("shuf4", 4), ("reach_antic", 8), ("reach", 4), ("hover", 4)])
mark("dev_cut")                      # device close-up insert
seq([("press_hold", 5)], alarm="off", btn=1)
seq([("release", 5), ("release2", 6)], btn=0)
seq([("after_front", 8)], alarm="idle")
seq([("shufb1", 3), ("shufb2", 3), ("shufb3", 3), ("shufb4", 4), ("lookback", 16), ("lookback2", 12)])
# ---------------- BEAT 4: lean broom, walk to the window seat, sit; sunset fades, room lights glow
mark("epi")
EPI0 = len(K["robot"])
seq([("place1", 8), ("place2", 10), ("stand_qr", 6), ("stand_front", 5), ("stand_ql", 5), ("stand_l", 6)])
WALK0 = len(K["robot"])
for i in range(d.WALK_N):
    if i == 66: hold("corner_bl", 2)
    hold(f"walk{i:02d}", 1)
WALK1 = len(K["robot"])
seq([("arrive_back", 10), ("arrive_look", 16), ("hop_antic", 6), ("hop", 4), ("land", 4), ("sit", 8)])
SIT0 = len(K["robot"])
def idle(nf, breath_at=()):
    for j in range(nf): hold("sit_breath" if any(b <= j < b + 6 for b in breath_at) else f"sit_idle{(j // 8) % 4}", 1)
idle(40, (22,)); hold("sit_lean", 20); idle(62, (18, 48))
N = len(K["robot"])
# ---------------- light curves (smooth)
def ss(t): t = min(1.0, max(0.0, t)); return t * t * (3 - 2 * t)
for f in range(N):
    if f >= DUSK0:
        h = ss((f - DUSK0) / 30)                          # dusk light floods in over ~1.2 s
        e = ss((f - RING0) / (N - 1 - RING0))             # then the sun sinks for the rest of the film
        e2 = ss((f - EPI0) / (N - 1 - EPI0))
        K["sun"][f] = 0.45 + 0.55 * h - 0.7 * (0.35 * e + 0.65 * e2)
        K["beam"][f] = 0.6 + 0.4 * h - 0.45 * (0.3 * e + 0.7 * e2)
        K["day"][f] = 0.75 * (1 - h)
        K["dusk"][f] = 0.15 * e + 0.85 * e2
        K["lamps"][f] = 0.12 + 0.28 * h + 1.35 * (0.25 * e + 0.75 * e2)
        K["amb"][f] = 1.45 - 0.45 * h - 0.12 * e2
# ---------------- camera (top-left of the 384x216 window, native px; world 448x288)
def keyed(f, keys):
    for (a, pa), (b, pb) in zip(keys, keys[1:]):
        if f <= b:
            t = ss((f - a) / (b - a)); return [pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t]
    return list(keys[-1][1])
D2 = marks["day2"]
KEYS = [(0, (0, 72)), (10, (0, 72)), (84, (50, 8)), (D2 - 1, (52, 6)), (D2, (52, 6)), (DUSK0, (52, 6)), (DUSK0 + 60, (58, 4)), (RING0, (58, 4)),
        (RING0 + 30, (50, 6)), (EPI0, (50, 6))]
cam = []; c = [50.0, 6.0]; v = [0.0, 0.0]
for f in range(N):
    if f <= EPI0: cam.append(keyed(f, KEYS)); c = cam[-1][:]; continue
    n = K["robot"][f]
    if WALK0 - 10 <= f < WALK1 + 20: tx, ty = min(64, max(0, dj[n]["cx"] + 56 - 222)), min(72, max(0, dj[n]["by"] + 26 - 126))
    elif f < WALK0 - 10: tx, ty = 50, 6
    else: tx, ty = 0, 0
    w = 2 * math.pi / 44.0
    for k, t in ((0, tx), (1, ty)):
        a = w * w * (t - c[k]) - 2 * w * v[k]; v[k] += a; c[k] += v[k]
    cam.append([min(64, max(0, c[0])), min(72, max(0, c[1]))])
out = dict(K); out["fps"] = 24; out["cam"] = cam
json.dump(out, open("frames/timeline07.json", "w"))
json.dump({"marks": marks, "N": N}, open("frames/marks07.json", "w"))
print(N, "wide frames", N / 24, "s", marks)
