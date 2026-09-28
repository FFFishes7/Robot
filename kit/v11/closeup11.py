"""v11 close-ups = option B (see closeup_research.md): a full-screen zoom cut. Each frame of a close-up is a 128x72
window of the FINAL wide frame's native pixels (read at 5x5 block centres, grid aligned via the camera offset),
enlarged x3 by pure nearest neighbour -> 384x216 native-screen (x5 again in assembly). Nothing is redrawn.
The window is locked per shot in world coords, framed on the subject's union bbox over the whole shot
(robot sprite alpha + device / calendar), so nothing is cut off and the framing does not jitter."""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); from paths import KIT
sys.path.insert(0, KIT + 'v11'); sys.path.insert(0, KIT + 'v10')
import insets11 as I, panels10 as P
WN, HN = 128, 72
# subject boxes (albedo/world coords): device (258-274, 77-89), calendar (245-256, 78-93), robot = per-shot sprite union
SUBJ = dict(task=[(258, 76, 275, 95)], cal=[(245, 75, 257, 94)], face=[], press=[(258, 76, 275, 95)])
_crop = {}
def robot_union(a, b):
    from PIL import Image
    bs = []
    for r in sorted(set(P.G('robot', F) for F in range(a, b))):
        al = P.L(P.RF + f'{r}_a.png')[..., 3] > 0; ys, xs = np.nonzero(al); bs.append((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    return (min(x[0] for x in bs), min(x[1] for x in bs), max(x[2] for x in bs), max(x[3] for x in bs))
def crop_for(name):
    if name in _crop: return _crop[name]
    a, b = P.MK['panels'][name]
    boxes = SUBJ[name] + [robot_union(a, b)]
    x0 = min(q[0] for q in boxes); y0 = min(q[1] for q in boxes); x1 = max(q[2] for q in boxes); y1 = max(q[3] for q in boxes)
    assert x1 - x0 <= WN - 8 and y1 - y0 <= HN - 8, (name, x0, y0, x1, y1)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if name == 'face': cy -= 4                                  # head room: favour the head
    X, Y = int(round(cx - WN / 2)), int(round(cy - HN / 2))
    # keep inside the visible wide for every frame of the shot
    vx0 = max((P.cam(F)[0] + 4) // 5 for F in range(a, b)); vy0 = max((P.cam(F)[1] + 4) // 5 for F in range(a, b))
    vx1 = min(P.cam(F)[0] // 5 + 383 for F in range(a, b)); vy1 = min(P.cam(F)[1] // 5 + 215 for F in range(a, b))
    X = int(np.clip(X, vx0, vx1 - WN)); Y = int(np.clip(Y, vy0, vy1 - HN))
    assert X <= x0 and Y <= y0 and X + WN >= x1 and Y + HN >= y1, (name, 'subject cut')
    _crop[name] = (X, Y); return X, Y
def zoom_native(a, F, X, Y):
    """a = final wide frame (1920x1080); returns 72x128 native window"""
    return I.native_crop(a, F, (X - P.OX, Y - P.OY, X - P.OX + WN, Y - P.OY + HN))
def closeup(a, F, name):
    X, Y = crop_for(name); nat = zoom_native(a, F, X, Y)
    return np.repeat(np.repeat(nat, 3, 0), 3, 1)                  # 216x384, pure integer nearest
def check(a, F, name):
    """grid alignment check: within-block std of the source blocks (should be ~0)"""
    X, Y = crop_for(name); cx, cy = P.cam(F)
    x0 = X * 5 - cx; y0 = Y * 5 - cy; blk = a[y0:y0 + HN * 5, x0:x0 + WN * 5].astype(float).reshape(HN, 5, WN, 5, 3)
    return float(blk.std(axis=(1, 3)).mean())
