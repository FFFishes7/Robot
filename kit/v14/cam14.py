"""v14 camera: exact integer native grid in every frame, no stray steps.
v13 scan (see jitter_report_v13.md): the whole frame shifted by 1 OUTPUT pixel (= 1/5 native px, off the native grid)
in rare isolated steps. Causes in the v10-v13 camera (timeline10.py; Godot does world.position = -(cam*5).round()):
  * f 80..586: key (80,(50,8)) -> (586,(52,6)) eased over 506 frames = an ultra-slow drift toward the upper right
    (2 native px in 21 s), i.e. isolated 1-output-px jumps at film f148 204 246 282 317 350 385 518 (0:08.5, 0:10.25 = the
    moment the wall device switches to the check screen, ...), each also leaving the frame off the native grid.
  * every move was quantised to OUTPUT pixels (1/5 native), so all pans ran off-grid, with sparse ease tails.
  * f 1085..1196: the robot-follow spring swung right 10 native px and then panned left (back and forth), and its
    asymptotic tail crept the last output pixels in isolated steps up to f1196.
v14: the camera is only HOLD or MOVE, always on integer native pixels (so the render offset is a multiple of 5 output px).
  * the drift is removed: hold (50,8) from f80 until the dusk push.
  * each move advances a step counter k = 0..K along its line (K = max |dx|,|dy| native px; x and y step together),
    driven by a trapezoid speed profile whose ends never drop below 1 step / 3 frames -> regular cadence, monotonic,
    no isolated single steps. Short 8-px moves (dusk push, ring pull) therefore run at a steady 1 px / 3 frames.
Kept framings: (0,72) -> (50,8) intro pan, dusk push to (58,4), ring pull back to (50,6), final pan to (0,0) as the robot
walks to the window (v13 spring left (50,6) at f1084 and reached (0,0) at ~f1165)."""
import json, numpy as np
M = json.load(open("/workspace/robot2d/kit/robot09/frames/marks10.json"))["marks"]
DK, RG = M["dusk"], M["ring"]
V0 = 1 / 3.0                                             # slowest cadence at the ends of a move: 1 native px / 3 frames
# (start frame, duration, from, to); holds in between
MOVES = [(10, 70, (0, 72), (50, 8)), (DK, 24, (50, 8), (58, 4)), (RG, 24, (58, 4), (50, 6)), (1084, 84, (50, 6), (0, 0))]
def profile(K, D):
    """k(t) for t = 0..D: integral of a trapezoid speed (V0 at the ends, vm in the middle), total K, rounded, monotonic"""
    R = max(1.0, D / 4.0)
    def total(vm):
        return sum(V0 + (vm - V0) * min(1.0, (t + 0.5) / R, (D - t - 0.5) / R) for t in range(D))
    lo, hi = V0, 10.0
    if total(lo) >= K: vm = K / D; spd = [vm] * D                   # short move: steady cadence
    else:
        for _ in range(60):
            mid = (lo + hi) / 2; lo, hi = (mid, hi) if total(mid) < K else (lo, mid)
        spd = [V0 + (lo - V0) * min(1.0, (t + 0.5) / R, (D - t - 0.5) / R) for t in range(D)]
    s = np.concatenate([[0], np.cumsum(spd)]); s *= K / s[-1]
    k = np.floor(s + 1e-9).astype(int); k[-1] = K
    return np.maximum.accumulate(k)
def track(n):
    pos = [None] * n; cur = MOVES[0][2]
    for f in range(n): pos[f] = cur
    for (a, D, p0, p1) in MOVES:
        K = max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1])); k = profile(K, D)
        for t in range(D + 1):
            if a + t < n: pos[a + t] = (p0[0] + round((p1[0] - p0[0]) * k[t] / K), p0[1] + round((p1[1] - p0[1]) * k[t] / K))
        for f in range(a + D + 1, n): pos[f] = p1
    return [[float(x), float(y)] for x, y in pos]
def check(cam):
    c = np.array(cam); bad = []
    if (c != np.round(c)).any(): bad.append("off native grid")
    for f in range(1, len(c)):
        if (c[f] != c[f - 1]).any() and not any(a < f <= a + D for a, D, _, _ in MOVES): bad.append(("step in hold", f))
    for a, D, p0, p1 in MOVES:
        for ax in (0, 1):
            d = np.diff(c[a:a + D + 1, ax])
            if (d > 0).any() and (d < 0).any(): bad.append(("reversal", a, ax))
        st = [f for f in range(a + 1, a + D + 1) if (c[f] != c[f - 1]).any()]
        gaps = np.diff([a] + st + [a + D + 1]); 
        if gaps.max() > 3: bad.append(("gap > 3 frames", a, int(gaps.max())))
    return bad
if __name__ == "__main__":
    R9 = "/workspace/robot2d/kit/robot09/frames/"
    t = json.load(open(R9 + "timeline13.json")); t["cam"] = track(len(t["cam"]))
    print("bad:", check(t["cam"]))
    json.dump(t, open(R9 + "timeline14.json", "w")); print("wrote timeline14.json", len(t["cam"]))
