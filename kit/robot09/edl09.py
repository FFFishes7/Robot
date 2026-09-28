"""Edit decision list for the v08 film: wide spans (Godot chunks) + native close-up inserts."""
import json
M = json.load(open(__file__.rsplit('/', 1)[0] + "/frames/marks09.json")); mk = M["marks"]; N = M["N"]
CH = [0, mk["task_cut"], mk["cal_cut"], mk["face_cut"], mk["press_cut"]]
CL = "/workspace/robot2d/kit/closeups08/"; CL7 = "/workspace/robot2d/kit/closeups07/"
CLIPS = {"task": (CL + "task/f{:03d}.png", 68), "cal": (CL + "cal/f{:03d}.png", 64), "face": (CL7 + "face/f{:03d}.png", 66), "press": (CL + "press/f{:03d}.png", 64)}
EDL = [("wide", 0, mk["task_cut"], 20, 0), ("clip", "task"), ("wide", mk["task_cut"], mk["cal_cut"], 0, 0), ("clip", "cal"),
       ("wide", mk["cal_cut"], mk["face_cut"], 0, 0), ("clip", "face"), ("wide", mk["face_cut"], mk["press_cut"], 0, 0), ("clip", "press"),
       ("wide", mk["press_cut"], N, 0, 40)]
def wide_path(F):
    S = max(s for s in CH if s <= F); return f"/tmp/w9_{S}/f{6 + F - S:08d}.png"
def frames():
    """-> list of (path, gain) for every output frame"""
    out = []
    for e in EDL:
        if e[0] == "wide":
            _, a, b, fin, fout = e
            for F in range(a, b):
                g = 1.0
                if fin and F - a < fin: g = (F - a + 1) / (fin + 1)
                if fout and b - 1 - F < fout: g = min(g, (b - F - 1) / fout)
                out.append((wide_path(F), g))
        else:
            pat, n = CLIPS[e[1]]; out += [(pat.format(t), 1.0) for t in range(n)]
    return out
def out_of_wide(F):
    """output frame index of wide frame F"""
    o = 0
    for e in EDL:
        if e[0] == "wide":
            if e[1] <= F < e[2]: return o + F - e[1]
            o += e[2] - e[1]
        else: o += CLIPS[e[1]][1]
    return o
def clip_start(name):
    o = 0
    for e in EDL:
        if e[0] == "clip" and e[1] == name: return o
        o += (e[2] - e[1]) if e[0] == "wide" else CLIPS[e[1]][1]
def total(): return len(frames())
