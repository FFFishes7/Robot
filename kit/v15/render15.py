"""v15 wide renders: Godot Movie Maker of main12.tscn driven by timeline15.json -> build/w15_S/f%08d.png (wide frame
F = f{6+F-S} of chunk S).  Usage: render15.py [S ...] (default: every chunk).
Godot: $GODOT, else tools/godot/Godot_v*, else `godot` on PATH; on Linux without a display it runs under xvfb-run.
On Windows the Godot window must stay visible while it records (a minimised window repeats frames), so each chunk is
checked for frames that stayed identical although the camera or the robot drawing changed."""
import glob, json, os, shutil, subprocess, sys, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); from paths import ROOT, KIT, BUILD
CHUNKS = {0: 300, 300: 300, 600: 300, 900: 300, 1200: 326}
def godot():
    if os.environ.get("GODOT"): return os.environ["GODOT"]
    found = sorted(glob.glob(ROOT + "tools/godot/Godot_v*_console.exe") + glob.glob(ROOT + "tools/godot/Godot_v*.x86_64"))
    return found[-1] if found else "godot"
def render(S, L):
    D = f"{BUILD}w15_{S}"; shutil.rmtree(D, ignore_errors=True); os.makedirs(D)
    cmd = [godot(), "--path", ROOT + "godot", "--rendering-driver", "opengl3", "--write-movie", D + "/f.png", "--fixed-fps", "24",
           "--quit-after", str(L + 7), "res://main12.tscn", "--", "--mode=anim", "--tl=timeline15.json", f"--start={S - 3}"]
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"): cmd = ["xvfb-run", "-a", "-s", "-screen 0 1920x1080x24"] + cmd
    with open(D + ".log", "w") as log: subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=True)
    return sum("ERROR" in line for line in open(D + ".log", errors="replace"))
def frozen(S, L, T):
    cam, rob = T["cam"], T["robot"]; prev = None; bad = []
    for F in range(S, min(S + L, len(rob))):
        a = np.array(Image.open(f"{BUILD}w15_{S}/f{6 + F - S:08d}.png").convert("L"))
        if prev is not None and np.array_equal(a, prev) and (cam[F] != cam[F - 1] or rob[F] != rob[F - 1]): bad.append(F)
        prev = a
    return bad
if __name__ == "__main__":
    T = json.load(open(KIT + "robot09/frames/timeline15.json")); ok = True
    for S in [int(a) for a in sys.argv[1:]] or list(CHUNKS):
        L = CHUNKS[S]; errors = render(S, L); bad = frozen(S, L, T)
        print(f"chunk {S}: {len(glob.glob(f'{BUILD}w15_{S}/*.png'))} frames, {errors} errors, frozen frames: {bad or 'none'}", flush=True)
        ok &= errors == 0 and not bad
    sys.exit(0 if ok else 1)
