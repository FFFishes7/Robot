"""v15 camera = v13 camera (timeline13) without the slow stray steps, and without v14's native-pixel stepping.
Godot renders world.position = -(cam*5).round(), i.e. the camera lands on OUTPUT pixels (1/5 native).
v13: any stretch where the camera moves slower than ~1 output px per 2 frames shows up as isolated whole-frame jumps:
  * f80..586 drift (50,8) -> (52,6): single 1-px jumps at f205 247 283 318 351 386 519 in a still shot;
  * smoothstep ease tails of the dusk push (f594, 598, 646, 648) and ring pull;
  * the epilogue follow spring: target from the standing robot (cx 236) swung the camera right to x 60 before panning
    left, y went 6 -> 0.5 -> 2 -> 0, and its asymptotic tail crept single pixels until f1197.
v14 put every move on whole native px (5 output px per step): pans became visibly stepped (5 px every 3 frames in the
dusk push / ring pull, irregular 1-2 frame gaps in the final pan next to the walking robot).
v15: the camera is only HOLD (exactly still) or MOVE, positions are whole OUTPUT px (as in v13, so pans stay smooth):
  * the drift is gone: hold (50,8) from f80 to the dusk push;
  * a move keeps the v13 smoothstep speed shape, but the dominant axis never goes below VMIN output px / frame, so it
    steps at least every 2 frames from start to end (no isolated tail steps);
  * the epilogue is one finite move (50,6) -> (0,0) from W0-10 (where the v13 spring started) to the robot reaching
    the window corner (first 'corner_bl' frame): one direction per axis, no settling tail.
Framings are the v13 ones.  Everything else in timeline13 (robot, light, ...) is copied unchanged."""
import json, math, numpy as np
R9 = "/workspace/robot2d/kit/robot09/frames/"
M = json.load(open(R9 + "marks10.json"))["marks"]
DK, RG = M["dusk"], M["ring"]
VMIN = 0.5
def moves(robot):
    W0, CB = robot.index("walk00"), robot.index("corner_bl")
    return [(10, 80, (0, 72), (50, 8)), (DK, DK + 80, (50, 8), (58, 4)), (RG, RG + 30, (58, 4), (50, 6)), (W0 - 10, CB, (50, 6), (0, 0))]
def profile(L, D):
    """dominant-axis output px reached at t = 0..D: smoothstep speed with a floor of VMIN px/frame, total L"""
    assert L >= VMIN * D, (L, D)
    w = np.array([6 * u * (1 - u) for u in ((t + 0.5) / D for t in range(D))])
    lo, hi = 0.0, 4.0 * L / D
    for _ in range(80):
        mid = (lo + hi) / 2; lo, hi = (mid, hi) if np.maximum(VMIN, mid * w).sum() < L else (lo, mid)
    inc = np.maximum(VMIN, hi * w); inc *= L / inc.sum()
    k = np.floor(np.concatenate([[0], np.cumsum(inc)]) + 1e-9).astype(int); k[-1] = L
    return k
def track(n, robot):
    MV = moves(robot); out = [None] * n; cur = (MV[0][2][0] * 5, MV[0][2][1] * 5)
    for f in range(n): out[f] = cur
    for a, b, p0, p1 in MV:
        q0 = (p0[0] * 5, p0[1] * 5); d = ((p1[0] - p0[0]) * 5, (p1[1] - p0[1]) * 5); L = max(map(abs, d))
        k = profile(L, b - a)
        for t in range(b - a + 1):
            out[a + t] = tuple(q0[i] + math.floor(d[i] * k[t] / L + 0.5) for i in (0, 1))
        for f in range(b + 1, n): out[f] = (p1[0] * 5, p1[1] * 5)
    return [[x / 5, y / 5] for x, y in out], MV
def check(cam, MV):
    o = np.round(np.array(cam) * 5).astype(int); bad = []
    if (np.abs(np.array(cam) * 5 - o) > 1e-6).any(): bad.append("off output grid")
    inside = lambda f: any(a < f <= b for a, b, _, _ in MV)
    for f in range(1, len(o)):
        if (o[f] != o[f - 1]).any() and not inside(f): bad.append(("step in hold", f))
    for a, b, p0, p1 in MV:
        seg = np.diff(o[a:b + 1], axis=0)
        for ax in (0, 1):
            if (seg[:, ax] > 0).any() and (seg[:, ax] < 0).any(): bad.append(("reversal", a, ax))
        dom = int(abs(p1[0] - p0[0]) < abs(p1[1] - p0[1]))
        st = [a + 1 + i for i in np.nonzero(seg[:, dom])[0]]
        gaps = np.diff([a] + st + [b])
        if gaps.max() > 2: bad.append(("gap > 2 frames", a, int(gaps.max())))
    return bad
if __name__ == "__main__":
    t = json.load(open(R9 + "timeline13.json")); t["cam"], MV = track(len(t["cam"]), t["robot"])
    print("moves:", MV); print("bad:", check(t["cam"], MV))
    json.dump(t, open(R9 + "timeline15.json", "w")); print("wrote timeline15.json", len(t["cam"]))
