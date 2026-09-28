"""Cut the v07 film: Godot wide chunks + native close-up inserts (5x nearest) + fades -> ffmpeg."""
import subprocess, sys, numpy as np
from PIL import Image
CH = {0: "/tmp/w7b_0", 258: "/tmp/w7_258", 433: "/tmp/w7c_433", 648: "/tmp/w7c_648"}; CL = "/workspace/robot2d/kit/closeups07/"
def wide(F):
    S = max(s for s in CH if s <= F); return f"{CH[S]}/f{6 + F - S:08d}.png"
EDL = []   # (path, fade multiplier)
def span(a, b, fin=0, fout=0):
    for F in range(a, b):
        g = 1.0
        if fin and F - a < fin: g = (F - a + 1) / (fin + 1)
        if fout and b - 1 - F < fout: g = min(g, (b - F - 1) / fout)
        EDL.append((wide(F), g))
span(0, 258, 20, 16)
EDL += [(None, 0.0)] * 10
span(258, 433, 12, 0)
EDL += [(CL + f"face/f{t:03d}.png", 1.0) for t in range(66)]
span(433, 648)
EDL += [(CL + f"device/f{t:03d}.png", 1.0) for t in range(64)]
span(648, 999, 0, 36)
if __name__ != "__main__": raise SystemExit
out = sys.argv[1] if len(sys.argv) > 1 else "/workspace/robot2d/robot_story_full_07.mp4"
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", "24", "-i", "-",
    "-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-crf", "8", "-pix_fmt", (sys.argv[2] if len(sys.argv) > 2 else "yuv420p"), "-movflags", "+faststart", out], stdin=subprocess.PIPE)
black = np.zeros((1080, 1920, 3), np.uint8)
for path, g in EDL:
    if path is None: a = black
    else:
        im = Image.open(path).convert("RGB")
        if im.size != (1920, 1080): im = im.resize((1920, 1080), Image.NEAREST)
        a = np.asarray(im)
        if g < 1.0: a = (a.astype(np.float32) * (g * g * (3 - 2 * g))).astype(np.uint8)
    p.stdin.write(a.tobytes())
p.stdin.close(); p.wait()
print(len(EDL), "frames", len(EDL) / 24, "s ->", out)
