"""v08 calendar close-up for the time pass: night -> dawn; page 12 lifts, curls, tears off and flies away, revealing 13.
Drawn natively at 384x216, then graded per frame (moonlit blue -> dawn pink -> morning)."""
import os, numpy as np
from px import *
from device8 import digit
HERE = os.path.dirname(os.path.abspath(__file__)); os.makedirs(HERE + "/cal", exist_ok=True)
N = 64
X0, X1, Y0, Y1 = 132, 252, 34, 192
def wall(cv):
    cv.put(yy < 60, "#3c4a50"); cv.put((yy < 60) & (xx % 12 == 5), "#445258"); cv.put((yy < 60) & (xx % 12 == 11) & (yy % 14 == 6), "#56666c")
    cv.put((yy >= 60) & (yy < 66), "#7a4428"); cv.put(yy == 60, "#a0603a"); cv.put(yy == 65, "#3a1c10")
    cv.put(yy >= 66, "#6e3c24"); cv.put((yy >= 66) & (xx % 28 == 0), "#4a2416"); cv.put((yy >= 66) & (xx % 28 == 1), "#86502e")
    cv.put(yy >= 204, "#5a2e1c"); cv.put(yy == 204, "#a0603a")
def page(cv, num, y_bot=Y1, shade=False):
    m = rrect(X0, Y0 + 30, X1, y_bot, 3)
    cv.put(m, "#f3eada"); cv.put(m & (xx >= X1 - 6), "#dccfb8"); cv.put(m & (yy >= y_bot - 3), "#d8cab4")
    if y_bot > Y0 + 118:
        digit(cv, num[0], X0 + 22, Y0 + 58, 10, "#c0303a"); digit(cv, num[1], X0 + 52, Y0 + 58, 10, "#c0303a")
        for k in range(3): cv.put(m & (yy == Y0 + 140 + k * 6) & (xx >= X0 + 14) & (xx <= X1 - 20 - k * 14), "#d8cab4")
    return m
def frame(t):
    cv = Cv(); wall(cv)
    full = rrect(X0, Y0, X1, Y1, 4)
    cv.put(shift(full, 5, 4) & ~full, "#3a1c12")
    cv.put(edge(full), "#3e2833")
    page(cv, "13")
    # the old page (12) peels: bottom rises with a curl, then it tears off and flies up-right
    if t < 22: pb = Y1
    elif t < 30: pb = round(Y1 - (Y1 - 96) * ((t - 22) / 8) ** 1.4)
    else: pb = None
    if pb is not None:
        cv.put(rrect(X0, pb, X1, min(Y1, pb + 6), 2) & (yy > pb), "#b8a88e") if pb < Y1 else None      # its shadow on the new page
        tmp = Cv(); tmp.a = cv.a.copy(); pm = page(tmp, "12", Y1)
        keep = pm & (yy < pb); cv.a[keep] = tmp.a[keep]
        if pb < Y1: cv.put(pm & (yy >= pb - 3) & (yy < pb), "#d8cab4")
        if pb < Y1:                                                     # curl: the underside rolls up
            curl = rrect(X0 + 2, pb - 10, X1 - 2, pb, 5)
            cv.put(edge(curl), "#8e7a64"); cv.put(curl, "#e6dccb"); cv.put(curl & (yy <= pb - 7), "#fffaf0"); cv.put(curl & (yy >= pb - 2), "#c8b8a2")
    elif t < 42:                                                          # torn page flutters away
        u = (t - 30) / 12.0; cx = round(192 + 190 * u); cy = round(96 - 150 * u + 30 * np.sin(u * 6))
        w, h = round(56 - 20 * u), round(40 - 10 * u); sk = round(14 * np.sin(u * 9))
        m = ((yy >= cy - h // 2) & (yy <= cy + h // 2)) & ((xx - cx - (yy - cy) * sk / max(1, h)) ** 2 <= (w / 2) ** 2)
        cv.put(edge(m), "#8e7a64"); cv.put(m, "#f3eada" if (t // 2) % 2 else "#dccfb8"); cv.put(m & (yy <= cy - h // 2 + 6), "#c0303a")
    # header (binding) over the pages
    hd = rrect(X0, Y0, X1, Y0 + 30, 4)
    cv.put(hd, "#c0303a"); cv.put(hd & (yy <= Y0 + 2), "#e05a50"); cv.put(hd & (yy >= Y0 + 27), "#8a1c24")
    for rx in (X0 + 22, X1 - 30):
        r = rrect(rx, Y0 - 8, rx + 7, Y0 + 10, 3); cv.put(edge(r), "#1a1018"); cv.put(r, "#3a2a36"); cv.put(r & (xx == rx + 1), "#6a5a66")
    # ---- grade: moonlit night -> dawn -> morning; plus a window-light patch that grows from the right with dawn
    a = cv.a.astype(np.float32)
    d = min(1.0, max(0.0, (t - 18) / 30.0)); d = d * d * (3 - 2 * d)
    night = np.array([0.30, 0.36, 0.62]); dawn = np.array([0.97, 0.86, 0.80])
    g = night * (1 - d) + dawn * d
    patch = ((xx - 470) + yy * 0.5 > -300) & ((xx - 470) + yy * 0.5 < -80)
    a *= g
    if d > 0: a[patch] *= 1.0 + 0.16 * d
    # moonlight rim at night
    cv.a = np.clip(a, 0, 255).astype(np.uint8)
    return cv
if __name__ == "__main__":
    for t in range(N): frame(t).save(f"{HERE}/cal/f{t:03d}.png")
    print("cal", N)
