"""v08 sky overlays for the time pass: night (deep blue, stars, moon) and dawn; masks = window glass from emit_win07."""
import numpy as np, random
from PIL import Image
V = '../v07/'
E = np.array(Image.open(V + 'emit_win07.png').convert('RGBA')); m = E[..., 3] > 0
mul = m & (((E[..., 0] == 201) & (E[..., 1] == 130)) | ((E[..., 0] == 173) & (E[..., 1] == 100)))
lit = (E[..., 0] == 201) & (E[..., 1] == 130)
H, W = m.shape; ys, xs = np.nonzero(m); y0, y1 = ys.min(), ys.max()
def grad(stops):
    out = np.zeros((H, W, 4), np.uint8)
    for y in range(y0, y1 + 1):
        t = (y - y0) / (y1 - y0)
        for (ta, ca), (tb, cb) in zip(stops, stops[1:]):
            if ta <= t <= tb:
                u = (t - ta) / (tb - ta); c = [round(ca[i] + (cb[i] - ca[i]) * u) for i in range(3)]; break
        row = m[y]; out[y, row, :3] = c; out[y, row, 3] = 255
    return out
night = grad([(0, (10, 14, 40)), (0.6, (20, 28, 66)), (1, (40, 46, 96))])
dawn = grad([(0, (104, 128, 184)), (0.5, (214, 164, 170)), (1, (255, 214, 168))])
# bands like the painted sky (keep the room's banded look): quantise night into 3 steps
ne = np.zeros_like(night); ne[..., 3] = 0
random.seed(4); stars = []
while len(stars) < 26:
    x, y = random.randint(xs.min(), xs.max()), random.randint(y0, y0 + 18)
    if m[y, x] and m[y, x - 1] and m[y, x + 1] and m[y + 1, x]: stars.append((x, y))
for i, (x, y) in enumerate(stars):
    c = (255, 246, 216) if i % 3 else (200, 210, 255)
    night[y, x, :3] = c; ne[y, x] = (*c, 255)
    if i % 7 == 0:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            night[y + dy, x + dx, :3] = (120, 130, 180); ne[y + dy, x + dx] = (90, 100, 150, 255)
# moon (crescent) in the left window
mx, my = 166, 62
for dy in range(-2, 3):
    for dx in range(-2, 3):
        if dx * dx + dy * dy <= 5 and (dx + 1) ** 2 + dy * dy > 3 and m[my + dy, mx + dx]:
            night[my + dy, mx + dx, :3] = (240, 236, 208); ne[my + dy, mx + dx] = (240, 236, 208, 255)
night[mul, :3] = (34, 24, 30); night[lit, :3] = (54, 40, 48); dawn[mul, :3] = (120, 84, 64); dawn[lit, :3] = (170, 120, 84); ne[mul] = 0
Image.fromarray(night).save('sky_night08.png'); Image.fromarray(ne).save('sky_night_e08.png'); Image.fromarray(dawn).save('sky_dawn08.png')
print('ok', len(stars))
