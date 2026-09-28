# full story cut (~14 s): the 6 s loop, then lean the broom, walk to the window seat, hop up, sit and watch the sunset.
import json, math, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import drawings as d
base = json.load(open("frames/timeline.json"))
T = list(base["robot"]); alarm = list(base["alarm"])
def add(n, k): T.extend([n] * k)
for n, k in [("lookback", 4), ("place1", 6), ("place2", 6), ("turnL", 8)]: add(n, k)
for i in range(d.WALK_N): add(f"walk{i:02d}", 1)
for n, k in [("arrive_up", 8), ("hop_antic", 5), ("hop", 4), ("land", 3), ("sit_e", 10)]: add(n, k)
def idle(nf, breath_at=()):
    for j in range(nf):
        add("sit_breath" if any(b <= j < b + 6 for b in breath_at) else f"sit_idle{(j // 7) % 4}", 1)
idle(40, (22,)); add("sit_lean_e", 16); idle(30, (12,))
alarm += ["off"] * (len(T) - len(alarm))
dj = json.load(open("frames/drawings.json"))
rx = [dj[n]["cx"] - d.CX for n in T]; ry = [dj[n]["by"] - d.BY for n in T]
# camera: the loop's keyed moves, then a damped follow of the robot (native px, top-left of the 384x216 window)
KEYS = [(0, (54, 20)), (64, (60, 10)), (92, (58, 8)), (128, (50, 5)), (143, (50, 5))]
def keyed(f):
    for (a, pa), (b, pb) in zip(KEYS, KEYS[1:]):
        if f <= b:
            t = (f - a) / (b - a); t = t * t * (3 - 2 * t)
            return (pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t)
    return KEYS[-1][1]
cam = []; c = keyed(143); v = [0.0, 0.0]
for f, n in enumerate(T):
    if f <= 143: cam.append(list(keyed(f))); continue
    walking = n.startswith("walk") or n.startswith("arrive") or n.startswith("hop")
    tx = min(64, max(0, dj[n]["cx"] + 56 - 240)) if walking else c[0]; ty = min(72, max(0, dj[n]["by"] + 26 - 128)) if walking else c[1]
    if f > 150 + d.WALK_N: tx, ty = 0, 0                   # settle on the window seat framing
    for k, t in ((0, tx), (1, ty)):                        # critically damped spring, ~0.6 s
        w = 2 * math.pi / 40.0; a = w * w * (t - c[k]) - 2 * w * v[k]; v[k] += a; c = (c[0] + v[0], c[1]) if k == 0 else (c[0], c[1] + v[1])
    cam.append([min(64, max(0, c[0])), min(72, max(0, c[1]))])
def sun(f):   # the sun sinks while he watches: sunlight fades to ~40% over the last few seconds
    t = min(1.0, max(0.0, (f - 262) / (len(T) - 1 - 262))); t = t * t * (3 - 2 * t); return 1.0 - 0.6 * t
json.dump({"fps": 24, "robot": T, "alarm": alarm, "rx": rx, "ry": ry, "cam": cam, "sun": [sun(f) for f in range(len(T))]}, open("frames/timeline_full.json", "w"))
print(len(T), "frames", len(T) / 24, "s")
