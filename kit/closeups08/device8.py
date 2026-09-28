"""v08 device close-ups, drawn natively at 384x216 (same pixel size as the wide shot).
 task : day-1 cue. The reminder beeps and flashes (gold bell, broom icon); the robot's head at the right edge boots and snaps up.
 press: the alarm rings. HIS mitten on HIS salmon arm (from his shoulder, his head and squinting eye at the right edge) hovers,
        winds back, presses the button, and the alarm stops (green check)."""
import os, sys, numpy as np
from px import *
HERE = os.path.dirname(os.path.abspath(__file__))
DIG = {"1": ["01", "11", "01", "01", "01", "01", "11"], "3": ["111", "001", "001", "011", "001", "001", "111"], "2": ["111", "001", "001", "111", "100", "100", "111"]}
def digit(cv, d, x0, y0, s, c):
    for r, row in enumerate(DIG[d]):
        for q, ch in enumerate(row):
            if ch == "1": cv.put((xx >= x0 + q * s) & (xx < x0 + (q + 1) * s) & (yy >= y0 + r * s) & (yy < y0 + (r + 1) * s), c)
def background(cv, ox, light, cal="13"):
    cv.put(yy < 182, "#6e3c24"); cv.put((yy < 182) & ((xx - ox) % 28 == 0), "#4a2416"); cv.put((yy < 182) & ((xx - ox) % 28 == 1), "#86502e")
    for x0 in range(-56, 440, 28):
        for k in range(6):
            y = ((x0 + 56) * 7 + k * 31) % 170; cv.put((xx >= x0 + ox + 6 + k * 3) & (xx <= x0 + ox + 10 + k * 3) & (yy == y), "#643520")
    if light == "dusk":
        beam = ((xx - 400) + yy * 0.7 > -200) & ((xx - 400) + yy * 0.7 < -40) & (yy < 182)
        cv.put(beam, "#8a5230"); cv.put(beam & ((xx - ox) % 28 == 0), "#5e3020"); cv.put(beam & ((xx - ox) % 28 == 1), "#a4663a")
        cv.put(beam & ~shift(beam, 2, 0) & checker(), "#7a4628")
    else:                                                   # soft, cool morning light from the window (upper right)
        beam = ((xx - 470) + yy * 0.45 > -260) & ((xx - 470) + yy * 0.45 < -60) & (yy < 182)
        cv.put(beam, "#7c4a30"); cv.put(beam & ((xx - ox) % 28 == 0), "#58301f"); cv.put(beam & ((xx - ox) % 28 == 1), "#946040")
        cv.put(beam & ~shift(beam, 2, 0) & checker(), "#744228")
    cv.put((yy >= 178) & (yy < 184), "#a0603a"); cv.put(yy == 178, "#c47e4a"); cv.put((yy >= 184) & (yy < 196), "#5a2e1c"); cv.put(yy >= 196, "#2e160e")
    cv.put((yy >= 196) & (yy < 199), "#3e2014")
    calm = rrect(-10 + ox, 60, 64 + ox, 172, 3)
    if calm.any():
        cv.put(edge(calm), "#3e2833"); cv.put(calm, "#f3eada"); cv.put(calm & (xx >= 58 + ox), "#d8cab4"); cv.put(calm & (yy < 80), "#c0303a"); cv.put(calm & (yy == 60), "#e05a50")
        for rx in (10, 40): cv.put(rrect(rx + ox, 54, rx + 4 + ox, 66, 1), "#2a1e28")
        digit(cv, cal[0], 8 + ox, 96, 6, "#c0303a"); digit(cv, cal[1], 26 + ox, 96, 6, "#c0303a")
        cv.put(calm & (yy >= 146) & (yy <= 147) & (xx >= 8 + ox) & (xx <= 50 + ox), "#d8cab4")
        cv.put(shift(calm, 4, 3) & ~calm & (yy < 178), "#4a2416")
    return beam
