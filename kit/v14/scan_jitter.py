"""Scan a film for whole-frame shifts between consecutive frames (phase correlation, screen pixels) and for local
tile shifts (sprite/prop jitter).  Output: json with per-frame global shift + per-tile shifts."""
import subprocess, sys, json, numpy as np
src = sys.argv[1]; out = sys.argv[2]
W, H = 1920, 1080
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
def pc(a, b):
    A = np.fft.rfft2(a); B = np.fft.rfft2(b); R = A * np.conj(B); R /= np.abs(R) + 1e-9
    r = np.fft.irfft2(R, a.shape); i = np.unravel_index(np.argmax(r), r.shape)
    dy, dx = [(v if v < s // 2 else v - s) for v, s in zip(i, a.shape)]
    return int(dx), int(dy), float(r[i])
TS = 120                                                   # tile size (24 native px)
prev = None; res = []; n = 0
while True:
    buf = p.stdout.read(W * H)
    if len(buf) < W * H: break
    f = np.frombuffer(buf, np.uint8).reshape(H, W).astype(np.float32)
    if prev is not None:
        same = np.array_equal(f, prev)
        dx, dy, pk = (0, 0, 1.0) if same else pc(f, prev)
        tiles = []
        if not same:
            d = np.abs(f - prev)
            for ty in range(0, H, TS):
                for tx in range(0, W, TS):
                    a = f[ty:ty + TS, tx:tx + TS]; b = prev[ty:ty + TS, tx:tx + TS]
                    if d[ty:ty + TS, tx:tx + TS].mean() < 0.5 or a.std() < 4: continue
                    tdx, tdy, tpk = pc(a, b)
                    if (tdx, tdy) != (dx, dy) and tpk > 0.3 and abs(tdx) <= 10 and abs(tdy) <= 10: tiles.append((tx, ty, tdx, tdy, round(tpk, 2)))
        res.append(dict(n=n, dx=dx, dy=dy, pk=round(pk, 3), same=same, tiles=tiles))
    prev = f; n += 1
json.dump(res, open(out, "w")); print(n, "frames")
