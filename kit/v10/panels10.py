"""v10 close-up insets (Stardew-style framed portraits over the live wide shot).
Every inset is DERIVED from the same scene the wide shows at that frame: the room albedo + device state + calendar page
(+ page-turn fx) + dust + the robot drawing of that frame, cropped around the subject, drawn up at a fixed 3x with a
grain-keeping upscaler (up3) + 1-px re-detailing, then graded to the actual Godot wide frame (per-class affine fit +
banded local light) so palette, light and colour temperature match. Props therefore sit exactly where they are in the wide."""
import json, sys, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom
sys.path.insert(0, "/workspace/robot2d/kit/v10")
import up3 as U
from detail import detail
K = "/workspace/robot2d/kit/"; V = K + "v07/"; V8 = K + "v08/"; RF = K + "robot09/frames/"
TL = json.load(open(RF + "timeline10.json")); MK = json.load(open(RF + "marks10.json"))
Z = 3; OX, OY = 56, 26
_c = {}
def L(p):
    if p not in _c: _c[p] = np.array(Image.open(p).convert("RGBA"))
    return _c[p]
def over(dst, src):
    a = src[..., 3:4].astype(np.float32) / 255
    dst[..., :3] = (dst[..., :3] * (1 - a) + src[..., :3] * a).astype(np.uint8); dst[..., 3] = np.maximum(dst[..., 3], src[..., 3])
def G(k, F, d=0): v = TL.get(k); return v[min(F, len(v) - 1)] if v else d
def wide_path(F):
    CH = [0, 300, 600, 900, 1200]; S = max(s for s in CH if s <= F); return f"/tmp/w10_{S}/f{6 + F - S:08d}.png"
def compose(F, robot=None):
    """native world RGBA + class map (0 room, 1 robot, 2 emissive) at wide frame F"""
    a = L(K + "v09/albedo09.png").copy(); cls = np.zeros(a.shape[:2], np.uint8)
    c = str(G("cal", F, "12")); over(a, L(V + f"cal_{c}07.png"))
    fx = int(G("calfx", F, 0))
    if fx: over(a, L(K + f"v10/calfx/calfx{fx}.png"))
    if G("btn", F, 0): over(a, L(V + "alarm_btn07.png"))
    over(a, L(V + f"dust{int(G('dust', F, 0))}07.png"))
    # emissive: window glass (sky blend exactly as main09), lamps, device state
    em = L(V + "emit_win07.png").copy().astype(np.float32)
    for p, w in ((V + "sky_day07.png", G("day", F)), (V + "sky_dim07.png", 0.55 * G("dusk", F)), (V8 + "sky_dawn08.png", G("dawn", F)), (V8 + "sky_night08.png", G("night", F))):
        s = L(p).astype(np.float32); al = s[..., 3:4] / 255 * w; em[..., :3] = em[..., :3] * (1 - al) + s[..., :3] * al
    em = em.astype(np.uint8); m = em[..., 3] > 0; a[m] = em[m]; cls[m] = 2
    for p in (V + "emit_lamps07.png", V + f"alarm_{G('alarm', F, 'idle')}07.png"):
        s = L(p); m = s[..., 3] > 0; over(a, s); cls[m] = 2
    r = robot or G("robot", F, "standby")
    ra, re = L(RF + f"{r}_a.png"), L(RF + f"{r}_e.png")
    over(a, ra); cls[ra[..., 3] > 0] = 1; over(a, re); cls[re[..., 3] > 0] = 3
    return a, cls, r
def cam(F):
    c = G("cam", F, [50, 5]); return (int(round(min(64, max(0, c[0])) * 5)), int(round(min(72, max(0, c[1])) * 5)))
