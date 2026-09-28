"""v11 hills, take 2: each ridge row is a heightfield z(depth u, x) of pointed-rounded mountains + short isotropic
ridged spurs (weighted by slope, so they cluster on the flanks), shaded by a 3D normal against a low sun to the
upper right, posterised to 5 tones, raymarched near->far with a y-buffer. Output = index maps, coloured per frame."""
import numpy as np
from scipy.ndimage import gaussian_filter, generic_filter
def sn(rng, shape, s):
    g = gaussian_filter(rng.randn(*shape), s, mode='wrap'); return g / (g.std() + 1e-9)
def row_field(rng, W, U, npk, width):
    x = np.arange(W)[None, :]; u = np.linspace(0, 1, U)[:, None]
    h = np.zeros((U, W))
    for q in range(npk):
        px = (q + rng.uniform(0.1, 0.9)) * (W + 80) / npk - 40; pu = rng.uniform(0.35, 0.8)
        a = rng.uniform(0.6, 1.0); w = width * rng.uniform(0.75, 1.3)
        r = np.sqrt(((x - px) / w) ** 2 + ((u - pu) / 0.30) ** 2)
        h = np.maximum(h, a * np.exp(-r ** 1.45 * 1.5))             # max(): distinct peaks with saddles between
    spur = (1 - np.abs(sn(rng, (U, W), (3.5, 2.4)))) ** 3           # short ridged spurs
    gu, gx = np.gradient(h); slope = np.clip(np.sqrt(gx ** 2 + (gu / 12) ** 2) * 40, 0, 1)
    h = h + 0.11 * spur * slope + 0.025 * sn(rng, (U, W), (6, 16))
    return gaussian_filter(h, (1.0, 1.2))
ROWS = [  # base y, amplitude, depth rise, peaks, peak width
    (8, 14, 4, 12, 20), (17, 17, 6, 10, 24), (28, 21, 7, 9, 29),
    (42, 26, 9, 8, 34), (59, 31, 10, 7, 40), (80, 36, 12, 6, 47)]
def render_rows(W=384, CH=336, HZ=250, seed=11, L=(0.62, -0.25, 0.74)):
    rng = np.random.RandomState(seed)
    L = np.array(L) / np.linalg.norm(L)
    ROW = np.full((CH, W), -1); TONE = np.zeros((CH, W), int); RIM = np.zeros((CH, W), bool); VF = np.zeros((CH, W))
    for k, (yb0, A, D, npk, wd) in enumerate(ROWS):
        yb = HZ + yb0; U = 110; h = row_field(rng, W, U, npk, wd)
        gu, gx = np.gradient(h)
        dzdx = gx * A; dzdd = gu * A / (D * 1.6 / U) / 6.0           # depth units ~ foreshortened
        n = np.stack([-dzdx, -dzdd, np.ones_like(h)], -1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
        s = n @ L
        tq = np.digitize(s, [0.42, 0.64, 0.8, 0.92])
        ybuf = np.full(W, CH, int); tone_k = np.zeros((CH, W), int); drawn = np.zeros((CH, W), bool)
        for i in range(U):
            ys = np.round(yb - A * h[i] - (i / (U - 1)) * D).astype(int)
            for x in np.nonzero(ys < ybuf)[0]:
                y = max(0, ys[x]); tone_k[y:ybuf[x], x] = tq[i, x]; drawn[y:ybuf[x], x] = True; ybuf[x] = y
        vf = np.clip((np.arange(CH)[:, None] - ybuf[None]) / np.maximum(10.0, yb + 4 - ybuf)[None], 0, 1)
        m = drawn
        # majority cleanup of tone specks (row-local)
        f = generic_filter(np.where(m, tone_k, 0), lambda v: np.bincount(v.astype(int), minlength=5).argmax(), size=3, mode='nearest')
        tone_k = np.where(m, f, 0)
        ROW[m] = k; TONE[m] = tone_k[m]; VF[m] = vf[m]
        top = m & ~np.roll(m, 1, 0)
        RIM[top] = False; RIM |= top & (np.maximum(tone_k, np.roll(tone_k, -1, 0)) >= 3)
        RIM[m & ~top] = False
    return dict(row=ROW, tone=TONE, rim=RIM, vf=VF, n=len(ROWS))
