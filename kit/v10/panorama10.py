"""v10 ending panorama: what he is looking at -- a Stardew-title-style layered sunset (clean banded gradient sky, cross
stars, big fluffy layered clouds framing both sides, rows of ridged hills with crisp lit/shadow slopes, dark foliage in
the corners), 1-px grain at 384x216. Opening colours = the window-band grade of the wide at the cut frame; it drifts
into dusk (sun sinks, first stars, village lights) and tilts up into the night sky the credits sit on."""
import sys, numpy as np
sys.path.insert(0, '/workspace/robot2d/kit/v10')
from PIL import Image
W, H, CH = 384, 216, 336            # canvas taller than the screen: the camera tilts up at the end
N = 168
HZ = 250                            # horizon row on the canvas
NIGHT = dict(A=(16, 14, 38), F=(30, 28, 68), G=(46, 38, 86), H=(62, 48, 96), I=(76, 58, 102), D=(92, 70, 108))
CRED_BG = (22, 13, 22)
def ss(t): t = min(1, max(0, t)); return t * t * (3 - 2 * t)
def mix(a, b, t): return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))
def shade(c, k):
    """k<0 darker & cooler (toward plum), k>0 lighter & warmer"""
    c = np.array(c, float)
    if k < 0: return tuple(np.clip(c * (1 + 0.55 * k) + np.array([6, 0, 14]) * (-k), 0, 255).astype(int))
    return tuple(np.clip(c + (np.array([255, 226, 178]) - c) * 0.5 * k, 0, 255).astype(int))
