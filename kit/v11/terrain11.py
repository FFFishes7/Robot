"""Voxel-space raymarch of a ridged-noise mountain heightmap -> per-pixel (shade, fog, rim) index maps for the
panorama. Rendered once; colours are applied per frame from the palette (sunset -> dusk -> night)."""
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates
def fbm(n, seed, scales=((96, 1.0), (40, 0.5), (16, 0.25), (6, 0.1))):
    rng = np.random.RandomState(seed); out = np.zeros((n, n))
    for s, a in scales:
        g = gaussian_filter(rng.randn(n, n), s, mode='wrap'); out += a * g / g.std()
    return out
def heightmap(n=1024, seed=3):
    base = fbm(n, seed, ((140, 1.0), (60, 0.55)))
    rid = 1 - np.abs(fbm(n, seed + 1, ((36, 1.0), (14, 0.45))))          # ridged: sharp-but-rounded crests + gullies
    rid = gaussian_filter(np.clip(rid, 0, 1), 1.6, mode='wrap')
    H = 40 * base + 70 * rid ** 2
    return gaussian_filter(H, 1.2, mode='wrap')
def render(Hm=None, W=384, Hs=150, hz=24, seed=3, cam_h=95.0, f=260.0, z0=20.0, z1=900.0, light=(0.75, -0.25, 0.6)):
    """returns dict of float maps (Hs x W): shade in [-1,1], fog in [0,1], depth, rim bool; hz = horizon row inside"""
    Hm = heightmap(seed=seed) if Hm is None else Hm; n = Hm.shape[0]
    gy, gx = np.gradient(Hm)
    L = np.array(light, float); L /= np.linalg.norm(L)
    ybuf = np.full(W, Hs, int)
    shade = np.zeros((Hs, W)); fog = np.ones((Hs, W)); depth = np.full((Hs, W), z1); rim = np.zeros((Hs, W), bool)
    sky = np.ones((Hs, W), bool)
    xs = (np.arange(W) - W / 2) / f
    z = z0; cz, cx = 200.0, 300.0
    while z < z1:
        wx = cx + xs * z * 1.0; wz = np.full(W, cz + z)
        h = map_coordinates(Hm, [wz % n, wx % n], order=1, mode='wrap')
        dx = map_coordinates(gx, [wz % n, wx % n], order=1, mode='wrap'); dz = map_coordinates(gy, [wz % n, wx % n], order=1, mode='wrap')
        nrm = np.stack([-dx, np.full(W, 1.0), -dz], -1); nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
        # light: x = right, y = up, z = away  (dz is along +z)
        s = nrm[:, 0] * L[0] + nrm[:, 1] * L[1] + (-nrm[:, 2]) * L[2]
        ys = (hz + (cam_h - h) * f / z).astype(int)
        fz = min(1.0, max(0.0, (z - z0) / (z1 - z0))) ** 0.7
        for x in range(W):
            y = max(0, ys[x])
            if y < ybuf[x]:
                shade[y:ybuf[x], x] = s[x]; fog[y:ybuf[x], x] = fz; depth[y:ybuf[x], x] = z; sky[y:ybuf[x], x] = False
                rim[y, x] = True
                ybuf[x] = y
        z += max(1.0, z * 0.012)
    return dict(shade=shade, fog=fog, depth=depth, rim=rim, sky=sky)
if __name__ == '__main__':
    import time; t = time.time(); r = render(); print(time.time() - t)
    np.savez_compressed('/tmp/terrain11.npz', **r)
    from PIL import Image
    s = r['shade']; fg = r['fog']
    img = np.zeros(s.shape + (3,))
    lit = np.clip((s + 0.2) / 1.2, 0, 1)
    img[..., 0] = 60 + 160 * lit; img[..., 1] = 50 + 110 * lit; img[..., 2] = 90 + 60 * lit
    img = img * (1 - fg[..., None]) + np.array([230, 170, 150]) * fg[..., None]
    img[r['sky']] = (80, 60, 110)
    Image.fromarray(img.astype(np.uint8)).resize((1152, 450), Image.NEAREST).save('/tmp/v9chk/terr_a.png')
