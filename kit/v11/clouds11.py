"""v11 cumulus banks: a heightfield built as the max of many sphere lobes (big body lobes along the bank + 3
generations of smaller lobes budding off the upper surface, irregular radii), shaded by the lobe normals
(light from the low sun at upper right / front), posterised to 5 tones + a lit silhouette rim + cool undersides,
majority-cleaned. Returns per-bank index sprites (tone map, -1 = empty) coloured per frame."""
import numpy as np
from scipy.ndimage import generic_filter
def bank(rng, w, h, side, n0=7, scale=1.0):
    """lobes (cx, cy, r) inside a w x h sprite; bank grows taller toward the outer edge (side -1 = left bank)"""
    lobes = []
    for i in range(n0):
        u = i / (n0 - 1)                                      # 0 inner .. 1 outer
        outer = u if side > 0 else 1 - u
        cx = w * (0.12 + 0.76 * u) + rng.uniform(-4, 4)
        r = scale * (12 + 16 * (1 - outer) ** 0 * (0.5 + outer)) * rng.uniform(0.8, 1.15)
        cy = h - r * 0.55 - outer * h * 0.30 + rng.uniform(-3, 3)
        lobes.append((cx, cy, r))
    for gen, (cnt, rf) in enumerate(((10, 0.55), (18, 0.38), (30, 0.24))):
        base = list(lobes)
        for _ in range(cnt):
            px, py, pr = base[rng.randint(len(base))]
            a = rng.uniform(-2.7, -0.45)                      # upper hemisphere (y down)
            r = pr * rf * rng.uniform(0.75, 1.25)
            cx = px + np.cos(a) * pr * 0.92; cy = py + np.sin(a) * pr * 0.92
            if r > 2.2 and cy + r < h: lobes.append((cx, cy, r))
    return lobes
def shade_bank(lobes, w, h, L=(0.55, -0.55, 0.62), floor=None):
    L = np.array(L) / np.linalg.norm(L)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    acc = np.zeros((h, w)); inside = np.zeros((h, w), bool); k = 2.2; zmax = np.zeros((h, w))
    for (cx, cy, r) in lobes:
        d2 = (xx - cx) ** 2 + (yy - cy) ** 2; m = d2 < r * r
        z = np.sqrt(np.maximum(r * r - d2, 0)) * 0.8 + r * 0.5
        acc += np.where(m, np.exp(np.minimum(z / k, 60) - 30), 0); inside |= m; zmax = np.maximum(zmax, np.where(m, z, 0))
    Z = np.where(inside, k * (np.log(acc + 1e-300) + 30), 0)
    from scipy.ndimage import gaussian_filter
    Zs = gaussian_filter(Z, 1.6)
    gy, gx = np.gradient(Zs)
    NX = -gx; NY = -gy; NZ = np.ones_like(Z) * 1.1
    nn = np.sqrt(NX ** 2 + NY ** 2 + NZ ** 2); NX /= nn; NY /= nn; NZ /= nn
    Zmin = Z
    m = inside
    s = NX * L[0] + NY * L[1] + NZ * L[2]
    tone = np.digitize(s, [0.15, 0.45, 0.72, 0.9])           # 0 shadow .. 4 highlight
    tone[(NY > 0.35) & (tone > 1)] = 1                       # undersides fall into cool shadow
    tone[(NY > 0.6)] = 0
    crev = (gaussian_filter(Z, 2.5) - Z) > 1.3; tone[crev & (tone > 0)] -= 1
    tone = np.where(m, tone, -1)
    f = generic_filter(tone + 1, lambda v: np.bincount(v.astype(int), minlength=6).argmax(), size=3, mode='constant') - 1
    tone = np.where(m, np.maximum(f, 0), -1)
    # lit silhouette rim on the sun-facing top edges
    edge = m & (~np.roll(m, 1, 0) | ~np.roll(m, -1, 1) | ~np.roll(m, 1, 1))
    rim = edge & (NY < 0.1) & (NX * np.sign(L[0]) > -0.3)
    return tone, rim
def make_banks(seed=5, W=384, HZ=250):
    rng = np.random.RandomState(seed); out = []
    for side in (-1, 1):
        for depth in (1, 0):
            w, h = (140, 78) if depth == 0 else (124, 66)
            lb = bank(rng, w, h, -1, n0=7 if depth == 0 else 6, scale=0.8 if depth == 0 else 0.64)
            xa = min(c[0] - c[2] for c in lb) - 2; ya = min(c[1] - c[2] for c in lb) - 2
            xb = max(c[0] + c[2] for c in lb) + 2
            lb = [(c[0] - xa, c[1] - ya, c[2]) for c in lb]; w = int(xb - xa) + 1; h = int(h - ya)
            if side > 0: lb = [(w - 1 - c[0], c[1], c[2]) for c in lb]; xa = 140 - xb
            # irregular base: a wavy floor line close to the sprite bottom
            fl = h - 3 - 3 * np.sin(np.arange(w) / 9.0 + rng.rand() * 6) - 2 * np.sin(np.arange(w) / 4.3)
            tone, rim = shade_bank(lb, w, h, L=(0.55 if side < 0 else -0.45, -0.55, 0.62), floor=fl[None, :])
            x0 = int(xa) + ((-30 + 44 * depth) if side < 0 else (W - 140 + 30 - 44 * depth))
            y0 = HZ - h + 10 - 16 * depth
            out.append(dict(tone=tone, rim=rim, x0=x0, y0=y0, depth=depth, side=side))
    return out
