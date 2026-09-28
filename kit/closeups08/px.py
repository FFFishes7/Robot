"""Tiny native-res pixel drawing kit for the v07 close-ups (384x216, hard pixels, no AA)."""
import numpy as np
from PIL import Image
W, H = 384, 216
def hx(c): return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)], np.uint8)
yy, xx = np.mgrid[0:H, 0:W]
class Cv:
    def __init__(s, bg="#000000"): s.a = np.zeros((H, W, 3), np.uint8); s.a[:] = hx(bg)
    def put(s, m, c): s.a[m] = hx(c)
    def px(s, x, y, c):
        if 0 <= x < W and 0 <= y < H: s.a[y, x] = hx(c)
    def save(s, p, scale=1):
        im = Image.fromarray(s.a); (im.resize((W * scale, H * scale), Image.NEAREST) if scale > 1 else im).save(p)
def rrect(x0, y0, x1, y1, r):
    """inclusive rounded-rect mask with pixel-art corners"""
    m = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
    if r > 0:
        for cx, cy, sx, sy in ((x0 + r, y0 + r, -1, -1), (x1 - r, y0 + r, 1, -1), (x0 + r, y1 - r, -1, 1), (x1 - r, y1 - r, 1, 1)):
            q = ((xx - cx) * sx > 0) & ((yy - cy) * sy > 0)
            m &= ~(q & ((xx - cx) ** 2 + (yy - cy) ** 2 > (r + 0.35) ** 2))
    return m
def ell(cx, cy, rx, ry):
    return ((xx - cx) / (rx + 0.3)) ** 2 + ((yy - cy) / (ry + 0.3)) ** 2 <= 1.0
def edge(m):
    """1px outer ring around mask m"""
    n = np.zeros_like(m)
    n[1:, :] |= m[:-1, :]; n[:-1, :] |= m[1:, :]; n[:, 1:] |= m[:, :-1]; n[:, :-1] |= m[:, 1:]
    return n & ~m
def inner(m, k=1):
    e = m.copy()
    for _ in range(k):
        n = e.copy(); n[1:, :] &= e[:-1, :]; n[:-1, :] &= e[1:, :]; n[:, 1:] &= e[:, :-1]; n[:, :-1] &= e[:, 1:]; e = n
    return e
def shift(m, dx, dy): return np.roll(np.roll(m, dy, 0), dx, 1)
def checker(ph=0): return ((xx + yy + ph) % 2) == 0
def line_pts(x0, y0, x1, y1):
    pts = []; dx = abs(x1 - x0); dy = -abs(y1 - y0); sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1; e = dx + dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1: break
        e2 = 2 * e
        if e2 >= dy: e += dy; x0 += sx
        if e2 <= dx: e += dx; y0 += sy
    return pts
def thick_line(x0, y0, x1, y1, w):
    m = np.zeros((H, W), bool)
    for (x, y) in line_pts(x0, y0, x1, y1): m |= ell(x, y, w / 2 - 0.5, w / 2 - 0.5)
    return m
