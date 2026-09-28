"""Cut v08: Godot wide chunks + native close-ups (5x nearest) + fades, muxed with the mixed soundtrack."""
import subprocess, sys, numpy as np
from PIL import Image
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import edl08
out = sys.argv[1] if len(sys.argv) > 1 else "/workspace/robot2d/robot_story_full_08.mp4"
pix = sys.argv[2] if len(sys.argv) > 2 else "yuv420p"
FR = edl08.frames()
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", "24", "-i", "-",
    "-i", "/workspace/robot2d/audio/robot_story_08_mix.wav",
    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-crf", "8", "-pix_fmt", pix,
    "-af", "acompressor=threshold=0.25:ratio=2:attack=8:release=120,alimiter=limit=0.8:attack=4:release=60,loudnorm=I=-16:TP=-1.5:LRA=11",
    "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
for path, g in FR:
    im = Image.open(path).convert("RGB")
    if im.size != (1920, 1080): im = im.resize((1920, 1080), Image.NEAREST)
    a = np.asarray(im)
    if g < 1.0: a = (a.astype(np.float32) * (g * g * (3 - 2 * g))).astype(np.uint8)
    p.stdin.write(a.tobytes())
p.stdin.close(); p.wait(); print(len(FR), "frames", len(FR) / 24, "s ->", out)
