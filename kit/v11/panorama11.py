"""v11 ending panorama: same shot/timing/interface as v10 (Pano(lut0).frame(f) / backdrop(f), N=168, tilt up at the
end), redrawn layers: clean many-step banded sky (no checker rows), shaded cumulus banks (clouds11), organic ridge
rows with atmospheric perspective (hills11b + colour11), leaf-stamp foliage corners without floating twigs.
Sun, stars, Milky Way and moon are kept from v10. 1-px grain at 384x216."""
import sys, numpy as np
sys.path.insert(0, '/workspace/robot2d/kit/v11'); sys.path.insert(0, '/workspace/robot2d/kit/v10')
import panorama10 as P10
from panorama10 import W, H, CH, N, HZ, ss, mix, shade, CRED_BG
import clouds11 as CL, hills11b as HB, colour11 as C11
PAR = [0.35, 0.45, 0.58, 0.72, 0.86, 1.0]
def m3(a, b, t): return np.array(a, float) * (1 - t) + np.array(b, float) * t
LEAF = [np.array(s) for s in (
    [[0, 1, 1, 0], [1, 1, 1, 1], [0, 1, 1, 0]],
    [[0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 0], [1, 0, 0, 0]],
    [[1, 1, 0, 0], [1, 1, 1, 0], [0, 1, 1, 1], [0, 0, 0, 1]],
    [[0, 1, 0], [1, 1, 1], [1, 1, 1], [0, 1, 0]])]
