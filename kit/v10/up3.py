"""3x pixel-art upscaler that keeps ONE pixel grain: Scale3x (AdvMAME3x) for shapes, and thin 1-px dark lines
(outlines / seams) re-drawn 1 px wide through the centre of each 3x3 block instead of becoming 3 px thick."""
import numpy as np
def pack(a):   # RGBA uint8 -> uint32
    a = a.astype(np.uint32); return (a[..., 0] << 24) | (a[..., 1] << 16) | (a[..., 2] << 8) | a[..., 3]
def unpack(p):
    return np.stack([(p >> 24) & 255, (p >> 16) & 255, (p >> 8) & 255, p & 255], -1).astype(np.uint8)
def scale3x(p):
    P = np.pad(p, 1, mode='edge')
    A, B, C = P[:-2, :-2], P[:-2, 1:-1], P[:-2, 2:]
    D, E, F = P[1:-1, :-2], P[1:-1, 1:-1], P[1:-1, 2:]
    G, H, I = P[2:, :-2], P[2:, 1:-1], P[2:, 2:]
    c1 = (D == B) & (D != H) & (B != F); c2 = (B == F) & (B != D) & (F != H)
    c3 = (D == H) & (D != B) & (H != F); c4 = (H == F) & (D != H) & (B != F)
    out = np.zeros((p.shape[0] * 3, p.shape[1] * 3), np.uint32)
    E0 = np.where(c1, D, E); E1 = np.where((c1 & (E != C)) | (c2 & (E != A)), B, E); E2 = np.where(c2, F, E)
    E3 = np.where((c1 & (E != G)) | (c3 & (E != A)), D, E); E5 = np.where((c2 & (E != I)) | (c4 & (E != C)), F, E)
    E6 = np.where(c3, D, E); E7 = np.where((c3 & (E != I)) | (c4 & (E != G)), H, E); E8 = np.where(c4, F, E)
    for (i, j), M in {(0, 0): E0, (0, 1): E1, (0, 2): E2, (1, 0): E3, (1, 1): E, (1, 2): E5, (2, 0): E6, (2, 1): E7, (2, 2): E8}.items():
        out[i::3, j::3] = M
    return out
def lum(a): return 0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]
def up3(rgba, dark_thr=52):
    """rgba: HxWx4 uint8 -> 3H x 3W x 4"""
    p = pack(rgba); out = scale3x(p)
    dk = (lum(rgba.astype(float)) < dark_thr) & (rgba[..., 3] > 0)
    Dp = np.pad(dk, 1); nb4 = Dp[:-2, 1:-1].astype(int) + Dp[2:, 1:-1] + Dp[1:-1, :-2] + Dp[1:-1, 2:]
    nondark_nb = (~Dp[:-2, 1:-1]) | (~Dp[2:, 1:-1]) | (~Dp[1:-1, :-2]) | (~Dp[1:-1, 2:])
    line = dk & (nb4 <= 2) & nondark_nb
    Pp = np.pad(p, 1, mode='edge'); Dk = np.pad(dk, 1)
    H, W = dk.shape
    ys, xs = np.nonzero(line)
    for y, x in zip(ys, xs):
        c = p[y, x]
        nb = {(dy, dx): (bool(Dk[y + 1 + dy, x + 1 + dx]), Pp[y + 1 + dy, x + 1 + dx]) for dy in (-1, 0, 1) for dx in (-1, 0, 1)}
        def fill(dy, dx):
            # colour for a sub-pixel pushed toward (dy, dx): that neighbour if not dark, else any non-dark 4-neighbour
            for q in ((dy, dx), (dy, 0), (0, dx), (-dy, 0), (0, -dx), (1, 0), (-1, 0), (0, 1), (0, -1)):
                if q != (0, 0) and not nb[q][0]: return nb[q][1]
            return c
        for i in range(3):
            for j in range(3):
                dy, dx = i - 1, j - 1
                keep = (dy == 0 and dx == 0) or nb[(dy, dx)][0] and (dy == 0 or dx == 0 or (not nb[(dy, 0)][0] and not nb[(0, dx)][0]))
                out[y * 3 + i, x * 3 + j] = c if keep else fill(dy, dx)
    return unpack(out)
def up3s(rgba, dark_thr=48, dk=None, ret_mask=False):
    """v10 final: Scale3x shapes; thin dark lines (1-px strokes in the native art) are skeletonised to a clean 1-px
    medial line at 3x and the freed pixels take the nearest non-line colour (so corners/diagonals stay tidy)."""
    from scipy.ndimage import binary_opening, distance_transform_edt
    from skimage.morphology import skeletonize
    p = pack(rgba); out = scale3x(p)
    if dk is None: dk = (lum(rgba.astype(float)) < dark_thr) & (rgba[..., 3] > 0)
    thin = dk & ~binary_opening(dk, np.ones((2, 2), bool))
    m3 = scale3x(thin.astype(np.uint32)) > 0
    sk = skeletonize(m3)
    _, (iy, ix) = distance_transform_edt(m3, return_indices=True)
    fill = out[iy, ix]
    res = np.where(m3 & ~sk, fill, out)
    if ret_mask:
        dk3 = np.repeat(np.repeat(dk & ~thin, 3, 0), 3, 1)
        return unpack(res), sk | (dk3 & ~m3)
    return unpack(res)
