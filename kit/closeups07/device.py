"""Close-up insert 2: the reminder device ringing; the mitten hovers, winds back, presses the button, the alarm stops.
Native 384x216 drawing at the wide shot's pixel size."""
import os, numpy as np
from px import *
OUT = os.path.dirname(os.path.abspath(__file__)) + "/device/"; os.makedirs(OUT, exist_ok=True)
N = 64
DIG = {"1": ["01", "11", "01", "01", "01", "01", "11"], "3": ["111", "001", "001", "011", "001", "001", "111"]}
def digit(cv, d, x0, y0, s, c):
    for r, row in enumerate(DIG[d]):
        for q, ch in enumerate(row):
            if ch == "1": cv.put((xx >= x0 + q * s) & (xx < x0 + (q + 1) * s) & (yy >= y0 + r * s) & (yy < y0 + (r + 1) * s), c)
def background(cv):
    cv.put(yy < 182, "#6e3c24"); cv.put((yy < 182) & (xx % 28 == 0), "#4a2416"); cv.put((yy < 182) & (xx % 28 == 1), "#86502e")
    for x0 in range(0, 384, 28):                             # wood grain flecks
        for k in range(6):
            y = (x0 * 7 + k * 31) % 170; cv.put((xx >= x0 + 6 + k * 3) & (xx <= x0 + 10 + k * 3) & (yy == y), "#643520")
    beam = ((xx - 400) + yy * 0.7 > -200) & ((xx - 400) + yy * 0.7 < -40) & (yy < 182)
    cv.put(beam, "#8a5230"); cv.put(beam & (xx % 28 == 0), "#5e3020"); cv.put(beam & (xx % 28 == 1), "#a4663a")
    ed = beam & ~shift(beam, 2, 0) & checker(); cv.put(ed, "#7a4628")
    # ledge / wainscot cap
    cv.put((yy >= 178) & (yy < 184), "#a0603a"); cv.put(yy == 178, "#c47e4a"); cv.put((yy >= 184) & (yy < 196), "#5a2e1c"); cv.put(yy >= 196, "#2e160e")
    cv.put((yy >= 196) & (yy < 199), "#3e2014")
    # calendar at the left edge
    cal = rrect(-10, 60, 64, 172, 3)
    cv.put(edge(cal), "#3e2833"); cv.put(cal, "#f3eada"); cv.put(cal & (xx >= 58), "#d8cab4"); cv.put(cal & (yy < 80), "#c0303a"); cv.put(cal & (yy == 60), "#e05a50")
    for rx in (10, 40): cv.put(rrect(rx, 54, rx + 4, 66, 1), "#2a1e28")
    digit(cv, "1", 8, 96, 6, "#c0303a"); digit(cv, "3", 26, 96, 6, "#c0303a")
    cv.put(cal & (yy >= 146) & (yy <= 147) & (xx >= 8) & (xx <= 50), "#d8cab4"); cv.put(cal & (yy >= 154) & (yy <= 155) & (xx >= 8) & (xx <= 40), "#d8cab4")
    sh = shift(cal, 4, 3) & ~cal & (yy < 178); cv.put(sh, "#4a2416")
    return beam
