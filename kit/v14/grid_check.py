"""Native-grid check: in a frame on the exact integer native grid (x5), colour edges only occur at x%5==0 / y%5==0.
Reports per frame the share of edge energy off the grid (0 = perfectly on grid)."""
import subprocess, sys, json, numpy as np
src = sys.argv[1]; W, H = 1920, 1080
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
res = []; n = 0
while True:
    b = p.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.int16)
    ex = (np.abs(np.diff(f, axis=1)).sum(2) > 24).sum(0)      # edges between column x and x+1 -> boundary at x+1
    ey = (np.abs(np.diff(f, axis=0)).sum(2) > 24).sum(1)
    px = np.array([ex[k::5].sum() for k in range(5)]); py = np.array([ey[k::5].sum() for k in range(5)])
    offx = 1 - px[4] / max(1, px.sum()); offy = 1 - py[4] / max(1, py.sum())   # boundary x+1 = 0 mod 5 -> x%5 == 4
    res.append((n, round(float(offx), 4), round(float(offy), 4), int(np.argmax(px)), int(np.argmax(py)))); n += 1
json.dump(res, open(sys.argv[2], "w"))
bad = [r for r in res if r[1] > 0.02 or r[2] > 0.02]
print(n, "frames; off-grid frames:", len(bad), bad[:20])
