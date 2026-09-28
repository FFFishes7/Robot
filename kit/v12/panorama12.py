"""v12 ending panorama (interface as v10/v11: Pano(lut0).frame(f) / backdrop(f), N=168).
Framed high: sky ~70% of the frame, the hills a low band. Richer banded sky built from the room's dusk band LUT
(hue-matched, saturation lifted, gold horizon), posterised sun rays, clouds lit by the low sun (gold flanks and
undersides, violet tops, glow rims), green vegetated ridge rows (yellow-green lit faces, orange crest rims,
teal/violet shade, hazy far rows), leafy corner trees built from many small leaf clumps. Dusk/night: stars,
Milky Way, moon (v10/v11), moonlit clouds, muted teal hills. 1-px grain, no dither rows, no smoothing."""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); from paths import KIT
sys.path.insert(0, KIT + 'v12'); sys.path.insert(0, KIT + 'v11'); sys.path.insert(0, KIT + 'v10')
import panorama11 as P11
from panorama10 import W, H, CH, N, HZ, ss, mix, CRED_BG
import hills11b as HB
import clouds12 as CL
TOP0 = 96                                    # canvas row at the top of the frame before the tilt (horizon at y=154)
SUNX = 250
HB.ROWS = [(4, 11, 3, 13, 18), (11, 13, 4, 11, 22), (19, 15, 5, 10, 26), (28, 17, 6, 9, 30), (38, 20, 7, 8, 35), (50, 23, 8, 7, 40), (64, 26, 9, 6, 46)]
def m3(a, b, t): return np.array(a, float) * (1 - t) + np.array(b, float) * t
def sat(c, k):
    c = np.array(c, float); g = c.mean(); return np.clip(g + (c - g) * k, 0, 255)
