"""Assemble v10: Godot wide frames + inset panels (5x nearest, screen space) + page-turn patches, the interior sunset
shot, the ending panorama, the credits; muxed with the v10 soundtrack."""
import subprocess, sys, json, numpy as np
from PIL import Image
sys.path.insert(0, "/workspace/robot2d/kit/robot10"); sys.path.insert(0, "/workspace/robot2d/kit/v10")
import edl10 as E
import panels10 as P
import panorama10 as PN, sunset10 as SS, credits10 as CR
out = sys.argv[1] if len(sys.argv) > 1 else "/workspace/robot2d/robot_story_full_10.mp4"
pix = sys.argv[2] if len(sys.argv) > 2 else "yuv420p"
only = sys.argv[3] if len(sys.argv) > 3 else None          # "a:b" to dump PNG frames instead (preview)
IDX = json.load(open("/tmp/p10/index.json")); CFX = json.load(open("/tmp/p10/calfx.json"))
def up5(a): return np.repeat(np.repeat(a, 5, 0), 5, 1)
def wide(F):
    a = np.array(Image.open(P.wide_path(F)).convert("RGB"))
    if str(F) in CFX:                                   # page-turn pixels (world native -> screen 5x)
        p = np.array(Image.open(f"/tmp/p10/calfx_{F}.png")); bx, by = CFX[str(F)]; cx, cy = P.cam(F)
        X, Y = bx * 5 - cx, by * 5 - cy; q = up5(p); m = q[..., 3] > 0
        sub = a[Y:Y + q.shape[0], X:X + q.shape[1]]; sub[m] = q[..., :3][m]
    if str(F) in IDX:
        name, x, y = IDX[str(F)]; p = np.array(Image.open(f"/tmp/p10/{F}.png")); q = up5(p)
        al = q[..., 3:4].astype(np.float32) / 255; sub = a[y * 5:y * 5 + q.shape[0], x * 5:x * 5 + q.shape[1]]
        sub[:] = (sub * (1 - al) + q[..., :3] * al).astype(np.uint8)
    return a
def frames():
    pano = None
    for seg in E.segments():
        kind = seg[0]
        if kind == "wide":
            for F in range(seg[1], seg[2]):
                a = wide(F)
                if F < 20: a = (a.astype(np.float32) * ((F + 1) / 21) ** 1.5).astype(np.uint8)
                yield a
        elif kind == "sunset":
            for F in range(seg[1], seg[2]): yield up5(SS.shot(F, F - seg[1])[..., :3])
        elif kind == "pano":
            pano = PN.Pano(SS.band_lut(seg[1]))
            c0 = np.array(CR.frame(0, backdrop=pano.backdrop(0))).astype(np.float32)
            for f in range(seg[2]):
                a = pano.frame(f).astype(np.float32)
                k = max(0, min(4, (seg[2] - 1 - f) // 3))          # 4-step crossfade into the credits' night sky
                a = c0 + (a - c0) * (k / 4.0)
                yield up5(a.astype(np.uint8))
        elif kind == "cred":
            for i in range(seg[2]): yield up5(np.array(CR.frame(i, backdrop=pano.backdrop(seg[2] + i))))
if only:
    a0, b0 = map(int, only.split(":"))
    for i, fr in enumerate(frames()):
        if i >= b0: break
        if i >= a0: Image.fromarray(fr).save(f"/tmp/v10prev/{i:05d}.png")
    sys.exit()
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", "24", "-i", "-",
    "-i", "/workspace/robot2d/audio/robot_story_10_mix.wav",
    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-crf", "8", "-pix_fmt", pix,
    "-af", "acompressor=threshold=0.25:ratio=2:attack=8:release=120,alimiter=limit=0.8:attack=4:release=60,loudnorm=I=-16:TP=-1.5:LRA=11",
    "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
n = 0
for fr in frames(): p.stdin.write(np.ascontiguousarray(fr).tobytes()); n += 1
p.stdin.close(); p.wait(); print(n, "frames", n / 24, "s ->", out)
