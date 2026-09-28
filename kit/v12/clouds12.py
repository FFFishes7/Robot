"""v12 cumulus: the v11 lobe geometry (clouds11.bank), shaded against the LOW SUN (from the side, slightly below:
sun-facing flanks and undersides catch the light, tops fall into cool shade), 5 tones + a sun-side glow rim."""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); from paths import KIT
sys.path.insert(0, KIT + 'v11')
from scipy.ndimage import gaussian_filter, generic_filter
from clouds11 import bank
def shade(lobes, w, h, L, floor=None):
    L = np.array(L, float) / np.linalg.norm(L)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    acc = np.zeros((h, w)); inside = np.zeros((h, w), bool); k = 2.2
    for (cx, cy, r) in lobes:
        d2 = (xx - cx) ** 2 + (yy - cy) ** 2; m = d2 < r * r
        z = np.sqrt(np.maximum(r * r - d2, 0)) * 0.8 + r * 0.5
        acc += np.where(m, np.exp(np.minimum(z / k, 60) - 30), 0); inside |= m
    Z = np.where(inside, k * (np.log(acc + 1e-300) + 30), 0)
    gy, gx = np.gradient(gaussian_filter(Z, 1.6))
    NX, NY, NZ = -gx, -gy, np.full_like(Z, 1.1); nn = np.sqrt(NX ** 2 + NY ** 2 + NZ ** 2); NX /= nn; NY /= nn; NZ /= nn
    m = inside
    if floor is not None: m &= yy < floor
    s = NX * L[0] + NY * L[1] + NZ * L[2]
    tone = np.digitize(s, [0.25, 0.5, 0.72, 0.88])
    crev = (gaussian_filter(Z, 2.5) - Z) > 1.3; tone[crev & (tone > 0)] -= 1
    tone = np.where(m, tone, -1)
    f = generic_filter(tone + 1, lambda v: np.bincount(v.astype(int), minlength=6).argmax(), size=3, mode='constant') - 1
    tone = np.where(m, np.maximum(f, 0), -1)
    mm = tone >= 0
    edge = mm & (~np.roll(mm, 1, 0) | ~np.roll(mm, -1, 0) | ~np.roll(mm, -1, 1) | ~np.roll(mm, 1, 1))
    rim = edge & ((NX * L[0] + NY * L[1]) > 0.3) & (tone >= 3)
    return tone, rim
def make_banks(seed=5, W=384, HZ=250, sunx=250):
    rng = np.random.RandomState(seed); out = []
    specs = [(-1, 1, 120, 64, 0.62, -30, 26), (-1, 0, 138, 76, 0.78, -46, 4), (1, 1, 112, 58, 0.56, 34, 24), (1, 0, 130, 70, 0.74, 52, 4),
             (-1, 2, 60, 28, 0.34, 112, 70), (1, 2, 54, 24, 0.3, 300, 96), (-1, 2, 46, 22, 0.28, 176, 112)]
    for side, depth, w, h, sc, xoff, lift in specs:
        lb = bank(rng, w, h, -1, n0=7 if depth < 2 else 5, scale=sc)
        xa = min(c[0] - c[2] for c in lb) - 2; ya = min(c[1] - c[2] for c in lb) - 2; xb = max(c[0] + c[2] for c in lb) + 2
        lb = [(c[0] - xa, c[1] - ya, c[2]) for c in lb]; ww = int(xb - xa) + 1; hh = int(h - ya)
        if depth == 2: hh = int(max(c[1] + c[2] for c in lb) + 2)
        if side > 0: lb = [(ww - 1 - c[0], c[1], c[2]) for c in lb]
        fl = hh - 3 - 3 * np.sin(np.arange(ww) / 9.0 + rng.rand() * 6) - 2 * np.sin(np.arange(ww) / 4.3)
        x0 = xoff if side < 0 else W - ww + xoff
        if depth == 2: x0 = xoff
        cx = x0 + ww / 2; lx = 0.7 if cx < sunx else -0.7
        tone, rim = shade(lb, ww, hh, L=(lx, 0.25, 0.65), floor=None if depth == 2 else fl[None, :])
        out.append(dict(tone=tone, rim=rim, x0=int(x0), y0=int(HZ - hh - lift), depth=depth, side=side))
    return out
