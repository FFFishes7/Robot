"""Layered 2.5D ridge rows (Stardew title-screen structure): each row is a small relief field h(x,u) (big rounded
peaks + ridged folds), raymarched with a y-buffer, shaded from its normal, posterised to 4 tones + crest rim.
Output: index maps (row id, tone 0..4, valley-depth) -> coloured per frame."""
import numpy as np
from scipy.ndimage import gaussian_filter
def smooth_noise(rng, shape, sx, sy):
    g = gaussian_filter(rng.randn(*shape), (sy, sx), mode='wrap'); return g / (g.std() + 1e-9)
def row_field(rng, W, U, npk, width, fold_s):
    x = np.arange(W)[None, :]; u = np.linspace(0, 1, U)[:, None]
    h = np.zeros((U, W))
    for q in range(npk):
        px = rng.uniform(-40, W + 40); pu = rng.uniform(0.25, 0.85); a = rng.uniform(0.55, 1.0); w = width * rng.uniform(0.7, 1.4)
        h += a * np.exp(-((x - px) / w) ** 2 - ((u - pu) / 0.32) ** 2)
    # ridged folds running down the slopes (stretched along u = the fall line in this view)
    n = smooth_noise(rng, (U, W), fold_s * 0.5, 14.0)                     # long streaks along the fall line
    folds = np.clip(1 - np.abs(n), 0, 1) ** 2
    h = h + 0.10 * folds * np.clip(h, 0, None) ** 0.5 + 0.02 * smooth_noise(rng, (U, W), 30, 10)
    return gaussian_filter(h, (0.8, 1.0))
def render_rows(W=384, CH=336, HZ=250, seed=7, light=(0.8, 0.55)):
    """rows far->near. returns row (int, -1 none), tone (0 deep..3 highlight), rim bool, vfrac (0 crest..1 base)"""
    rng = np.random.RandomState(seed)
    rows = [  # base y, amplitude, depth rise, peaks, peak width, fold scale
        (HZ + 2, 12, 6, 11, 26, 3), (HZ + 14, 15, 8, 10, 32, 3), (HZ + 28, 19, 10, 9, 38, 4),
        (HZ + 45, 24, 12, 8, 46, 4), (HZ + 66, 30, 14, 7, 54, 5), (HZ + 92, 36, 16, 6, 62, 5)]
    ROW = np.full((CH, W), -1); TONE = np.zeros((CH, W), int); RIM = np.zeros((CH, W), bool); VF = np.zeros((CH, W))
    for k, (yb, A, D, npk, wd, fs) in enumerate(rows):
        U = 90; h = row_field(rng, W, U, npk, wd, fs)
        gu, gx = np.gradient(h)
        ybuf = np.full(W, CH, int); top = np.full(W, CH, int)
        tone_k = np.zeros((CH, W), int); drawn = np.zeros((CH, W), bool); vf = np.zeros((CH, W))
        for i in range(U):                      # near (u=0) -> far (u=1)
            u = i / (U - 1)
            ys = np.round(yb - A * h[i] - u * D).astype(int)
            # normal in screen terms: x-slope and "facing up" (u-slope)
            nx = -gx[i] * A * 0.9; ny = 1.0 + np.maximum(0, gu[i]) * A * 0.02
            s = (nx * light[0] + ny * light[1]) / np.sqrt(nx * nx + ny * ny)
            t = np.digitize(s, [0.05, 0.42, 0.72, 0.9])        # 0 deep shadow .. 4 highlight
            for x in range(W):
                y = max(0, ys[x])
                if y < ybuf[x]:
                    tone_k[y:ybuf[x], x] = t[x] if i > 0 else 0; drawn[y:ybuf[x], x] = True
                    ybuf[x] = y
        # crest rim + vertical fraction (crest -> base) for the valley haze
        for x in range(W):
            if ybuf[x] < CH:
                RIM_y = ybuf[x]; col = drawn[:, x]
                vfx = (np.arange(CH) - ybuf[x]) / max(8.0, yb + 6 - ybuf[x])
                vf[:, x] = np.clip(vfx, 0, 1)
        m = drawn
        ROW[m] = k; TONE[m] = tone_k[m]; VF[m] = vf[m]
        rim_k = m & ~np.roll(m, 1, 0) & (np.roll(tone_k, -1, 0) >= 2); RIM[m] = False; RIM |= rim_k
    # clean isolated tone specks (majority of 3x3 within the same row)
    from scipy.ndimage import generic_filter
    def maj(v):
        c = np.bincount(v.astype(int), minlength=5); return c.argmax()
    T2 = TONE.copy()
    for k in range(len(rows)):
        m = ROW == k
        if not m.any(): continue
        t = np.where(m, TONE, -1).astype(float)
        f = generic_filter(np.where(m, TONE, 0), maj, size=3, mode='nearest')
        T2[m] = f[m]
    return dict(row=ROW, tone=T2, rim=RIM, vf=VF, n=len(rows))
if __name__ == '__main__':
    import time; t0 = time.time(); r = render_rows(); print(time.time() - t0)
    np.savez_compressed('/tmp/hills11.npz', **r)
    from PIL import Image
    CH, W = r['row'].shape; img = np.zeros((CH, W, 3), np.uint8); img[:] = (70, 60, 110)
    base = [(170, 130, 160), (130, 100, 150), (100, 76, 130), (74, 56, 106), (52, 40, 84)]
    for k in range(r['n']):
        for t in range(5):
            m = (r['row'] == k) & (r['tone'] == t)
            c = np.array(base[k]) * (0.62 + 0.14 * t) + np.array([60, 30, 0]) * (t >= 3)
            img[m] = np.clip(c, 0, 255)
    img[r['rim']] = (240, 190, 150)
    Image.fromarray(img[180:]).resize((1152, 468), Image.NEAREST).save('/tmp/v9chk/hills_a.png')