LEAF = P11.LEAF
class Pano(P11.Pano):
    def __init__(self, lut0):
        P11.P10.Pano.__init__(self, lut0)
        self.banks = CL.make_banks(sunx=SUNX)
        self.hr = HB.render_rows()
        r = self.hr; self.rowm = []; self.rowt = []
        for k in range(r["n"]):
            m = r["row"] == k; ext = np.maximum.accumulate(m, axis=0)
            t_ = np.clip(r["tone"] - np.floor(r["vf"] * 2.4).astype(int), 0, 4); self.rowm.append(ext); self.rowt.append(np.where(m, t_, 0))
        rng = np.random.RandomState(31)
        self.vill = [(int(x), rng.rand()) for x in rng.randint(40, W - 40, 12)]
        yy, xx = np.mgrid[0:CH, 0:W]; self.yy, self.xx = yy, xx
        self._fol = {s: self._fol12(s) for s in (-1, 1)}
    # ---------------- palette: the room LUT, saturation lifted, drifting to night
    def palette(self, t):
        P = {k: tuple(sat(self.L0[k], 1.45).astype(int)) for k in "AFGHID"}
        P["D"] = tuple(np.clip(m3(P["D"], (255, 222, 150), 0.45), 0, 255).astype(int))
        P["I"] = tuple(np.clip(m3(P["I"], (250, 160, 80), 0.35), 0, 255).astype(int))
        return {k: mix(P[k], P11.P10.NIGHT[k], ss((t - 0.12) / 0.5)) for k in "AFGHID"}
    def sky(self, img, P, dusk):
        stops = [(0, mix(P["A"], CRED_BG, 0.6)), (TOP0 - 10, P["A"]), (TOP0 + 50, P["F"]), (TOP0 + 92, P["G"]), (TOP0 + 122, P["H"]), (TOP0 + 142, P["I"]), (HZ, P["D"])]
        def col(y):
            for (a, ca), (b, cb) in zip(stops, stops[1:]):
                if a <= y <= b: return mix(ca, cb, (y - a) / (b - a))
            return stops[-1][1]
        ys = sorted(set([0] + [int(HZ * (1 - (1 - i / 52) ** 1.25)) for i in range(53)]))
        for a, b in zip(ys, ys[1:]): img[a:b] = col((a + b) / 2)
        img[HZ:] = P["D"]
    def sun(self, img, P, t):
        cy = HZ - 22 + int(round(40 * ss(t / 0.5))); cx = SUNX; R = 14
        yy, xx = self.yy, self.xx; d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2); sky = yy < HZ
        k0 = 1 - ss(t / 0.55)                                   # rays + glow fade as the sun goes down
        if k0 > 0:
            # posterised sun rays: alternating wedges, 3 distance steps, one band-step lighter
            ang = np.arctan2(yy - cy, xx - cx); wob = 0.18 * np.sin(ang * 7 + 1.3)
            wedge = (np.floor((ang + wob) * 15 / np.pi) % 2 == 0) & (yy < cy + 2) & sky
            for rr, k in ((210, 0.035), (140, 0.06), (84, 0.09)):
                m = wedge & (d < rr); img[m] = np.clip(m3(img[m], (255, 226, 170), k * k0), 0, 255).astype(np.uint8)
            for rr, k in ((R + 36, 0.16), (R + 22, 0.32), (R + 12, 0.55), (R + 5, 0.8)):
                m = (d < rr) & sky; img[m] = np.clip(m3(img[m], (255, 214, 150), k * 0.6 * k0 + 0.1), 0, 255).astype(np.uint8)
        fade = ss(t / 0.5) * 0.6
        m = (d < R) & sky; img[m] = mix((255, 236, 186), P["D"], fade)
        m = (d < R - 4) & sky; img[m] = mix((255, 250, 222), P["D"], fade)
    def cloud_layer(self, img, P, f, off):
        nt = self._nt; t = f / (N - 1); glow = 1 - ss(t / 0.6)
        for b in sorted(self.banks, key=lambda b: -b["depth"]):
            d = b["depth"]
            dx = (f // (16 if d else 11)) * (1 if b["side"] < 0 else -1) if d < 2 else f // 20
            dy = int(off * (0.25 if d else 0.35))
            # sunset: violet shade -> rose body -> coral -> gold flank -> cream glow; night: moonlit blue-grey
            ss_ = [m3(P["F"], (86, 64, 128), 0.35), m3(P["F"], P["G"], 0.55), m3(P["G"], (236, 150, 150), 0.25), m3(P["H"], (250, 176, 150), 0.35), m3(P["I"], P["D"], 0.6)]
            nn = [(40, 42, 76), (52, 54, 90), (64, 66, 104), (84, 88, 124), (116, 120, 156)]
            du = [(66, 54, 104), (88, 70, 120), (112, 88, 134), (150, 116, 146), (196, 160, 164)]
            cols = []
            for q in range(5):
                c = m3(m3(ss_[q], du[q], ss((t - 0.2) / 0.4)), nn[q], nt)
                if d == 2: c = m3(c, img[HZ - 60, 0], 0.15)
                if d == 1: c = m3(c, P["G"] if nt < 0.5 else (40, 40, 70), 0.12)
                cols.append(np.clip(c, 0, 255).astype(np.uint8))
            rimc = np.clip(m3(m3(m3(cols[4], (255, 240, 196), 0.6), (214, 206, 222), ss((t - 0.2) / 0.4)), (150, 156, 196), nt), 0, 255).astype(np.uint8)
            tt0 = b["tone"]; h, w = tt0.shape; X0 = b["x0"] + dx; Y0 = b["y0"] + dy
            xa, xb, ya, yb = max(0, X0), min(W, X0 + w), max(0, Y0), min(CH, Y0 + h)
            if xa >= xb or ya >= yb: continue
            tt = tt0[ya - Y0:yb - Y0, xa - X0:xb - X0]; rr = b["rim"][ya - Y0:yb - Y0, xa - X0:xb - X0]; reg = img[ya:yb, xa:xb]
            for k in range(5): reg[tt == k] = cols[k]
            reg[rr & (tt >= 0)] = rimc
    def hills(self, img, P, t, off, f):
        r = self.hr; nt = self._nt; n = r["n"]
        haze = m3(P["H"], P["I"], 0.5)
        for k in range(n):
            dd = k / (n - 1)                                     # 0 far .. 1 near
            body = m3((66, 128, 72), (40, 96, 62), dd)
            sh = m3(body, (34, 60, 92), 0.55); deep = m3(body, (30, 32, 70), 0.72)
            lit = m3(body, (178, 196, 78), 0.62); hi = m3(body, (232, 216, 104), 0.72); rim = m3(hi, (255, 164, 84), 0.55)
            tones = [deep, sh, body, lit, hi, rim]
            hz = 0.62 * (1 - dd) ** 1.2                          # atmospheric perspective toward the glowing horizon
            tones = [m3(c, haze, hz) for c in tones]
            dusk_t = ss((t - 0.25) / 0.35)
            dk = [m3(c, (70, 64, 108), 0.55) for c in tones]     # dusk: light leaves, violet shade takes over
            nb = m3((72, 106, 126), (24, 50, 60), dd ** 0.8)
            ng = [m3(nb, (8, 16, 30), 0.6), m3(nb, (10, 22, 38), 0.4), nb, m3(nb, (92, 136, 140), 0.3), m3(nb, (120, 164, 160), 0.42), m3(nb, (120, 164, 160), 0.42)]
            cc = [np.clip(m3(m3(a, b_, dusk_t), c_, nt), 0, 255).astype(np.uint8) for a, b_, c_ in zip(tones, dk, ng)]
            dy = int(round(off * 1.4 * P11.PAR[min(k, 5)]))
            m = self.rowm[k]; tone = self.rowt[k]; rimm = r["rim"] & (r["row"] == k)
            if dy: m = np.vstack([np.zeros((dy, W), bool), m[:-dy]]); tone = np.vstack([np.zeros((dy, W), int), tone[:-dy]]); rimm = np.vstack([np.zeros((dy, W), bool), rimm[:-dy]])
            for q in range(5): img[m & (tone == q)] = cc[q]
            if dusk_t < 0.6: img[rimm] = cc[5]
            if k == 1:
                for (vx, th) in self.vill:
                    if th < ss((t - 0.35) / 0.5) and ((f // 20 + vx) % 7):
                        col = np.nonzero(m[:, vx])[0]
                        if len(col):
                            y = col[0] + 4
                            for dxx in (0, 2):
                                if y < CH and m[y, min(W - 1, vx + dxx)]: img[y, vx + dxx] = (255, 206, 120)
    def _fol12(self, side):
        """leafy corner tree: ~260 small leaf clumps (r 3-6) inside a corner envelope, each clump shaded on its own
        (max-of-spheres) -> readable leaf clusters; serrated leaf stamps on the lit crown edge; a few branches that
        start inside the canopy. tone -1 empty, 0..4 dark->lit, 5 = branch."""
        rng = np.random.RandomState(9 if side < 0 else 19)
        w, h = 110, 120
        yy, xx = np.mgrid[0:h, 0:w].astype(float)
        env = lambda x, y: (x / 70.0) ** 1.6 + ((h - y) / 112.0) ** 1.6 < 1.0 + 0.08 * np.sin(y / 5.0 + x / 7.0)
        Z = np.full((h, w), -1e9); T = np.full((h, w), -1, int)
        L = np.array([0.55, -0.6, 0.58]); L /= np.linalg.norm(L)
        cl = []
        while len(cl) < 260:
            x, y = rng.uniform(-6, w), rng.uniform(0, h + 6)
            if env(max(x, 0), min(y, h - 1)): cl.append((x, y, rng.uniform(3.0, 6.2)))
        cl.sort(key=lambda c: c[1])
        for (cx, cy, r) in cl:
            d2 = (xx - cx) ** 2 + (yy - cy) ** 2; m = d2 < r * r
            depth = (cy / h) * 20 + (1 - cx / w) * 8          # lower/outer clumps sit in front
            z = np.where(m, np.sqrt(np.maximum(r * r - d2, 0)) + depth, -1e9)
            b = z > Z
            if not b.any(): continue
            nx = (xx - cx) / r; ny = (yy - cy) / r; nz = np.sqrt(np.maximum(0, 1 - nx * nx - ny * ny))
            s = nx * L[0] + ny * L[1] + nz * L[2]
            # clumps higher in the crown / nearer the light get lighter ramps
            lift = 0.9 * (1 - cy / h) + 0.4 * (cx / w)
            tone = np.clip(np.digitize(s + lift * 0.35 - 0.2, [0.1, 0.38, 0.62, 0.84]), 0, 4)
            Z[b] = z[b]; T[b] = tone[b]
        # serrated leaf stamps along the top/outer silhouette
        mm = T >= 0; edge = mm & ~np.roll(mm, 1, 0); ys, xs = np.nonzero(edge)
        for i in rng.choice(len(ys), len(ys) // 3, replace=False):
            s_ = LEAF[rng.randint(len(LEAF))]; y, x = ys[i] - s_.shape[0] + 1, xs[i] - 1; t_ = T[ys[i], xs[i]]
            for j in range(s_.shape[0]):
                for q in range(s_.shape[1]):
                    if s_[j, q] and 0 <= y + j < h and 0 <= x + q < w and T[y + j, x + q] < 0: T[y + j, x + q] = t_
        # branches: short dark limbs from inside the crown out into a leaf gap (never floating)
        for (x0, y0, x1, y1) in ((20, 100, 46, 70), (8, 70, 34, 44)):
            for s_ in np.linspace(0, 1, 40):
                x = int(round(x0 + (x1 - x0) * s_)); y = int(round(y0 + (y1 - y0) * s_ + 4 * np.sin(s_ * 3)))
                if 0 <= x < w and 0 <= y < h and T[y, x] >= 0 and T[y, x] <= 2: T[y, x] = 5
        if side > 0: T = T[:, ::-1]
        return T
    def foliage(self, img, P, t, off, f):
        nt = self._nt
        base = [(12, 24, 30), (18, 40, 40), (28, 60, 48), (48, 88, 54), (88, 122, 60)]
        dusk_t = ss((t - 0.25) / 0.35)
        cols = []
        for q, c in enumerate(base):
            c = m3(c, P["H"], 0.18 * q / 4)                          # sunset warms the lit clumps
            c = m3(c, m3(c, (40, 36, 70), 0.5), dusk_t)
            c = m3(c, [(8, 16, 26), (12, 26, 36), (18, 38, 48), (28, 56, 62), (46, 80, 84)][q], nt)
            cols.append(np.clip(c, 0, 255).astype(np.uint8))
        branch = np.clip(m3((58, 34, 30), (22, 20, 30), nt), 0, 255).astype(np.uint8)
        top = max(0, TOP0 - int(round(off * 1.25)))
        dy = int(round(off * 1.8)) - int(round(off * 1.25))
        for side in (-1, 1):
            T = self._fol[side]; h, w = T.shape
            X0 = -4 if side < 0 else W - w + 4; Y0 = top + H - h + 6 + dy
            ya, yb = max(0, Y0), min(CH, Y0 + h); xa, xb = max(0, X0), min(W, X0 + w)
            if ya >= yb: continue
            tt = T[ya - Y0:yb - Y0, xa - X0:xb - X0]; reg = img[ya:yb, xa:xb]
            for q in range(5): reg[tt == q] = cols[q]
            reg[tt == 5] = branch
    def frame(self, f):
        t = f / (N - 1); P = self.palette(t); self._nt = ss((t - 0.28) / 0.34)
        off = int(round(96 * ss((f - 100) / 60)))           # night hills hold a beat before the tilt up
        img = np.zeros((CH, W, 3), np.uint8)
        self.sky(img, P, t); self.sun(img, P, t); self.star_layer(img, P, t, f); self.night_sky(img, P, t, f)
        self.cloud_layer(img, P, f, off); self.hills(img, P, t, off, f); self.foliage(img, P, t, off, f)
        for b, (x0, y0, sp) in enumerate(((W + 8, HZ - 70, 3), (W + 20, HZ - 64, 3), (W + 30, HZ - 74, 4))):
            x = x0 - f // sp; y = y0 + int(np.sin(f / 7 + b)) + int(off * 0.3); flap = (f // 4 + b) % 2
            for dx, dyy in ((0, 0), (-1, -1 + (0 if flap else 1)), (1, -1 + (0 if flap else 1)), (-2, -1 if flap else 0), (2, -1 if flap else 0)):
                if 0 <= x + dx < W and 0 <= y + dyy < CH: img[y + dyy, x + dx] = mix(P["A"], (20, 14, 30), 0.5)
        top = max(0, TOP0 - int(round(off * 1.25)))
        return img[top:top + H]
