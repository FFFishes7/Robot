import sys; sys.path.insert(0, '/workspace/robot2d/kit/v10')
import panels10 as P, numpy as np, os
from PIL import Image
REG = dict(task=(198, 50, 250, 74), cal=(174, 46, 216, 72), face=(216, 40, 256, 68), press=(198, 50, 250, 74))
def pol_task(r, i): r = P.glass(r, i); return P.eyes(r, i)
def pol_face(r, i):
    r = P.glass(r, i, tint=(170, 120, 150), warm=(214, 120, 90)); r = P.eyes(r, i, catch=(255, 196, 130)); return P.rim(r, i, (255, 190, 120), 1, 0.5)
POL = dict(task=pol_task, cal=None, face=pol_face, press=pol_task)
def sheet(items, out):
    rows = []
    for name, F in items:
        if not os.path.exists(P.wide_path(F)): print("missing", F); continue
        c, info = P.render(F, REG[name], polish=POL.get(name) if 'POL' in globals() else None)
        a = Image.fromarray(c).resize((c.shape[1] * 4, c.shape[0] * 4), Image.NEAREST)
        w = P.wide_crop(F, REG[name]).resize(a.size, Image.NEAREST)
        r = Image.new('RGB', (a.width * 2 + 8, a.height), (0, 0, 0)); r.paste(a, (0, 0)); r.paste(w, (a.width + 8, 0)); rows.append(r)
    W = max(r.width for r in rows); H = sum(r.height + 6 for r in rows)
    S = Image.new('RGB', (W, H), (0, 0, 0)); y = 0
    for r in rows: S.paste(r, (0, y)); y += r.height + 6
    S.save(out)
if __name__ == '__main__':
    it = [(a.split(':')[0], int(a.split(':')[1])) for a in sys.argv[2:]]
    sheet(it, sys.argv[1])
