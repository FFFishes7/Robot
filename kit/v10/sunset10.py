"""v10 sunset (afterglow) shot: a full-frame view at the same fixed 3x as the insets, derived from the layout at that
moment -- window 1 with its curtains and brass rod, the bookshelf at left, the telescope at right, the blue bench and
him sitting on it (the actual sit drawings of the timeline). The glass is redrawn at the 1:1 inset grain with the SAME
band design as the wide window (indigo+stars / violet / rose / coral / peach / bright horizon line), coloured per frame
from the Godot wide (LUT grade), plus scalloped band edges, thin cloud wisps, twinkle, a horizon halo and two tiny birds."""
import sys, json, numpy as np
sys.path.insert(0, '/workspace/robot2d/kit/v10')
import panels10 as P
from PIL import Image
REG = (44, 14, 172, 86)                      # Lua; 128x72 -> 384x216 at 3x
GX0, GX1, GY0, GY1 = 92, 124, 30, 57         # glass rect (Lua, end exclusive)
EW = P.L(P.V + "emit_win07.png")
BANDS = dict(A=(0x3a, 0x2e, 0x5e), F=(0x6a, 0x4a, 0x7a), G=(0xb0, 0x60, 0x7a), H=(0xe8, 0x86, 0x6a), I=(0xf8, 0xb8, 0x70), D=(0xfd, 0xe0, 0xa0), E=(255, 255, 255))
def band_lut(F):
    """graded colour of each band design colour at wide frame F (median of its visible native samples in window 1)"""
    a, cls, r = P.compose(F)
    bx = (GX0 + P.OX, GY0 + P.OY, GX1 + P.OX, GY1 + P.OY)
    Wd, ok = P.sample_wide(F, bx)
    E = EW[bx[1]:bx[3], bx[0]:bx[2], :3].astype(int); rob = cls[bx[1]:bx[3], bx[0]:bx[2]] >= 1
    rob = rob & (cls[bx[1]:bx[3], bx[0]:bx[2]] != 2)
    out = {}
    for k, c in BANDS.items():
        m = (E[..., 0] == c[0]) & (E[..., 1] == c[1]) & (E[..., 2] == c[2]) & ok & ~rob
        out[k] = np.median(Wd[m], 0) if m.sum() >= 2 else None
    # fallbacks (all visible in practice)
    for k in out:
        if out[k] is None: out[k] = np.array(BANDS[k], float) * 0.6
    return out
