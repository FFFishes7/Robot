"""Re-detail an up3 image so every surface carries the same 1-px grain as the wide shot:
top/left 1-px highlights and bottom/right 1-px shades on region boundaries (hue-shifted ramps, no pure black),
plus sparse grain streaks on large flat areas."""
import numpy as np, colorsys
def shade(rgb, k):
    """k>0 lighter (warmer), k<0 darker (cooler, toward purple) -- the room's ramp convention"""
    r, g, b = [v / 255 for v in rgb]; h, l, s = colorsys.rgb_to_hls(r, g, b)
    if k > 0: l = min(0.97, l + 0.09 * k); h = h + (0.12 - h) * 0.12 * k if h < 0.6 else h
    else: l = max(0.05, l + 0.10 * k); h = (h - 0.03 * k) % 1.0; s = min(1, s * (1 - 0.1 * k))
    r, g, b = colorsys.hls_to_rgb(h % 1.0, l, s); return (int(r * 255), int(g * 255), int(b * 255))
def detail(a, keep=None, seed=3, grain=0.035):
    """a: HxWx4 uint8 (up3 output). keep: bool mask of pixels not to touch (lines, emissive)."""
    a = a.copy(); H, W = a.shape[:2]; rng = np.random.RandomState(seed)
    rgb = a[..., :3].astype(int); al = a[..., 3] > 0
    key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    kp = np.zeros((H, W), bool) if keep is None else keep
    def nb(dy, dx):
        k = np.full((H, W), -1); ys = slice(max(0, dy), H + min(0, dy)); yd = slice(max(0, -dy), H + min(0, -dy))
        xs = slice(max(0, dx), W + min(0, dx)); xd = slice(max(0, -dx), W + min(0, -dx))
        k[yd, xd] = np.where(al[ys, xs], key[ys, xs], -1); return k
    up, dn, lf, rt = nb(-1, 0), nb(1, 0), nb(0, -1), nb(0, 1)
    up2, dn2 = nb(-2, 0), nb(2, 0)
    same_in = (dn == key) & (dn2 == key)                      # region continues 2 px below -> a real surface, not a thin line
    hi = al & ~kp & (up != key) & same_in
    lo = al & ~kp & (dn != key) & (up == key) & (up2 == key)
    lf_hi = al & ~kp & (lf != key) & (rt == key) & ~hi & ~lo
    cache = {}
    def sh(c, k):
        if (c, k) not in cache: cache[(c, k)] = shade(((c >> 16) & 255, (c >> 8) & 255, c & 255), k)
        return cache[(c, k)]
    for m, k in ((hi, 1.0), (lf_hi, 0.6), (lo, -1.0)):
        ys, xs = np.nonzero(m)
        for y, x in zip(ys, xs): a[y, x, :3] = sh(int(key[y, x]), k)
    # grain: short 2-3 px streaks one shade darker inside flat interiors
    flat = al & ~kp & (up == key) & (dn == key) & (lf == key) & (rt == key)
    ys, xs = np.nonzero(flat & (rng.rand(H, W) < grain))
    for y, x in zip(ys, xs):
        c = sh(int(key[y, x]), -0.55); L = rng.randint(2, 4)
        for d in range(L):
            if x + d < W and key[y, x + d] == key[y, x] and not kp[y, x + d]: a[y, x + d, :3] = c
    return a
