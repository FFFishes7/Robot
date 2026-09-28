"""v11 insets: EXACT native pixels of the wide shot, enlarged by pure integer nearest-neighbour (x3).
Native pixel (wx, wy) of the world is read at the centre of its 5x5 block in the final wide frame
(block origin = wx*5 - round(cam_x*5)), i.e. the crop is aligned to the native grid, no resampling."""
import sys, json, os, numpy as np
sys.path.insert(0, '/workspace/robot2d/kit/v10'); sys.path.insert(0, '/workspace/robot2d/kit/robot10')
import panels10 as P
from PIL import Image
REG = dict(task=(198, 50, 250, 74), cal=(174, 46, 216, 72), face=(213, 40, 259, 72), press=(198, 50, 250, 74))
OPEN = [0.2, 0.45, 0.7, 0.9]
CFX = json.load(open("/tmp/p10/calfx.json"))
def up5(a): return np.repeat(np.repeat(a, 5, 0), 5, 1)
def wide_base(F):
    """the wide frame as it appears in the film (incl. page-turn patch), before any inset"""
    a = np.array(Image.open(P.wide_path(F)).convert("RGB"))
    if str(F) in CFX:
        p = np.array(Image.open(f"/tmp/p10/calfx_{F}.png")); bx, by = CFX[str(F)]; cx, cy = P.cam(F)
        X, Y = bx * 5 - cx, by * 5 - cy; q = up5(p); m = q[..., 3] > 0
        sub = a[Y:Y + q.shape[0], X:X + q.shape[1]]; sub[m] = q[..., :3][m]
    return a
def native_crop(a, F, reg):
    cx, cy = P.cam(F)
    x0, y0, x1, y1 = reg[0] + P.OX, reg[1] + P.OY, reg[2] + P.OX, reg[3] + P.OY
    ys = np.arange(y0, y1) * 5 - cy + 2; xs = np.arange(x0, x1) * 5 - cx + 2
    assert ys.min() >= 0 and xs.min() >= 0 and ys.max() < 1080 and xs.max() < 1920, (F, reg)
    return a[ys[:, None], xs[None, :]]
def inset(F, name):
    nat = native_crop(wide_base(F), F, REG[name])
    c = np.repeat(np.repeat(nat, 3, 0), 3, 1)                     # pure integer nearest-neighbour
    rgba = np.concatenate([c, np.full(c.shape[:2] + (1,), 255, np.uint8)], -1)
    return rgba, nat
def main(names):
    os.makedirs('/tmp/p11', exist_ok=True)
    idx = json.load(open('/tmp/p11/index.json')) if os.path.exists('/tmp/p11/index.json') else {}
    for name in names:
        a, b = P.MK["panels"][name]; n = b - a
        for F in range(a, b):
            c, _ = inset(F, name)
            j = F - a; t = 1.0
            if j < 4: t = OPEN[j]
            if n - 1 - j < 4: t = OPEN[n - 1 - j]
            fr = P.frame(c, t)
            Image.fromarray(fr).save(f'/tmp/p11/{F}.png'); idx[str(F)] = [name, 8, 216 - 6 - fr.shape[0]]
        print(name, a, b, flush=True)
    json.dump(idx, open('/tmp/p11/index.json', 'w'))
if __name__ == '__main__':
    main(sys.argv[1].split(','))
