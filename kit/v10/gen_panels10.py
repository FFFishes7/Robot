"""Render every inset frame (derived from the scene at that wide frame) -> build/p10/<F>.png (framed RGBA, native px)
+ build/p10/index.json {F: [name, x, y]} (screen-native top-left). Also native page-turn patches for the wide."""
import sys, json, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); from paths import KIT, BUILD
sys.path.insert(0, KIT + 'v10')
import panels10 as P
from PIL import Image
P10 = BUILD + 'p10/'
REG = dict(task=(198, 50, 250, 74), cal=(174, 46, 216, 72), face=(213, 40, 259, 72), press=(198, 50, 250, 74))
def pol_task(r, i): r = P.glass(r, i); return P.eyes(r, i)
def pol_face(r, i):
    r = P.glass(r, i, tint=(170, 120, 150), warm=(214, 120, 90)); r = P.eyes(r, i, catch=(255, 196, 130)); return P.rim(r, i, (255, 190, 120), 1, 0.5)
POL = dict(task=pol_task, cal=None, face=pol_face, press=pol_task)
OPEN = [0.2, 0.45, 0.7, 0.9]
def main(names):
    os.makedirs(P10, exist_ok=True)
    idx = json.load(open(P10 + 'index.json')) if os.path.exists(P10 + 'index.json') else {}
    for name in names:
        a, b = P.MK["panels"][name]; n = b - a
        for F in range(a, b):
            c, info = P.render(F, REG[name], polish=POL[name])
            j = F - a; t = 1.0
            if j < 4: t = OPEN[j]
            if n - 1 - j < 4: t = OPEN[n - 1 - j]
            fr = P.frame(c, t)
            Image.fromarray(fr).save(f'{P10}{F}.png')
            idx[str(F)] = [name, 8, 216 - 6 - fr.shape[0]]
        print(name, a, b, flush=True)
    json.dump(idx, open(P10 + 'index.json', 'w'))
def calfx_patches():
    """page-turn pixels graded like the scene at that frame -> build/p10/calfx_<F>.png (world-native RGBA, box origin in json)"""
    os.makedirs(P10, exist_ok=True)
    out = {}
    for F in range(len(P.TL["calfx"])):
        k = int(P.TL["calfx"][F])
        if not k: continue
        fx = P.L(P.K + f"v10/calfx/calfx{k}.png"); m = fx[..., 3] > 0
        ys, xs = np.nonzero(m); bx = (xs.min() - 6, ys.min() - 6, xs.max() + 7, ys.max() + 7)
        a, cls, r = P.compose(F)
        A = a[bx[1]:bx[3], bx[0]:bx[2]]; Cc = cls[bx[1]:bx[3], bx[0]:bx[2]]
        big = (bx[0] - 30, bx[1] - 30, bx[2] + 30, bx[3] + 30)
        Ab = a[big[1]:big[3], big[0]:big[2]]; Cb = cls[big[1]:big[3], big[0]:big[2]]; Wd, ok = P.sample_wide(F, big)
        Ag, _ = P.grade_native(Ab, Cb, Wd, ok)
        # the flip pixels themselves: map fx colours through the graded LUT of the matching paper/outline colours
        sub = Ag[30:-30, 30:-30]; mm = m[bx[1]:bx[3], bx[0]:bx[2]]
        rgba = np.zeros(sub.shape[:2] + (4,), np.uint8); rgba[..., :3] = sub.astype(np.uint8); rgba[..., 3] = np.where(mm, 255, 0)
        Image.fromarray(rgba).save(f'{P10}calfx_{F}.png'); out[str(F)] = [int(bx[0]), int(bx[1])]
    json.dump(out, open(P10 + 'calfx.json', 'w')); print("calfx", out)
if __name__ == '__main__':
    if sys.argv[1] == 'calfx': calfx_patches()
    else: main(sys.argv[1].split(','))