class Pano:
    def __init__(self, lut0):
        self.L0 = {k: tuple(int(v) for v in lut0[k]) for k in "AFGHID"}
        rng = np.random.RandomState(21); self.rng = rng
        self.stars = [(rng.randint(2, W - 2), rng.randint(4, HZ - 60), rng.rand(), rng.randint(0, 60), rng.rand() < 0.16) for _ in range(190)]
        # Milky Way: a diagonal band (lower-left -> upper-right) of glow bands, dark dust lanes and dense star dust
        yy, xx = np.mgrid[0:CH, 0:W]
        u = (xx * 0.42 + yy) - 175.0                                   # signed distance-ish across the band
        wob = 7 * np.sin(xx / 23.0) + 4 * np.sin(xx / 9.0 + 1.3)
        dist = np.abs(u + wob)
        from scipy.ndimage import gaussian_filter
        n1 = gaussian_filter(rng.randn(CH, W), 5); n1 /= n1.std(); n2 = gaussian_filter(rng.randn(CH, W), 2.2); n2 /= n2.std()
        dd = dist - 5 * n1                                               # clumpy, irregular edges
        self.mw_core = (dd < 8) & (n2 > -0.3); self.mw_mid = dd < 17; self.mw_out = dd < 28
        self.mw_lane = (dist < 14) & (np.abs(n1 + 0.6 * n2) < 0.28) & (np.abs(u + wob + 2) < 10)
        dust = rng.rand(CH, W)
        self.mw_dust = (dust < np.where(self.mw_core, 0.16, np.where(self.mw_mid, 0.08, np.where(self.mw_out, 0.03, 0.0)))) & ~self.mw_lane
        self.mw_ph = rng.randint(0, 50, (CH, W))
        self.moon = (66, 40, 12)
        # hill layers: (base row, peak amplitude, n peaks, slope, parallax)
        self.layers = []
        for li, (base, amp, npk, slope, par) in enumerate(((HZ - 2, 16, 9, 0.5, 0.35), (HZ + 14, 20, 8, 0.55, 0.55), (HZ + 34, 24, 7, 0.6, 0.75), (HZ + 58, 28, 6, 0.66, 1.0))):
            npk = int(W / (2 * amp / slope) * 1.25) + 2; pk = [(int(-20 + (W + 40) * (q + 0.5 * rng.rand()) / npk), amp * (0.5 + 0.5 * rng.rand())) for q in range(npk)]
            x = np.arange(W); hts = np.full(W, -1e9); own = np.zeros(W, int)
            for i, (px, a) in enumerate(pk):
                h = a - slope * np.abs(x - px) + 1.6 * np.sin(x * 0.35 + i)  # small ridge wobble
                better = h > hts; hts[better] = h[better]; own[better] = i
            top = (base - np.maximum(hts, 2)).astype(int)
            gul = [(rng.randint(0, W), rng.randint(3, 12)) for _ in range(npk * 3)]
            vill = [(rng.randint(40, W - 40), rng.rand()) for _ in range(10)] if li == 1 else []
            self.layers.append(dict(top=top, own=own, pk=pk, par=par, gul=gul, vill=vill, base=base))
        # clouds: bumps (cx, cy, r) per cloud; left and right banks, 2 depths each
        self.clouds = []
        for side, x0 in ((-1, -40), (1, W - 110)):
            for depth in (0, 1):
                bumps = []
                cx0 = x0 - 20 + (40 if depth else 0) * (-side); cy0 = HZ - 52 - depth * 26
                for k in range(16 + depth * 4):
                    u = rng.rand(); bx = cx0 + int(150 * u); r = rng.randint(10, 24) - depth * 4
                    inward = u if side < 0 else 1 - u              # banks thin out toward the centre of the frame
                    by = cy0 - int(0.5 * r) - int(rng.rand() * 34 * (1 - inward)) + int(22 * inward)
                    bumps.append((bx, by, r))
                self.clouds.append(dict(b=bumps, depth=depth, side=side))
    def palette(self, t):
        """band colours drifting from the matched sunset (t=0) into dusk/night (t=1)"""
        return {k: mix(self.L0[k], NIGHT[k], ss(t)) for k in "AFGHID"}
    def sky(self, img, P, dusk):
        # clean banded gradient: stops top->horizon; each band boundary is one checker row mixing the two bands
        stops = [(0, mix(P["A"], CRED_BG, 0.55)), (70, P["A"]), (150, P["F"]), (195, P["G"]), (222, P["H"]), (240, P["I"]), (HZ, P["D"])]
        def col(y):
            for (a, ca), (b, cb) in zip(stops, stops[1:]):
                if a <= y <= b: return mix(ca, cb, (y - a) / (b - a))
            return stops[-1][1]
        nb = 30; ys = np.linspace(0, HZ, nb + 1).astype(int); cs = [col((ys[i] + ys[i + 1]) / 2) for i in range(nb)]
        for i in range(nb):
            img[ys[i]:ys[i + 1]] = cs[i]
            if i > 0:
                y = ys[i]; img[y, (y % 2)::2] = cs[i - 1]
        img[HZ:] = P["D"]
    def sun(self, img, P, t):
        cy = HZ - 24 + int(round(44 * ss(t / 0.5)))                     # sinks below the horizon in the first ~3 s
        cx = 236; R = 15
        yy, xx = np.mgrid[0:CH, 0:W]; d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.0) ** 2)
        for rr, col, dith in ((R + 26, mix(P["I"], P["D"], 0.35), True), (R + 14, mix(P["I"], P["D"], 0.7), True), (R + 6, P["D"], False)):
            m = (d < rr) & (yy < HZ)
            if dith: m &= ((xx + yy) % 2 == 0) | (d < rr - 3)
            img[m] = mix(tuple(img[m][0]) if m.any() else col, col, 1.0) if False else col
        m = (d < R) & (yy < HZ); img[m] = mix((255, 238, 196), P["D"], ss(t / 0.5) * 0.6)
        m = (d < R - 4) & (yy < HZ); img[m] = mix((255, 250, 226), P["D"], ss(t / 0.5) * 0.6)
    def night_sky(self, img, P, t, f):
        nt = ss((t - 0.4) / 0.45)
        if nt <= 0: return
        # Milky Way glow bands (3 steps, checker edges), only above the horizon
        above = np.zeros(img.shape[:2], bool); above[:HZ - 20] = True
        chk = ((np.arange(CH)[:, None] + np.arange(W)[None]) % 2 == 0)
        for m, k in ((self.mw_out, 0.10), (self.mw_mid, 0.2), (self.mw_core, 0.32)):
            mm = m & above & (chk | (nt > 0.66))
            if nt < 0.33: mm &= chk
            base = img[mm].astype(float); tgt = np.array([150, 140, 200], float)
            img[mm] = (base + (tgt - base) * k * nt).astype(np.uint8)
        ln = self.mw_lane & above; img[ln] = (img[ln].astype(float) * (1 - 0.35 * nt)).astype(np.uint8)
        d = self.mw_dust & above & (((f + self.mw_ph) // 16) % 3 != 0)
        img[d] = (img[d].astype(float) * (1 - 0.6 * nt) + np.array([226, 222, 240]) * 0.6 * nt).astype(np.uint8)
        # moon: cratered disc with a soft banded glow
        mx, my, R = self.moon
        yy, xx = np.mgrid[0:CH, 0:W]; dd = np.sqrt((xx - mx) ** 2 + (yy - my) ** 2)
        for rr, k in ((R + 16, 0.08), (R + 9, 0.15), (R + 4, 0.24)):
            m = (dd < rr) & (((xx + yy) % 2 == 0) | (dd < rr - 2))
            img[m] = (img[m].astype(float) + (np.array([200, 200, 230]) - img[m]) * k * nt).astype(np.uint8)
        disc = dd <= R; lit = np.array([238, 232, 204]); shd = np.array([196, 188, 170]); crt = np.array([176, 168, 152])
        col = np.where(((xx - mx + 3) ** 2 + (yy - my + 3) ** 2 <= (R + 1) ** 2)[..., None], lit, shd)
        for (cx_, cy_, cr) in ((-4, -3, 2.6), (3, 2, 3.4), (-2, 5, 1.8), (5, -5, 1.6), (-6, 3, 1.4), (1, -7, 1.3)):
            cm = (xx - mx - cx_) ** 2 + (yy - my - cy_) ** 2 <= cr * cr
            col = np.where(cm[..., None], crt, col)
            hl = ((xx - mx - cx_ + 1) ** 2 + (yy - my - cy_ + 1) ** 2 <= cr * cr) & ~cm & ((xx - mx - cx_) ** 2 + (yy - my - cy_) ** 2 <= (cr + 1.2) ** 2)
            col = np.where((hl & (xx > mx + cx_) & (yy > my + cy_))[..., None], lit + 10, col)
        img[disc] = (img[disc].astype(float) * (1 - nt) + np.clip(col[disc], 0, 255) * nt).astype(np.uint8)
        e = disc & ~(np.sqrt((xx - mx) ** 2 + (yy - my) ** 2) <= R - 1) & (xx > mx) & (yy > my - 4)
        img[e] = (img[e].astype(float) * 0.85).astype(np.uint8)
    def star_layer(self, img, P, t, f):
        vis = ss((t - 0.25) / 0.6)
        for (x, y, th, ph, cross) in self.stars:
            if th > vis * 1.05: continue
            tw = ((f + ph) // 14) % 4; lit = mix(P["A"], (255, 246, 220), 0.9 if cross else 0.55)
            if y >= CH or img[y, x].sum() > 420: continue
            img[y, x] = lit if tw else mix(P["A"], lit, 0.5)
            if cross and tw in (1, 2):
                arm = mix(P["A"], lit, 0.45)
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)): img[y + dy, x + dx] = arm
                if tw == 1:
                    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)): img[y + dy, x + dx] = mix(P["A"], lit, 0.2)
    def cloud_layer(self, img, P, f, off):
        for c in sorted(self.clouds, key=lambda c: -c["depth"]):
            dx = (f // (16 if c["depth"] else 11)) * (1 if c["side"] < 0 else -1)
            dy = int(off * (0.25 if c["depth"] else 0.35))
            nt = self._nt
            base = mix(mix(P["G"], P["F"], 0.45 if c["depth"] else 0.15), (92, 92, 140) if c["depth"] else (120, 122, 170), nt)
            hi = mix(mix(base, P["D"], 0.45), (170, 172, 214), nt); hi2 = mix(mix(base, (255, 232, 196), 0.62), (206, 208, 236), nt); sh = shade(base, -0.28)
            under = mix(mix(P["H"], P["D"], 0.55), (84, 84, 130), nt); rim = mix(mix(P["I"], (255, 236, 200), 0.55), (150, 150, 200), nt)
            bumps = sorted(c["b"], key=lambda b: b[1])                 # back (high) puffs first, front (low) puffs over them
            bottom = max(by + r * 0.35 for _, by, r in bumps) + dy
            x0 = int(min(b[0] - b[2] for b in bumps) + dx - 2); x1 = int(max(b[0] + b[2] for b in bumps) + dx + 3)
            y0 = int(min(b[1] - b[2] for b in bumps) + dy - 2); y1 = int(bottom + 2)
            x0c, x1c, y0c, y1c = max(0, x0), min(W, x1), max(0, y0), min(CH, y1)
            if x0c >= x1c or y0c >= y1c: continue
            yy, xx = np.mgrid[y0c:y1c, x0c:x1c]
            reg = img[y0c:y1c, x0c:x1c]
            allm = np.zeros(yy.shape, bool)
            for (bx, by, r) in bumps:
                bx += dx; by += dy
                d = np.sqrt((xx - bx) ** 2 + (yy - by) ** 2)
                m = (d <= r) & (yy <= bottom)
                reg[m] = base
                cres = m & (np.sqrt((xx - bx) ** 2 + (yy - by - 0.3 * r) ** 2) > r)      # top crescent (lit from above-behind)
                reg[cres] = hi
                reg[m & (np.sqrt((xx - bx) ** 2 + (yy - by - 0.12 * r) ** 2) > r) & (yy < by - 0.45 * r)] = hi2
                reg[m & (yy - by > 0.25 * r) & (np.sqrt((xx - bx) ** 2 + (yy - by + 0.25 * r) ** 2) > r)] = sh
                # a 1-px darker seam where this puff overlaps the ones behind it (layered look)
                e = m & (d > r - 1) & allm
                reg[e] = sh
                allm |= m
            # warm underside: the bottom rows of the cloud are lit by the low sun
            low = allm & (yy > bottom - 4); reg[low] = under
            edge = allm & (yy > bottom - 1.5); reg[edge] = rim
    def hills(self, img, P, t, off, f):
        far = mix(P["G"], P["F"], 0.5)
        tints = [mix(far, P["H"], 0.3), mix(P["F"], (72, 46, 78), 0.35), mix((60, 44, 74), (40, 30, 58), 0.3), (32, 25, 46)]
        sunx = 236
        for li, Ly in enumerate(self.layers):
            dy = int(round(off * 1.4 * Ly["par"]))
            teal = [(70, 110, 128), (52, 96, 110), (38, 74, 90), (26, 50, 66)][li]
            base = mix(mix(tints[li], shade(tints[li], -0.5), ss(t) * 0.55), teal, self._nt * 0.85)
            lit = mix(mix(base, P["I"], 0.38 if li < 2 else 0.22), mix(base, (150, 200, 196), 0.35), self._nt); lit2 = mix(lit, mix(P["D"], (200, 236, 226), self._nt), 0.35)
            dark = shade(base, -0.25); deep = shade(base, -0.45)
            top = Ly["top"] + dy
            for x in range(W):
                y0 = top[x]
                if y0 >= CH: continue
                y0c = max(0, y0)
                px = Ly["pk"][Ly["own"][x]][0]
                facing = (x > px) == (sunx > px)
                col = lit if facing else dark
                img[y0c:CH, x] = col
                # haze / depth: lower rows step down toward the valley colour (checker at each step)
                for k, (dd, cc) in enumerate(((14, base if facing else deep), (26, deep))):
                    ya = y0 + dd
                    if ya < CH:
                        img[max(0, ya):CH, x] = cc
                        if 0 <= ya < CH and (x + ya) % 2 == 0: img[ya, x] = col if k == 0 else (base if facing else deep)
                # crisp ridge line: bright on sun-facing slopes, dark on the shadow side
                if 0 <= y0 < CH: img[y0, x] = lit2 if facing else deep
                if facing and 0 <= y0 + 1 < CH and li < 2: img[y0 + 1, x] = mix(lit, lit2, 0.5)
            for (gx, gl) in Ly["gul"]:
                px = Ly["pk"][Ly["own"][gx % W]][0]; sgn = 1 if gx > px else -1
                facing = (gx > px) == (sunx > px)
                for k in range(gl):
                    x = gx + sgn * (k // 2)
                    if 0 <= x < W:
                        y = top[x] + 3 + k
                        if 0 <= y < CH: img[y, x] = dark if facing else deep
            for (vx, th) in Ly["vill"]:
                if th < ss((t - 0.35) / 0.5):
                    y = top[vx] + 6
                    for dxx in (0, 3):
                        if 0 <= y < CH and 0 <= vx + dxx < W and ((f // 20 + vx) % 7): img[y, vx + dxx] = (255, 206, 120)
    def foliage(self, img, P, t, off, f):
        rng = np.random.RandomState(9)
        d0 = (22, 18, 32); d1 = (36, 30, 50); d2 = (54, 42, 66); d3 = (78, 56, 80)
        rimc = mix(P["H"], P["D"], 0.35); rimc = mix(rimc, d3, ss(t) * 0.7)
        dy = int(round(off * 1.8))
        for side in (-1, 1):
            # clumps along a curve hugging the corner
            clumps = []
            for k in range(12):
                u = k / 11.0
                cx = int((4 + 64 * (1 - u) ** 1.3) if side < 0 else (W - 4 - 64 * (1 - u) ** 1.3)); cy = int(CH - 10 - 92 * u ** 1.2) + dy
                clumps.append((cx + rng.randint(-10, 11), cy + rng.randint(-6, 7), rng.randint(16, 26) - int(8 * u)))
            # a small bare twig with two leaves poking out of the mass
            for k in range(14):
                x = (58 + k) if side < 0 else (W - 59 - k); y = CH - 84 - k // 2 + dy
                if 0 <= y < CH - 1 and 0 <= x < W: img[y, x] = (84, 50, 40); img[y + 1, x] = (48, 28, 28)
            sway = int(round(0.8 * np.sin(f / 20 + side)))
            for (cx, cy, R) in clumps:
                leaves = []
                for q in range(int(R * 3.2)):
                    a = rng.rand() * 2 * np.pi; rr = R * np.sqrt(rng.rand())
                    leaves.append((int(cx + rr * np.cos(a)) + (sway if cy < CH - 70 else 0), int(cy + 0.8 * rr * np.sin(a)), rng.randint(2, 5)))
                x0, x1 = max(0, cx - R - 6), min(W, cx + R + 6); y0, y1 = max(0, cy - R - 6), min(CH, cy + R + 6)
                if x0 >= x1 or y0 >= y1: continue
                yy, xx = np.mgrid[y0:y1, x0:x1]; reg = img[y0:y1, x0:x1]
                for lx, ly, lr in sorted(leaves, key=lambda l: l[1]):
                    m = (xx - lx) ** 2 + (yy - ly) ** 2 <= lr * lr
                    if not m.any(): continue
                    up = (ly - cy) / max(1, R)                       # -1 top .. 1 bottom
                    c = d2 if up < -0.35 else (d1 if up < 0.35 else d0)
                    reg[m] = c
                    reg[m & ((xx - lx + 1) ** 2 + (yy - ly + 1) ** 2 <= max(1, lr - 2) ** 2) & (up < 0)] = d3 if up < -0.55 else d2
                # warm rim along the top edge of the clump (sunset side)
                cm = np.zeros(yy.shape, bool)
                for lx, ly, lr in leaves: cm |= (xx - lx) ** 2 + (yy - ly) ** 2 <= lr * lr
                e = cm & ~np.roll(cm, 1, 0) & (yy < cy - R * 0.3)
                if side < 0: e &= xx > cx - R * 0.3
                else: e &= xx < cx + R * 0.3
                reg[e] = rimc
    def frame(self, f):
        t = f / (N - 1); P = self.palette(t); self._nt = ss((t - 0.35) / 0.5)
        off = int(round(96 * ss((f - 84) / 72)))                           # tilt up at the end
        img = np.zeros((CH, W, 3), np.uint8)
        self.sky(img, P, t)
        self.sun(img, P, t)
        self.star_layer(img, P, t, f)
        self.night_sky(img, P, t, f)
        # everything below the sky moves with parallax; the sky + stars move 0.5x
        can = img
        self.cloud_layer(can, P, f, off)
        self.hills(can, P, t, off, f)
        self.foliage(can, P, t, off, f)
        # birds
        for b, (x0, y0, sp) in enumerate(((W + 8, HZ - 70, 3), (W + 20, HZ - 64, 3), (W + 30, HZ - 74, 4))):
            x = x0 - f // sp; y = y0 + int(np.sin(f / 7 + b)) + int(off * 0.3); flap = (f // 4 + b) % 2
            for dx, dyy in ((0, 0), (-1, -1 + (0 if flap else 1)), (1, -1 + (0 if flap else 1)), (-2, -1 if flap else 0), (2, -1 if flap else 0)):
                if 0 <= x + dx < W and 0 <= y + dyy < CH: can[y + dyy, x + dx] = shade(P["F"], -0.5)
        top = CH - H - int(round(off * 1.25))
        top = max(0, top)
        return can[top:top + H]
    def backdrop(self, f):
        """night sky (gradient + stars + Milky Way + moon), top of the canvas -- the credits sit on it"""
        t = 1.0; P = self.palette(t); self._nt = 1.0
        img = np.zeros((CH, W, 3), np.uint8); self.sky(img, P, t); self.star_layer(img, P, t, f); self.night_sky(img, P, t, f)
        return img[:H]
if __name__ == '__main__':
    import json
    sys.path.insert(0, '/workspace/robot2d/kit/v10')
    import sunset10 as S
    F0 = int(sys.argv[1]) if len(sys.argv) > 1 else 1430
    lut = S.band_lut(F0); print({k: tuple(int(x) for x in v) for k, v in lut.items()})
    p = Pano(lut)
    for f in (0, 90, 130, 167): Image.fromarray(p.frame(f)).resize((1152, 648), Image.NEAREST).save(f'/tmp/v9chk/pano_{f}.png')