class Pano(P10.Pano):
    def __init__(self, lut0):
        super().__init__(lut0)
        self.banks = CL.make_banks()
        self.hr = HB.render_rows()
        # each row's mask continues down to the canvas bottom (hidden valley, deep tone) so different parallax per row
        # never opens a gap onto the sky between rows
        r = self.hr; self.rowm = []; self.rowt = []
        for k in range(r["n"]):
            m = r["row"] == k; ext = np.maximum.accumulate(m, axis=0)
            t_ = np.clip(r["tone"] - np.floor(r["vf"] * 2.4).astype(int), 0, 4); t_ = np.where(m, t_, 0)
            self.rowm.append(ext); self.rowt.append(t_)
        rng = np.random.RandomState(31)
        self.vill = [(int(x), rng.rand()) for x in rng.randint(40, W - 40, 12)]
    def sky(self, img, P, dusk):
        stops = [(0, mix(P["A"], CRED_BG, 0.55)), (70, P["A"]), (150, P["F"]), (195, P["G"]), (222, P["H"]), (240, P["I"]), (HZ, P["D"])]
        def col(y):
            for (a, ca), (b, cb) in zip(stops, stops[1:]):
                if a <= y <= b: return mix(ca, cb, (y - a) / (b - a))
            return stops[-1][1]
        # clean bands, narrower toward the horizon where the colour changes fastest; no dither rows
        ys = sorted(set([0] + [int(HZ * (1 - (1 - i / 44) ** 1.35)) for i in range(45)]))
        for a, b in zip(ys, ys[1:]): img[a:b] = col((a + b) / 2)
        img[HZ:] = P["D"]
    def sun(self, img, P, t):
        cy = HZ - 24 + int(round(44 * ss(t / 0.5))); cx = 192; R = 15
        yy, xx = np.mgrid[0:CH, 0:W]; d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2); sky = yy < HZ
        for rr, k in ((R + 30, 0.18), (R + 19, 0.36), (R + 10, 0.6), (R + 4, 0.85)):      # clean glow bands
            m = (d < rr) & sky; img[m] = np.clip(m3(img[m], mix(P["D"], (255, 226, 170), 0.3), k * 0.55), 0, 255).astype(np.uint8)
        fade = ss(t / 0.5) * 0.6
        m = (d < R) & sky; img[m] = mix((255, 238, 196), P["D"], fade)
        m = (d < R - 4) & sky; img[m] = mix((255, 250, 226), P["D"], fade)
    def night_sky(self, img, P, t, f):
        nt = ss((t - 0.4) / 0.45)
        if nt <= 0: return
        # Milky Way glow bands (3 steps, checker edges), only above the horizon
        above = np.zeros(img.shape[:2], bool); above[:HZ - 20] = True
        chk = ((np.arange(CH)[:, None] + np.arange(W)[None]) % 2 == 0)
        for m, k in ((self.mw_out, 0.10), (self.mw_mid, 0.2), (self.mw_core, 0.32)):
            mm = m & above
            base = img[mm].astype(float); tgt = np.array([150, 140, 200], float)
            img[mm] = (base + (tgt - base) * k * nt).astype(np.uint8)
        ln = self.mw_lane & above; img[ln] = (img[ln].astype(float) * (1 - 0.35 * nt)).astype(np.uint8)
        d = self.mw_dust & above & (((f + self.mw_ph) // 16) % 3 != 0)
        img[d] = (img[d].astype(float) * (1 - 0.6 * nt) + np.array([226, 222, 240]) * 0.6 * nt).astype(np.uint8)
        # moon: cratered disc with a soft banded glow
        mx, my, R = self.moon
        yy, xx = np.mgrid[0:CH, 0:W]; dd = np.sqrt((xx - mx) ** 2 + (yy - my) ** 2)
        for rr, k in ((R + 16, 0.08), (R + 9, 0.15), (R + 4, 0.24)):
            m = dd < rr
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
    def cloud_layer(self, img, P, f, off):
        nt = self._nt
        for b in self.banks:
            d = b["depth"]
            dx = (f // (16 if d else 11)) * (1 if b["side"] < 0 else -1)
            dy = int(off * (0.25 if d else 0.35))
            body = m3(m3(m3(P["G"], P["F"], 0.3), P["D"], 0.25 + 0.12 * d), (56, 58, 94) if d else (70, 72, 110), nt)
            cool = m3((70, 60, 120), (40, 42, 84), nt)
            warm = m3((255, 236, 200), (168, 174, 210), nt)
            cols = [m3(body, cool, 0.45), m3(body, cool, 0.2), body, m3(body, m3(P["D"], (120, 126, 170), nt), 0.5), m3(body, warm, 0.6)]
            cols = [np.clip(c, 0, 255).astype(np.uint8) for c in cols]
            rimc = np.clip(m3(m3(P["D"], (255, 244, 220), 0.6), (186, 192, 224), nt), 0, 255).astype(np.uint8)
            t = b["tone"]; h, w = t.shape; X0 = b["x0"] + dx; Y0 = b["y0"] + dy
            xa, xb, ya, yb = max(0, X0), min(W, X0 + w), max(0, Y0), min(CH, Y0 + h)
            if xa >= xb or ya >= yb: continue
            tt = t[ya - Y0:yb - Y0, xa - X0:xb - X0]; rr = b["rim"][ya - Y0:yb - Y0, xa - X0:xb - X0]; reg = img[ya:yb, xa:xb]
            for k in range(5): reg[tt == k] = cols[k]
            reg[rr & (tt >= 0)] = rimc
    def hills(self, img, P, t, off, f):
        r = self.hr; nt = self._nt
        cols = C11.hill_colours(P, nt, r["n"])
        for k in range(r["n"]):
            dy = int(round(off * 1.4 * PAR[k]))
            m = self.rowm[k]; tone = self.rowt[k]
            if dy: m = np.vstack([np.zeros((dy, W), bool), m[:-dy]]); tk = np.vstack([np.zeros((dy, W), int), tone[:-dy]]); rim = np.vstack([np.zeros((dy, W), bool), r["rim"][:-dy]])
            else: tk = tone; rim = r["rim"]
            cc = [np.clip(c, 0, 255).astype(np.uint8) for c in cols[k]]
            for q in range(5): img[m & (tk == q)] = cc[q]
            if nt < 0.3: img[m & rim & (r["row"] == k) if not dy else m & rim] = cc[5]          # warm crest rim only while the sun is up
            if k == 1:                                     # village lights come on at dusk
                for (vx, th) in self.vill:
                    if th < ss((t - 0.35) / 0.5) and ((f // 20 + vx) % 7):
                        col = np.nonzero(m[:, vx])[0]
                        if len(col):
                            y = col[0] + 5
                            for dxx in (0, 2):
                                if y < CH and m[y, min(W - 1, vx + dxx)]: img[y, vx + dxx] = (255, 206, 120)
    def _fol_sprite(self, side):
        """corner foliage mass: clusters of shaded lobes (clouds11 shader) + serrated leaf stamps on the lit edge"""
        rng = np.random.RandomState(9 if side < 0 else 19)
        w, h = 120, 150; lobes = []
        for k in range(13):
            u = k / 12.0
            cx = 0 + 46 * (1 - u) ** 1.3 + rng.uniform(-8, 8); cy = h - 6 - 84 * u ** 1.15 + rng.uniform(-5, 5)
            R = rng.uniform(10, 15) - 5 * u
            lobes.append((cx, cy, R)); lobes.append((cx - 18 * (1 - u) - 10, cy + 16, R + 2))
            for q in range(14):
                a = rng.uniform(-3.0, 0.6); rr_ = R * rng.uniform(0.55, 1.0); r = rng.uniform(4, 8)
                lobes.append((cx + np.cos(a) * rr_, cy + np.sin(a) * rr_, r))
        tone, rim = CL.shade_bank(lobes, w, h, L=(0.6, -0.6, 0.55))
        m = tone >= 0
        # leaf stamps poking out of the upper/outer silhouette (small serration, no stems)
        edge = m & ~np.roll(m, 1, 0)
        ys, xs = np.nonzero(edge)
        for i in rng.choice(len(ys), len(ys) // 3, replace=False):
            s_ = LEAF[rng.randint(len(LEAF))]; y, x = ys[i] - s_.shape[0] + 1, xs[i] - 1
            t = min(4, tone[ys[i], xs[i]] + 0)
            for j in range(s_.shape[0]):
                for q in range(s_.shape[1]):
                    if s_[j, q] and 0 <= y + j < h and 0 <= x + q < w and tone[y + j, x + q] < 0: tone[y + j, x + q] = t
        # interior leaf texture: small leaf stamps one tone darker, dense in the lit tones
        ys, xs = np.nonzero(tone >= 2)
        for i in rng.choice(len(ys), len(ys) // 22, replace=False):
            s_ = LEAF[rng.randint(len(LEAF))]; y, x = ys[i], xs[i]; t0 = tone[y, x] - 1
            for j in range(s_.shape[0]):
                for q in range(s_.shape[1]):
                    if s_[j, q] and y + j < h and x + q < w and tone[y + j, x + q] >= 1 and (j + q) % 3 != 1: tone[y + j, x + q] = t0
        rim = (tone >= 3) & ~np.roll(tone >= 0, 1, 0)
        if side > 0: tone = tone[:, ::-1]; rim = rim[:, ::-1]
        return tone, rim
    def foliage(self, img, P, t, off, f):
        if not hasattr(self, "_fol"): self._fol = {s: self._fol_sprite(s) for s in (-1, 1)}
        nt = self._nt
        d = [(16, 12, 26), (24, 19, 36), (36, 28, 50), (54, 40, 64), (80, 56, 78)]
        d[4] = tuple(int(v) for v in m3(m3(d[4], P["H"], 0.35), (60, 70, 96), nt))
        d[3] = tuple(int(v) for v in m3(d[3], (44, 50, 74), nt))
        rimc = tuple(int(v) for v in m3(m3(P["H"], P["D"], 0.35), (110, 120, 150), nt))
        dy = int(round(off * 1.8))
        for side in (-1, 1):
            tone, rim = self._fol[side]; h, w = tone.shape
            X0 = -6 if side < 0 else W - w + 6; Y0 = CH - h + dy
            ya, yb = max(0, Y0), min(CH, Y0 + h)
            if ya >= yb: continue
            xa, xb = max(0, X0), min(W, X0 + w)
            tt = tone[ya - Y0:yb - Y0, xa - X0:xb - X0]; rr = rim[ya - Y0:yb - Y0, xa - X0:xb - X0]; reg = img[ya:yb, xa:xb]
            for k in range(5): reg[tt == k] = d[k]
            reg[rr] = rimc