def sample_wide(F, box):
    """native lit colours of world pixels in box (x0,y0,x1,y1 world) sampled at 5x block centres of the Godot frame"""
    w = np.array(Image.open(wide_path(F)).convert("RGB")).astype(np.float32); cx, cy = cam(F)
    x0, y0, x1, y1 = box; ys = np.arange(y0, y1) * 5 - cy + 2; xs = np.arange(x0, x1) * 5 - cx + 2
    ok = (ys[:, None] >= 0) & (ys[:, None] < 1080) & (xs[None] >= 0) & (xs[None] < 1920)
    out = w[np.clip(ys, 0, 1079)[:, None], np.clip(xs, 0, 1919)[None]]
    return out, ok
def fit(alb, wide, m):
    """per-channel least squares wide ~ a*alb + b over mask m"""
    P = []
    for ch in range(3):
        x = alb[..., ch][m].astype(np.float64); y = wide[..., ch][m]
        if len(x) < 8: P.append((1.0, 0.0)); continue
        A = np.stack([x, np.ones_like(x)], 1); (aa, bb), *_ = np.linalg.lstsq(A, y, rcond=None); P.append((max(0.05, aa), bb))
    return P
def grade_native(A, Cc, Wd, ok):
    """palette LUT: each (class, albedo colour) -> median of its sampled wide colours (fallback: per-class affine)"""
    Af = A[..., :3].astype(np.float32)
    fits = {}
    for k in (0, 1, 2, 3):
        m = ok & (Cc == k); fits[k] = fit(Af, Wd, m) if m.sum() > 30 else None
    if fits[0] is None: fits[0] = fit(Af, Wd, ok)
    if fits[3] is None: fits[3] = fits[2]
    for k in (1, 2, 3):
        if fits[k] is None: fits[k] = fits[0]
    out = np.zeros_like(Af)
    for k in (0, 1, 2, 3):
        for ch in range(3): out[..., ch] = np.where(Cc == k, fits[k][ch][0] * Af[..., ch] + fits[k][ch][1], out[..., ch])
    key = (Cc.astype(np.int64) << 24) | (A[..., 0].astype(np.int64) << 16) | (A[..., 1].astype(np.int64) << 8) | A[..., 2]
    for kv in np.unique(key[ok]):
        m = key == kv; mo = m & ok
        if mo.sum() >= 3: out[m] = np.median(Wd[mo], 0)
    return np.clip(out, 0, 255), fits
def render(F, reg, robot=None, band=0.07, pad=4, polish=None, sigma=2.0):
    """reg: Lua (x0,y0,x1,y1). -> (3W x 3H RGBA inset content, info)"""
    x0, y0, x1, y1 = reg[0] + OX, reg[1] + OY, reg[2] + OX, reg[3] + OY
    a, cls, r = compose(F, robot)
    bx = (x0 - pad, y0 - pad, x1 + pad, y1 + pad)
    A = a[bx[1]:bx[3], bx[0]:bx[2]]; Cc = cls[bx[1]:bx[3], bx[0]:bx[2]]
    Wd, ok = sample_wide(F, bx)
    Ag, fits = grade_native(A, Cc, Wd, ok)
    ratio = np.where(ok[..., None], (Wd + 6) / (Ag + 6), 1.0)          # per channel: warm/cool light pools keep their hue
    ratio = np.clip(np.stack([gaussian_filter(ratio[..., c], sigma) for c in range(3)], -1), 0.6, 1.8)
    G8 = np.concatenate([Ag.astype(np.uint8), A[..., 3:4]], -1)
    dk = (U.lum(A.astype(float)) < 48) & (A[..., 3] > 0)
    up, lines = U.up3s(G8, dk=dk, ret_mask=True)
    Cu = np.repeat(np.repeat(Cc, Z, 0), Z, 1)
    near = np.repeat(np.repeat(G8, Z, 0), Z, 1)
    up[Cu == 3] = near[Cu == 3]                     # robot lights (eyes, icons): designed shapes, block-exact
    up = detail(up, keep=lines | (Cu >= 2), grain=0.022)
    Ru = np.stack([zoom(ratio[..., c], Z, order=1)[:up.shape[0], :up.shape[1]] for c in range(3)], -1)
    Ru = 1.0 + np.round((Ru - 1.0) / band) * band
    out = up.astype(np.float32)
    out[..., :3] *= np.where((Cu >= 2)[..., None], 1.0, Ru); out[..., 3] = 255
    res = np.clip(out, 0, 255).astype(np.uint8)
    info = dict(lines=lines, F=F, robot=r, box=bx, pad=pad, fits=fits, cls=Cu, reg=reg, light=dict((k, G(k, F)) for k in ("sun", "beam", "day", "dusk", "night", "dawn", "lamps", "amb")))
    if polish: res = polish(res, info)
    p = pad * Z
    return res[p:-p, p:-p], info