BELL = {"red": ("#c0303a", "#e0504a", "#ff8a78", "#801c28", "#3a0c14", "#a02830"),
        "gold": ("#e0a830", "#f8cc50", "#fff0a0", "#a06818", "#402408", "#c08820"),
        "dull": ("#a02c36", "#b8404a", "#d86a64", "#6a1822", "#3a0c14", "#8a2630")}
def device(cv, ox, dx, bdx, state, t, btn_out, beam, on=True):
    X = lambda v: v + dx + ox
    body = rrect(X(118), 80, X(262), 178, 14)
    cv.put(shift(body, -6, 0) & ~body & (yy < 178), "#4a2416")
    cv.put(edge(body), "#3e2833"); cv.put(body, "#ede0c8")
    cv.put(body & (yy <= 84), "#fff8ea"); cv.put(body & (xx <= X(126)), "#d4c2a6"); cv.put(body & (yy >= 170), "#c4ae90"); cv.put(body & (xx <= X(121)) & (yy >= 170), "#a8927a")
    cv.put(body & (xx >= X(256)), "#fff2dc"); cv.put(body & (xx >= X(259)), "#ffe0b0")
    cv.put(body & beam & (xx > X(126)) & (yy > 84) & (yy < 170), "#fbecd4")
    for i in range(5):
        m = rrect(X(150 + i * 18), 158, X(156 + i * 18), 162, 1); cv.put(m, "#b8a284"); cv.put(m & (yy == 158), "#8e7a64")
    bez = rrect(X(138), 96, X(242), 148, 7); cv.put(bez, "#2a1e28"); cv.put(bez & (yy >= 146), "#fff2de")
    gl = rrect(X(142), 100, X(238), 144, 5)
    if state == "ring":
        blink = (t // 3) % 2 == 0
        cv.put(gl, "#d0484a" if blink else "#a8323e"); cv.put(gl & (yy <= 106), "#ff7a68" if blink else "#c8484a")
        icon = (ell(X(190), 121, 10, 10) & (yy <= 124)) | rrect(X(178), 122, X(202), 128, 1)
        cv.put(icon, "#fff4e8" if blink else "#ffc8b0"); cv.put(ell(X(190), 131, 3, 2), "#fff4e8" if blink else "#ffc8b0")
        cv.put(rrect(X(188), 107, X(192), 110, 1), "#fff4e8" if blink else "#ffc8b0")
    elif state == "off":
        cv.put(gl, "#15101f"); cv.put(gl & (yy <= 104), "#1d1c34")
        pts = [(170, 122), (175, 127), (180, 132), (190, 122), (200, 112), (208, 104)]
        n = min(len(pts) - 1, max(0, (t - 28) // 2 + 1)) if t >= 28 else 0
        for (a, b) in zip(pts[:n], pts[1:n + 1]):
            m = thick_line(X(a[0]), a[1], X(b[0]), b[1], 5); cv.put(edge(m) & gl, "#1e4a2c"); cv.put(m & gl, "#6ad06a")
    elif state in ("task", "idle"):
        lit = state == "task" and on
        cv.put(gl, "#2e8a86" if lit else "#1c4a4c"); cv.put(gl & (yy <= 106), "#5ec8b8" if lit else "#24585a")
        if state == "task":                                    # broom icon
            c1, c2 = ("#fff4c0", "#f0c040") if lit else ("#6aa89a", "#4a8a80")
            for (x, y) in line_pts(X(176), 106, X(200), 128): cv.put(ell(x, y, 1, 1), c1)
            br = np.zeros_like(xx, bool)
            for k in range(8): br |= (yy == 129 + k) & (xx >= X(194 - k // 2)) & (xx <= X(210 + k // 3))
            cv.put(br, c2); cv.put(br & ((xx - X(0)) % 3 == 0), "#c89020" if lit else "#3a7068")
        else:
            cv.put(rrect(X(170), 118, X(210), 124, 2), "#2e6a6a")
    for (x, y) in line_pts(X(146), 112, X(154), 104): cv.px(x, y, "#ffffff" if state == "ring" or (state == "task" and on) else "#57609a")
    B = lambda v: v + dx + bdx + ox
    kind = "red" if state in ("ring", "off") else ("gold" if state == "task" and on else "dull")
    c0, c1, c2, c3, co, cr = BELL[kind]
    if kind == "gold":                                         # glow halo around the lit bell
        halo = ell(B(190), 70, 52, 42) & ~ell(B(190), 80, 38, 34) & (yy < 80) & checker(t % 2)
        cv.put(halo, "#b87838")
    dome = ell(B(190), 80, 38, 34) & (yy <= 80)
    cv.put(edge(dome) & (yy < 81), co); cv.put(dome, c0)
    cv.put(dome & ell(B(176), 60, 16, 12), c1); cv.put(dome & ell(B(172), 56, 7, 5), c2); cv.put(ell(B(170), 54, 2, 1), "#fff4e0")
    cv.put(dome & ~ell(B(186), 76, 36, 32), c3)
    stem = rrect(B(187), 38, B(193), 47, 1); cv.put(edge(stem), co); cv.put(stem, c3); cv.put(stem & (xx >= B(191)), c1)
    kn = ell(B(190), 36, 6, 4); cv.put(edge(kn), co); cv.put(kn, c0); cv.put(ell(B(188), 34, 2, 1), c2)
    rimb = rrect(B(150), 78, B(230), 83, 2); cv.put(edge(rimb) & ~body, co); cv.put(rimb, cr); cv.put(rimb & (yy == 78), c1)
    hs = rrect(X(260), 114, X(265), 138, 2); cv.put(edge(hs) & ~body, "#3e2833"); cv.put(hs, "#b8a284")
    bt = rrect(X(262), 117, X(263 + btn_out), 135, 3)
    cv.put(edge(bt) & ~hs, "#3a0c14"); cv.put(bt, "#d0403a"); cv.put(bt & (yy <= 119), "#ff7a60"); cv.put(bt & (yy >= 132), "#8a2020")
    cv.put(bt & (xx == X(263 + btn_out)) & (yy > 119) & (yy < 132), "#e85a4a")
def sound_lines(cv, t, cx, col="#ffe6a0", period=3):
    if (t // period) % 2: return
    for (a, b) in (((-50, -30), (-58, -36)), ((-54, -16), (-64, -18)), ((-44, -42), (-49, -50)), ((50, -30), (58, -36)), ((54, -16), (64, -18)), ((44, -42), (49, -50))):
        for (x, y) in line_pts(cx + a[0], 80 + a[1], cx + b[0], 80 + b[1]): cv.put(ell(x, y, 0.8, 0.8), col)
# ---------------- the robot at 7x (his real palette: cream shell, navy screen, salmon body/arms, white mittens)
S7 = 7
def head(cv, x0, y0, face, eye, ex=0, ey=0, bulb=True, light="dusk"):
    s = S7; W_, H_ = 19 * s, 14 * s
    hd = rrect(x0, y0, x0 + W_ - 1, y0 + H_ - 1, 2 * s)
    # antenna
    ax = x0 + 9 * s
    st = (xx >= ax + 2) & (xx <= ax + 5) & (yy >= y0 - 3 * s) & (yy < y0)
    cv.put(edge(st), "#40240e"); cv.put(st, "#f0a830"); cv.put(st & (xx >= ax + 4), "#ffd24a")
    bl = rrect(ax - 2, y0 - 5 * s, ax + 2 * s - 3, y0 - 3 * s - 1, 4)
    cv.put(edge(bl), "#6a3a2a"); cv.put(bl, "#fc773a" if bulb else "#6a3a2a")
    if bulb: cv.put(bl & (yy <= y0 - 5 * s + 3) & (xx <= ax + 3), "#fed6b2")
    cv.put(edge(hd), "#3e2833"); cv.put(hd, "#f3eada")
    cv.put(hd & (yy < y0 + s), "#fffdf2"); cv.put(hd & (xx < x0 + s) & (yy < y0 + 11 * s), "#fffdf2")
    cv.put(hd & (yy >= y0 + 12 * s), "#d8cab4"); cv.put(hd & (yy >= y0 + 13 * s), "#a8927a")
    if face == "front": cv.put(hd & (xx >= x0 + 17 * s), "#d8cab4")
    if light == "dusk": cv.put(hd & ~shift(hd, 3, 0) & (xx < x0 + 4 * s), "#ffe0b0")
    sx, sw = (x0 + 3 * s, 13) if face == "front" else (x0 + 2 * s, 11)
    scr = rrect(sx, y0 + 3 * s, sx + sw * s - 1, y0 + 11 * s - 1, s)
    cv.put(edge(scr), "#2a1e28"); cv.put(scr, "#15101f"); cv.put(scr & (yy < y0 + 4 * s), "#1d1c34"); cv.put(scr & (yy >= y0 + 10 * s), "#0c0814")
    cv.put(rrect(sx + s, y0 + 4 * s, sx + 2 * s - 1, y0 + 5 * s - 1, 1), "#57609a"); cv.put(rrect(sx + 2 * s, y0 + 4 * s, sx + 3 * s - 1, y0 + 5 * s - 1, 1), "#3a4070")
    if eye == "off": return
    for k, side in enumerate(("L", "R")):
        exx = sw // 2 - 3 + (5 * k) + ex; eyy = 2 + ey
        X0 = sx + exx * s; Y0 = y0 + 3 * s + eyy * s
        if eye == "blink": cv.put(rrect(X0 - 2, Y0 + 2 * s + 1, X0 + 2 * s + 1, Y0 + 3 * s - 2, 2), "#fcc794"); continue
        top = {"wide": -1, "open": 0, "squint": 1, "dim": 1}[eye]
        m = rrect(X0, Y0 + top * s, X0 + 2 * s - 1, Y0 + 3 * s - 1, 4)
        if eye == "dim": cv.put(m, "#8a6a58"); continue
        cv.put(edge(m) & scr & checker(), "#4a3040"); cv.put(m, "#fdf0d8")
        cv.put(m & (xx >= X0 + s) & (yy >= Y0 + 2 * s), "#fcc794")
        if eye != "squint": cv.put(rrect(X0 + 1, Y0 + top * s + 1, X0 + s - 1, Y0 + top * s + s - 1, 1), "#ffffff")
def body_arm(cv, x0, y0, hand=None, light="dusk"):
    s = S7; bx0 = x0 + 3 * s; bt = y0 + 13 * s
    bd = rrect(bx0, bt, bx0 + 13 * s - 1, bt + 9 * s, 2 * s)
    cv.put(edge(bd), "#46181a"); cv.put(bd, "#d8704f"); cv.put(bd & (yy < bt + s), "#f7a47e"); cv.put(bd & (xx < bx0 + s), "#f7a47e")
    cv.put(bd & (xx >= bx0 + 11 * s), "#b0503a")
    pan = rrect(bx0 + 4 * s, bt + s, bx0 + 8 * s, bt + 4 * s, 3); cv.put(edge(pan) & bd, "#b0503a"); cv.put(pan, "#f3eada"); cv.put(pan & (yy < bt + 2 * s), "#fffdf2")
    cv.put(rrect(bx0 + 6 * s, bt + 2 * s, bx0 + 7 * s - 1, bt + 3 * s - 1, 2), "#e46e4a")
    if hand is None: return
    sh = (bx0 - s // 2, bt + 2 * s + 3)
    hx, hy = hand
    arm = thick_line(sh[0], sh[1], hx + 8, hy + 4, 2 * s)
    cv.put(edge(arm), "#46181a"); cv.put(arm, "#f7a47e"); cv.put(arm & ~shift(arm, 0, 3), "#d8704f")
    mitten(cv, hx, hy)
def mitten(cv, cx, cy, squash=0):
    s = S7; h = 3 * s // 2
    m = rrect(cx - h + squash, cy - h, cx + h, cy + h, 6)
    cv.put(edge(m), "#3e2833"); cv.put(m, "#f3eada")
    cv.put(m & (yy < cy - h + s) & (xx < cx + h - s), "#fffdf2"); cv.put(m & (xx < cx - h + s + squash) & (yy < cy + h - s), "#fffdf2")
    cv.put(m & (yy >= cy + h - s + 1), "#d8cab4"); cv.put(m & (xx >= cx + h - s + 1) & (yy >= cy - h + s), "#d8cab4")
    cv.put(m & (xx >= cx + h - s + 1) & (yy >= cy + h - s + 1), "#a8927a")
def flash(cv, x, y, k):
    r = [5, 8, 10][k]
    for (ddx, ddy) in ((-1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1)):
        for q in range(r - 3, r + 1): cv.px(x + ddx * q, y + ddy * q, "#fffbe8" if k < 2 else "#ffe6a0")
def ease(a, b, u): u = min(1.0, max(0.0, u)); u = u * u * (3 - 2 * u); return round(a + (b - a) * u)
# ---------------- shot builders
def task_frame(t):
    ox = -64; cv = Cv(); beam = background(cv, ox, "morning", cal="12")
    on = (t % 8) < 5 or t >= 56
    state = "task"
    device(cv, ox, 0, 0, state, t, 11, beam, on=on)
    if on and t < 56 and (t % 8) < 3: sound_lines(cv, 0, 190 + ox, "#fff0a0", period=99)
    # the robot on standby at the right edge: head down; bulb flickers, eyes boot, then SNAP up
    snap = t >= 56
    y0 = 52 if snap else 60
    bulb = (t >= 44 and t % 3 != 0) or t >= 50
    eye = "off"
    if t in (48, 49, 52, 53): eye = "dim"
    if t >= 56: eye = "wide" if t < 62 else "open"
    body_arm(cv, 300, y0 + (0 if snap else 2), None)
    head(cv, 300, y0, "front", eye, -2 if t >= 60 else 0, 0, bulb=bulb, light="morning")
    return cv
def press_frame(t):
    cv = Cv(); beam = background(cv, 0, "dusk", cal="13")
    ringing = t < 23
    dx = ((t // 2) % 2) * 2 - 1 if ringing else ((1 if t in (23, 25) else (-1 if t == 24 else 0)))
    bdx = 2 * dx if ringing else 0
    # mitten centre path: hover (tremble) -> wind back -> snap to contact -> push -> hold
    if t < 14: mx, my = 292 + (1 if t % 6 == 3 else 0), 124
    elif t < 22: mx, my = ease(292, 304, (t - 14) / 7), ease(124, 120, (t - 14) / 7)
    elif t == 22: mx, my = 288, 125
    elif t == 23: mx, my = 283, 126
    elif t < 27: mx, my = [279, 277, 276][t - 24], 126
    else: mx, my = 276, 126
    ml = mx - 10
    btn_out = 11 if t < 23 else max(3, min(11, ml - 264))
    device(cv, 0, dx, bdx, "ring" if ringing else "off", t, btn_out, beam)
    if ringing: sound_lines(cv, t, 190 + dx)
    # his head + body + arm (he stands just right of the device); head leans back on the wind-up, in on the press
    hx0 = 312 + (2 if 14 <= t < 22 else (-2 if 22 <= t < 30 else 0)); hy0 = 40
    eye = "open" if t < 14 else ("squint" if t < 27 else ("blink" if t < 31 else "open"))
    body_arm(cv, hx0, hy0, (mx, my))
    head(cv, hx0, hy0, "ql", eye, -2, 0)
    mitten(cv, mx, my, squash=2 if t == 23 else (1 if t == 24 else 0))
    if 23 <= t < 26: flash(cv, ml - 1, 126, t - 23)
    return cv
if __name__ == "__main__":
    for name, fn, n in (("task", task_frame, 68), ("press", press_frame, 64)):
        os.makedirs(f"{HERE}/{name}", exist_ok=True)
        for t in range(n): fn(t).save(f"{HERE}/{name}/f{t:03d}.png")
        print(name, n)
