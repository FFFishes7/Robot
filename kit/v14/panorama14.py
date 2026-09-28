"""v14 panorama = v13 (no corner trees) with a clean end to the night tilt.
v13 bug: off = round(96 * ss(..)) but the frame top TOP0 - round(off * 1.25) hits row 0 at off ~77, so the camera stopped
dead at pano f143 (film 1633) while the parallax layers driven by off kept sliding for 17 more frames (clouds dropping
1 px at a time under a static sky = stray 1-px shifts). The integer off also made the sky step 1,1,1,2 px unevenly.
v14: off is a float that ends exactly where the frame top reaches row 0 (96 / 1.25 = 76.8), eased with the same
smoothstep over the same f100..160, and each layer rounds its own offset once -> every layer moves monotonically and
everything comes to rest together.  Nothing else changes."""
import sys, numpy as np
sys.path.insert(0, '/workspace/robot2d/kit/v13'); sys.path.insert(0, '/workspace/robot2d/kit/v12')
import panorama13 as P13, panorama12 as P12
from panorama12 import N, W, H, CH, HZ, ss, mix, TOP0
OFF_MAX = TOP0 / 1.25
class Pano(P13.Pano):
    def frame(self, f):
        t = f / (N - 1); P = self.palette(t); self._nt = ss((t - 0.28) / 0.34)
        off = OFF_MAX * ss((f - 100) / 60)
        img = np.zeros((CH, W, 3), np.uint8)
        self.sky(img, P, t); self.sun(img, P, t); self.star_layer(img, P, t, f); self.night_sky(img, P, t, f)
        self.cloud_layer(img, P, f, off); self.hills(img, P, t, off, f); self.foliage(img, P, t, off, f)
        for b, (x0, y0, sp) in enumerate(((W + 8, HZ - 70, 3), (W + 20, HZ - 64, 3), (W + 30, HZ - 74, 4))):
            x = x0 - f // sp; y = y0 + int(np.sin(f / 7 + b)) + int(off * 0.3); flap = (f // 4 + b) % 2
            for dx, dyy in ((0, 0), (-1, -1 + (0 if flap else 1)), (1, -1 + (0 if flap else 1)), (-2, -1 if flap else 0), (2, -1 if flap else 0)):
                if 0 <= x + dx < W and 0 <= y + dyy < CH: img[y + dyy, x + dx] = mix(P["A"], (20, 14, 30), 0.5)
        top = max(0, TOP0 - int(round(off * 1.25)))
        return img[top:top + H]