def wide_crop(F, reg, s=3):
    """the matching region of the Godot wide frame (for side-by-side verification)"""
    w = Image.open(wide_path(F)); cx, cy = cam(F); x0, y0 = (reg[0] + OX) * 5 - cx, (reg[1] + OY) * 5 - cy
    W, H = (reg[2] - reg[0]), (reg[3] - reg[1])
    return w.crop((x0, y0, x0 + W * 5, y0 + H * 5)).resize((W * s * 5 // 5 * 5, H * s * 5 // 5 * 5), Image.NEAREST)
# ---------------- 1-px polish (all drawn at the inset grain)
from scipy.ndimage import label, binary_erosion, binary_dilation
def lighten(c, k): return tuple(int(min(255, v + (255 - v) * k)) for v in c)
def screen_mask(res, info):
    """robot face screen (the big dark area inside the head) at 3x"""
    C = info["cls"]; lum = 0.3 * res[..., 0] + 0.59 * res[..., 1] + 0.11 * res[..., 2]
    m = ((C == 1) | (C == 3)) & ((lum < 45) | (C == 3))
    lab, n = label(m)
    if n == 0: return None
    sizes = np.bincount(lab.ravel()); sizes[0] = 0; k = sizes.argmax()
    return lab == k if sizes[k] > 150 else None
def glass(res, info, tint=(120, 130, 190), warm=None):
    """glass glint on the robot screen: two short diagonal streaks top-left + a soft reflected band at the bottom"""
    m = screen_mask(res, info)
    if m is None: return res
    ys, xs = np.nonzero(m); y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    C = info["cls"]
    base = np.median(res[m & (C == 1)][:, :3], 0) if (m & (C == 1)).any() else np.array([30, 20, 30])
    hl = tuple(int(b + (t - b) * 0.55) for b, t in zip(base, tint)); hl2 = tuple(int(b + (t - b) * 0.3) for b, t in zip(base, tint))
    for (L, off, c) in ((7, 3, hl), (4, 7, hl2)):
        for d in range(L):
            y, x = y0 + off + d - 2, x0 + off + 6 - d + (L - 4)
            if 0 <= y < res.shape[0] and 0 <= x < res.shape[1] and m[y, x] and C[y, x] == 1: res[y, x, :3] = c
    by = y1 - 1                                                         # bottom rim reflection (one row, broken)
    wc = warm if warm else hl2
    for x in range(x0 + 4, x1 - 3):
        if m[by, x] and C[by, x] == 1 and (x - x0) % 7 < 5: res[by, x, :3] = wc
    return res
def eyes(res, info, glint=(255, 255, 255), catch=None):
    """a 1-px sparkle on each lit eye (top-left) and, at dusk, a warm catch-light pixel low right"""
    C = info["cls"]; m = C == 3
    lab, n = label(m)
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if len(ys) < 9 or len(ys) > 200: continue
        res[ys.min(), xs.min(), :3] = glint
        if len(ys) >= 18: res[ys.min() + 1, xs.min(), :3] = lighten(tuple(res[ys.min() + 1, xs.min(), :3]), 0.6)
        if catch is not None: res[ys.max(), xs.max(), :3] = catch
    return res
def rim(res, info, col, side=1, amt=0.55):
    """1-px rim light on the robot silhouette on one side (side=+1 right, -1 left)"""
    C = info["cls"]; rb = (C == 1) | (C == 3)
    sh = np.zeros_like(rb)
    if side > 0: sh[:, :-1] = rb[:, :-1] & ~rb[:, 1:]
    else: sh[:, 1:] = rb[:, 1:] & ~rb[:, :-1]
    # move one px inward (the outline stays), light the body pixel
    inner = np.zeros_like(sh)
    if side > 0: inner[:, :-1] = sh[:, 1:]
    else: inner[:, 1:] = sh[:, :-1]
    tgt = inner & rb & (C == 1)
    lum = 0.3 * res[..., 0] + 0.59 * res[..., 1] + 0.11 * res[..., 2]
    tgt &= lum > 60
    res[tgt, :3] = (res[tgt, :3] * (1 - amt) + np.array(col) * amt).astype(np.uint8)
    return res
# ---------------- Stardew-ish wood frame
WD = dict(o=(46, 20, 16), d=(92, 46, 26), m=(142, 80, 42), l=(190, 120, 64), h=(226, 164, 96), br=(236, 200, 110), brd=(150, 104, 40))
def frame(content, t=1.0):
    """content HxW RGBA -> framed RGBA (H+14)x(W+14) incl. 2px drop shadow. t in [0,1] opening scale."""
    H, W = content.shape[:2]; B = 6; FH, FW = H + 2 * B, W + 2 * B
    out = np.zeros((FH + 2, FW + 2, 4), np.uint8)
    h = max(2 * B + 2, int(round(FH * t))); w = max(2 * B + 2, int(round(FW * t)))
    oy, ox = (FH - h) // 2, (FW - w) // 2
    def rect(y0, x0, y1, x1, c): out[y0:y1, x0:x1, :3] = c; out[y0:y1, x0:x1, 3] = 255
    rect(oy + 2, ox + 2, oy + h + 2, ox + w + 2, (30, 12, 14))                       # drop shadow
    out[oy + 2:oy + h + 2, ox + 2:ox + w + 2, 3] = 150
    rect(oy, ox, oy + h, ox + w, WD["o"])
    rect(oy + 1, ox + 1, oy + h - 1, ox + w - 1, WD["h"])                             # top/left light bevel
    rect(oy + 2, ox + 2, oy + h - 1, ox + w - 1, WD["d"])                             # bottom/right dark bevel
    rect(oy + 2, ox + 2, oy + h - 2, ox + w - 2, WD["m"])
    rect(oy + 2, ox + 2, oy + 3, ox + w - 2, WD["l"]); rect(oy + 2, ox + 2, oy + h - 2, ox + 3, WD["l"])
    # wood grain streaks on the face of the frame
    rng = np.random.RandomState(4)
    for k in range(int((w + h) * 0.25)):
        if rng.rand() < 0.5: y = oy + 3 + rng.randint(0, 2); x = ox + 4 + rng.randint(0, max(1, w - 12))
        else: y = oy + h - 4 - rng.randint(0, 2); x = ox + 4 + rng.randint(0, max(1, w - 12))
        out[y, x:x + rng.randint(2, 5), :3] = WD["d"]
    rect(oy + B - 1, ox + B - 1, oy + h - B + 1, ox + w - B + 1, WD["o"])            # inner dark line
    ih, iw = h - 2 * B, w - 2 * B
    if ih > 0 and iw > 0:
        cy, cx = (H - ih) // 2, (W - iw) // 2
        out[oy + B:oy + B + ih, ox + B:ox + B + iw] = content[cy:cy + ih, cx:cx + iw]
    for (yy, xx) in ((oy + 2, ox + 2), (oy + 2, ox + w - 4), (oy + h - 4, ox + 2), (oy + h - 4, ox + w - 4)):   # brass rivets
        out[yy:yy + 2, xx:xx + 2, :3] = WD["br"]; out[yy + 1, xx + 1, :3] = WD["brd"]
    return out
