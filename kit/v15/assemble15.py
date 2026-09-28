"""v15 = v13 with the slow stray camera steps removed (cam15 -> timeline15.json, wide renders in build/w15_*; moves stay on
output pixels like v13, not v14's native-pixel steps) and the v14 night tilt end (panorama14). Same cut, timing and
audio (robot_story_13_mix.wav) as v13.
v13 = v12 + 2.5 s hold on the window close-up (edl13), panorama without corner trees (panorama13), cleaned credits icon (credits13), audio13.
Assemble v12 (v11 cut + main12 wide renders + panorama12): Godot wide frames (+ page-turn patches); close-ups = full-screen x3 nearest zoom cuts of the final
wide frame (closeup11, option B -- no framed insets); the interior sunset shot = the same x3 zoom of the wide window
area, entered with an 8-frame dissolve; the redrawn ending panorama (panorama11); credits; v10 soundtrack (timing
unchanged)."""
import os, subprocess, sys, json, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); from paths import ROOT, KIT, BUILD
for d in ("robot10", "v10", "v11", "v12", "v13", "v14"): sys.path.insert(0, KIT + d)
import edl13 as E
import panels10 as P
# the close-up sampler and the page-turn patches must read the SAME camera and wide frames as the render
P.TL = json.load(open(P.RF + "timeline15.json"))
def _wide_path15(F):
    S = max(s for s in (0, 300, 600, 900, 1200) if s <= F); return f"{BUILD}w15_{S}/f{6 + F - S:08d}.png"
P.wide_path = _wide_path15
import gen_panels10 as G
G.calfx_patches()                                    # before insets11, which loads the patches at import
import sunset10 as SS, credits13 as CR
import panorama14 as PN, closeup11 as C, insets11 as I
out = sys.argv[1] if len(sys.argv) > 1 else ROOT + "robot_story_full_15.mp4"
pix = sys.argv[2] if len(sys.argv) > 2 else "yuv420p"
only = sys.argv[3] if len(sys.argv) > 3 else None
SHOTS = {n: P.MK["panels"][n] for n in ("task", "cal", "face", "press")}
SUN_XY = (SS.REG[0] + P.OX, SS.REG[1] + P.OY)         # world origin of the sunset window framing (128x72)
DISS = 8
def up5(a): return np.repeat(np.repeat(a, 5, 0), 5, 1)
def shot_of(F):
    for n, (a, b) in SHOTS.items():
        if a <= F < b: return n
    return None
def zoom_at(w, F, X, Y): return up5(np.repeat(np.repeat(C.zoom_native(w, F, X, Y), 3, 0), 3, 1))
def frames():
    pano = None
    for seg in E.segments():
        kind = seg[0]
        if kind == "wide":
            for F in range(seg[1], seg[2]):
                w = I.wide_base(F); n = shot_of(F)
                a = up5(C.closeup(w, F, n)) if n else w
                if F < 20: a = (a.astype(np.float32) * ((F + 1) / 21) ** 1.5).astype(np.uint8)
                yield a
        elif kind == "sunset":
            for F in range(seg[1], seg[2]):
                w = I.wide_base(F); z = zoom_at(w, F, *SUN_XY); j = F - seg[1]
                if j < DISS:
                    k = (j + 1) / (DISS + 1); z = (w.astype(np.float32) * (1 - k) + z.astype(np.float32) * k).astype(np.uint8)
                yield z
        elif kind == "pano":
            pano = PN.Pano(SS.band_lut(seg[1]))
            c0 = np.array(CR.frame(0, backdrop=pano.backdrop(0))).astype(np.float32)
            for f in range(seg[2]):
                a = pano.frame(f).astype(np.float32)
                k = max(0, min(4, (seg[2] - 1 - f) // 3))
                a = c0 + (a - c0) * (k / 4.0)
                yield up5(a.astype(np.uint8))
        elif kind == "cred":
            for i in range(seg[2]): yield up5(np.array(CR.frame(i, backdrop=pano.backdrop(seg[2] + i))))
if __name__ == "__main__":
    if only:
        a0, b0 = map(int, only.split(":")); os.makedirs(BUILD + "v15prev", exist_ok=True)
        for i, fr in enumerate(frames()):
            if i >= b0: break
            if i >= a0: Image.fromarray(fr).save(f"{BUILD}v15prev/{i:05d}.png")
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", "24", "-i", "-",
        "-i", ROOT + "audio/robot_story_13_mix.wav",
        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-crf", "8", "-pix_fmt", pix,
        "-af", "acompressor=threshold=0.25:ratio=2:attack=8:release=120,alimiter=limit=0.8:attack=4:release=60,loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    n = 0
    for fr in frames(): p.stdin.write(np.ascontiguousarray(fr).tobytes()); n += 1
    p.stdin.close(); p.wait(); print(n, "frames", n / 24, "s ->", out)