def mix(a, b, t): return np.array(a) * (1 - t) + np.array(b) * t
def sky(F, j):
    """1:1 sky canvas for the glass (96 x 81), in the 3x space; j = frame index in the shot (drift)"""
    Lc = band_lut(F); W, H = (GX1 - GX0) * 3, (GY1 - GY0) * 3
    S = np.zeros((H, W, 3), float)
    # band layout from the design (native rows -> 3x): A 30-35, checker 36, F 37-41, [muntin 42-43], G 44-46, checker 47, H 48-51, checker 52, I 53-54, D 55, I 56
    rows = [("A", 30, 36), ("F", 37, 42), ("F", 42, 44), ("G", 44, 47), ("H", 48, 52), ("I", 53, 55), ("D", 55, 56), ("I", 56, 57)]
    for k, r0, r1 in rows: S[(r0 - GY0) * 3:(r1 - GY0) * 3] = Lc[k]
    # scalloped transitions where the design has checker rows (36: A/F, 47: G/H, 52: H/I)
    x = np.arange(W)
    for (up, dn, r) in (("A", "F", 36), ("G", "H", 47), ("H", "I", 52)):
        y0 = (r - GY0) * 3; drift = (j // 10) % 6
        bump = np.round(1.5 + 1.5 * np.cos((x + drift) * 2 * np.pi / 6)).astype(int)   # 0..3 px scallops
        for xx in range(W):
            S[y0:y0 + 3, xx] = Lc[dn]; S[y0:y0 + bump[xx], xx] = Lc[up]
            # a 1-px lighter lip under each scallop (lit from below by the afterglow)
            if bump[xx] < 3: S[y0 + bump[xx], xx] = mix(Lc[dn], Lc["D"], 0.25)
    # thin cloud wisps (1-px, lighter tone, lit undersides), drifting 1 px every 8 frames
    rng = np.random.RandomState(5)
    for (k, yr, n) in (("F", (39, 41), 3), ("G", (44, 46), 2), ("A", (32, 35), 2)):
        for q in range(n):
            y = (yr[0] - GY0) * 3 + rng.randint(0, (yr[1] - yr[0]) * 3); L = rng.randint(10, 22); x0 = (rng.randint(0, W) + j // 8) % (W + 30) - 15
            top = mix(Lc[k], Lc["G" if k != "G" else "H"], 0.45); lip = mix(Lc[k], Lc["D"], 0.35)
            for d in range(L):
                xx = x0 + d
                if 0 <= xx < W:
                    S[y, xx] = top
                    if 2 <= d < L - 2 and y + 1 < H: S[y + 1, xx] = lip
    # stars of the design (D, E pixels in the top band) + twinkle; a few faint 1-px extras (sub-native)
    E = EW[GY0 + P.OY:GY1 + P.OY, GX0 + P.OX:GX1 + P.OX, :3].astype(int)
    for (yy, xx) in zip(*np.nonzero(((E[..., 0] == 0xfd) & (E[..., 1] == 0xe0) | (E[..., 0] == 255)) & (np.arange(E.shape[0])[:, None] < 7))):
        cy, cx = yy * 3 + 1, xx * 3 + 1; tw = ((j + xx * 7) // 12) % 4
        S[cy, cx] = Lc["E"] if tw else Lc["D"]
        if tw == 1 or (E[yy, xx, 0] == 255 and tw != 3):
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)): S[cy + dy, cx + dx] = mix(Lc["A"], Lc["D"], 0.45)
    for q in range(9):
        yy, xx = rng.randint(1, 16), rng.randint(1, W - 1)
        if ((j + q * 13) // 16) % 3: S[yy, xx] = mix(Lc["A"], Lc["E"], 0.35)
    # horizon: the bright line glows a little wider (dithered halo) on both sides
    hy = (55 - GY0) * 3
    for xx in range(W):
        if (xx + hy) % 2 == 0: S[hy - 1, xx] = mix(Lc["I"], Lc["D"], 0.5)
    S[hy + 1, :] = mix(Lc["D"], Lc["I"], 0.3)
    # two tiny distant birds gliding right -> left across the upper-left pane
    for b, (bx0, by0, sp) in enumerate(((W + 10, 25, 5), (W + 30, 29, 6))):
        xx = bx0 - j // sp; yy = by0 + int(1.2 * np.sin(j / 9 + b)); flap = (j // 5 + b) % 2
        col = mix(Lc["A"], Lc["F"], 0.2)
        pts = [(0, 0), (-1, -1 if flap else 0), (1, -1 if flap else 0)]
        for dx, dy in pts:
            if 0 <= xx + dx < W and 0 <= yy + dy < H: S[yy + dy, xx + dx] = col
    return np.clip(S, 0, 255).astype(np.uint8), Lc
def shot(F, j):
    res, info = P.render(F, REG, pad=4, polish=None)
    pad = info["pad"] * 3
    full = res                                         # uncropped (render returns cropped) -> work on cropped coords
    C = info["cls"][pad:-pad, pad:-pad]
    out = res.copy()
    # glass mask (sky pixels only: emissive class, inside the glass rect, not muntin wood)
    gx0, gy0 = (GX0 - REG[0]) * 3, (GY0 - REG[1]) * 3
    Sk, Lc = sky(F, j)
    Eg = EW[GY0 + P.OY:GY1 + P.OY, GX0 + P.OX:GX1 + P.OX, :3].astype(int)
    wood = ((Eg[..., 0] == 0xc9) & (Eg[..., 1] == 0x82)) | ((Eg[..., 0] == 0xad) & (Eg[..., 1] == 0x64))
    wood3 = np.repeat(np.repeat(wood, 3, 0), 3, 1)
    Hs, Ws = Sk.shape[:2]
    sub = out[gy0:gy0 + Hs, gx0:gx0 + Ws]; Cs = C[gy0:gy0 + Hs, gx0:gx0 + Ws]
    m = (Cs == 2) & ~wood3
    sub[m, :3] = Sk[m]
    # backlight: warm 1-px rim on his silhouette (both sides + top), in the afterglow colour
    rimc = tuple(int(v) for v in mix(Lc["I"], Lc["D"], 0.5))
    info2 = dict(info); info2["cls"] = C
    out = P.rim(out, info2, rimc, 1, 0.45); out = P.rim(out, info2, rimc, -1, 0.45)
    rb = (C == 1) | (C == 3); topm = np.zeros_like(rb); topm[1:] = rb[1:] & ~rb[:-1]
    inner = np.zeros_like(topm); inner[1:] = topm[:-1]; tg = inner & rb & (C == 1)
    lum = 0.3 * out[..., 0] + 0.59 * out[..., 1] + 0.11 * out[..., 2]; tg &= lum > 60
    out[tg, :3] = (out[tg, :3] * 0.55 + np.array(rimc) * 0.45).astype(np.uint8)
    return out
if __name__ == '__main__':
    a, b = P.MK["panels"]["sunset"]
    if len(sys.argv) > 1 and sys.argv[1] == 'all':
        import os; os.makedirs('/tmp/s10', exist_ok=True)
        for F in range(a, b): Image.fromarray(shot(F, F - a)).save(f'/tmp/s10/{F}.png')
        print("sunset", a, b)
    else:
        for F in (a + 10, a + 90):
            Image.fromarray(shot(F, F - a)).resize((1920, 1080), Image.NEAREST).save(f'/tmp/v9chk/sunset_{F}.png')