def device(cv, dx, bdx, state, t, btn_out, beam):
    X = lambda v: v + dx
    body = rrect(X(118), 80, X(262), 178, 14)
    sh = shift(body, -6, 0) & ~body & (yy < 178); cv.put(sh, "#4a2416")
    cv.put(edge(body), "#3e2833"); cv.put(body, "#ede0c8")
    cv.put(body & (yy <= 84), "#fff8ea"); cv.put(body & (xx <= X(126)), "#d4c2a6"); cv.put(body & (yy >= 170), "#c4ae90"); cv.put(body & (xx <= X(121)) & (yy >= 170), "#a8927a")
    cv.put(body & (xx >= X(256)), "#fff2dc"); cv.put(body & (xx >= X(259)), "#ffe0b0")
    cv.put(body & beam & (xx > X(126)) & (yy > 84) & (yy < 170), "#fbecd4")
    for i in range(5):                                       # speaker dots
        m = rrect(X(150 + i * 18), 158, X(156 + i * 18), 162, 1); cv.put(m, "#b8a284"); cv.put(m & (yy == 158), "#8e7a64")
    # screen
    bez = rrect(X(138), 96, X(242), 148, 7); cv.put(bez, "#2a1e28"); cv.put(bez & (yy >= 146), "#fff2de")
    gl = rrect(X(142), 100, X(238), 144, 5)
    if state == "ring":
        on = (t // 3) % 2 == 0
        cv.put(gl, "#d0484a" if on else "#a8323e"); cv.put(gl & (yy <= 106), "#ff7a68" if on else "#c8484a")
        # bell icon
        icon = (ell(X(190), 121, 10, 10) & (yy <= 124)) | rrect(X(178), 122, X(202), 128, 1)
        cv.put(icon, "#fff4e8" if on else "#ffc8b0"); cv.put(ell(X(190), 131, 3, 2), "#fff4e8" if on else "#ffc8b0")
        cv.put(rrect(X(188), 107, X(192), 110, 1), "#fff4e8" if on else "#ffc8b0")
    elif state == "off":
        cv.put(gl, "#15101f"); cv.put(gl & (yy <= 104), "#1d1c34")
        pts = [(170, 122), (175, 127), (180, 132), (190, 122), (200, 112), (208, 104)]
        n = min(len(pts) - 1, max(0, (t - 28) // 2 + 1)) if t >= 28 else 0
        for (a, b) in zip(pts[:n], pts[1:n + 1]):
            m = thick_line(X(a[0]), a[1], X(b[0]), b[1], 5); cv.put(edge(m) & gl, "#1e4a2c"); cv.put(m & gl, "#6ad06a")
        if n >= 5: cv.put(thick_line(X(172), 121, X(179), 128, 1) & gl, "#b0ffa0")
    # glass glint
    for (x, y) in line_pts(X(146), 112, X(154), 104): cv.px(x, y, "#ffffff" if state == "ring" else "#57609a")
    # bell dome (shakes a little more than the body)
    B = lambda v: v + dx + bdx
    dome = ell(B(190), 80, 38, 34) & (yy <= 80)
    cv.put(edge(dome) & (yy < 81), "#3a0c14"); cv.put(dome, "#c0303a")
    cv.put(dome & ell(B(176), 60, 16, 12), "#e0504a"); cv.put(dome & ell(B(172), 56, 7, 5), "#ff8a78"); cv.put(ell(B(170), 54, 2, 1), "#ffd0c0")
    cv.put(dome & ~ell(B(186), 76, 36, 32), "#801c28")
    cv.put(dome & beam & ~ell(B(186), 76, 36, 32), "#e8604a")
    stem = rrect(B(187), 38, B(193), 47, 1); cv.put(edge(stem), "#3a0c14"); cv.put(stem, "#6a1e24"); cv.put(stem & (xx >= B(191)), "#a03a3a")
    kn = ell(B(190), 36, 6, 4); cv.put(edge(kn), "#3a0c14"); cv.put(kn, "#c0303a"); cv.put(ell(B(188), 34, 2, 1), "#ff8a78")
    rimb = rrect(B(150), 78, B(230), 83, 2); cv.put(edge(rimb) & ~body, "#3a0c14"); cv.put(rimb, "#a02830"); cv.put(rimb & (yy == 78), "#e0504a")
    # side button (sticks out of the right side; btn_out = how far it protrudes)
    hs = rrect(X(260), 114, X(265), 138, 2); cv.put(edge(hs) & ~body, "#3e2833"); cv.put(hs, "#b8a284")
    bt = rrect(X(262), 117, X(263 + btn_out), 135, 3)
    cv.put(edge(bt) & ~hs, "#3a0c14"); cv.put(bt, "#d0403a"); cv.put(bt & (yy <= 119), "#ff7a60"); cv.put(bt & (yy >= 132), "#8a2020")
    cv.put(bt & (xx == X(263 + btn_out)) & (yy > 119) & (yy < 132), "#e85a4a")
def ring_lines(cv, t, dx):
    if (t // 3) % 2: return
    for (a, b) in (((140, 50), (132, 44)), ((136, 64), (126, 62)), ((146, 38), (141, 30)), ((240, 50), (248, 44)), ((244, 64), (254, 62)), ((234, 38), (239, 30))):
        for (x, y) in line_pts(a[0] + dx, a[1], b[0] + dx, b[1]): cv.put(ell(x, y, 0.8, 0.8), "#ffe6a0")
def mitten(cv, x, y, squash=0):
    # arm from off-screen lower right to the wrist
    wx, wy = x + 26, y + 14
    arm = thick_line(wx, wy, 410, 236, 13)
    cv.put(edge(arm), "#46181a"); cv.put(arm, "#f7a47e")
    cv.put(arm & ~shift(arm, 0, 3), "#d8704f"); cv.put(arm & ~shift(arm, 0, -2), "#ffc49a")
    cuff = ell(wx, wy, 7, 8); cv.put(edge(cuff), "#46181a"); cv.put(cuff, "#e8936c"); cv.put(cuff & (yy <= wy - 5), "#ffc49a")
    m = rrect(x + squash, y, x + 27, y + 24, 9)
    th = rrect(x + 8, y - 6, x + 17, y + 3, 4)
    mm = m | th
    cv.put(edge(mm), "#3e2833"); cv.put(mm, "#fbf4e8"); cv.put(mm & (yy <= y + 3) & ~th, "#fffdf6"); cv.put(th & (yy <= y - 3), "#fffdf6")
    cv.put(mm & (yy >= y + 18), "#d8cab4"); cv.put(mm & (xx <= x + squash + 3) & (yy > y + 4), "#e6dac6")
    cv.put(edge(th) & m, "#c8b8a2")
    cv.put(mm & (xx >= x + 22) & (yy > y + 4), "#ffe8c8")
def flash(cv, x, y, t):
    r = [5, 8, 10][t]
    for (ddx, ddy) in ((-1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1)):
        for k in range(r - 3, r + 1): cv.px(x + ddx * k, y + ddy * k, "#fffbe8" if t < 2 else "#ffe6a0")
def ease(a, b, u): u = min(1.0, max(0.0, u)); u = u * u * (3 - 2 * u); return round(a + (b - a) * u)
def frame(t):
    cv = Cv(); beam = background(cv)
    ringing = t < 23
    dx = ((t // 2) % 2) * 2 - 1 if ringing else ((1 if t in (23, 25) else (-1 if t == 24 else 0)))
    bdx = 2 * dx if ringing else 0
    if t < 14: mx = 290 + (1 if t % 6 == 3 else 0); my = 112
    elif t < 22: mx = ease(290, 298, (t - 14) / 7); my = ease(112, 110, (t - 14) / 7)   # anticipation: wind back
    elif t == 22: mx, my = 283, 113
    elif t == 23: mx, my = 275, 114                                                        # contact
    elif t < 27: mx, my = [270, 268, 267][t - 24], 114                                    # push in
    else: mx, my = 267, 114 if t < 50 else 115
    btn_out = 11 if t < 23 else (max(3, 11 - (275 - mx) * 1 - 3) if t < 27 else 3)
    if t >= 23: btn_out = min(btn_out, mx - 264)
    state = "ring" if ringing else "off"
    device(cv, dx, bdx, state, t, btn_out, beam)
    if ringing: ring_lines(cv, t, dx)
    mitten(cv, mx, my, squash=2 if t == 23 else (1 if t == 24 else 0))
    if 23 <= t < 26: flash(cv, mx - 2, 126, t - 23)
    return cv
if __name__ == "__main__":
    for t in range(N): frame(t).save(OUT + f"f{t:03d}.png")
    print("device frames", N)
