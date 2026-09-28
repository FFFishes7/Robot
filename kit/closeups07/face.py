"""Close-up insert 1: the robot's screen-face as the dusk light hits. Drawn natively at 384x216 (same pixel size as the wide shot)."""
import os, numpy as np
from px import *
OUT = os.path.dirname(os.path.abspath(__file__)) + "/face/"; os.makedirs(OUT, exist_ok=True)
N = 66
def background(cv, t):
    k = 1.0                                  # the sunset light arrives
    # wallpaper (dim teal) with thin stripes and tiny motifs
    cv.put(yy < 128, "#2a333d")
    cv.put((yy < 128) & (xx % 10 == 3), "#313c47")
    cv.put((yy < 128) & (xx % 10 == 8) & (yy % 12 == 5), "#3a4652")
    # wainscot: cap rail + boards
    cv.put((yy >= 128) & (yy < 134), "#5a3020"); cv.put(yy == 128, "#7a4428"); cv.put(yy == 133, "#2e160e")
    cv.put(yy >= 134, "#43231a"); cv.put((yy >= 134) & (xx % 24 == 0), "#2a130c"); cv.put((yy >= 134) & (xx % 24 == 1), "#553024")
    # window edge + curtain on the right (the thing he is looking at)
    win = (xx >= 352) & (yy < 118)
    for y0, c in ((0, "#c06a78"), (18, "#e88a6a"), (40, "#f8ac72"), (62, "#ffcf8e"), (84, "#ffe6b4"), (100, "#fff2d0")):
        cv.put(win & (yy >= y0), c)
    cv.put(win & (xx >= 364) & (xx <= 366), "#6a3524"); cv.put(win & (yy >= 56) & (yy <= 58), "#6a3524")
    cv.put((xx >= 350) & (xx <= 352) & (yy < 120), "#6a3524"); cv.put((xx >= 350) & (yy >= 118) & (yy <= 121), "#7c4430")
    cur = (xx >= 334) & (xx < 352) & (yy < 150)
    cv.put(cur, "#6a2030"); cv.put(cur & (xx % 6 == 1), "#8a2c3c"); cv.put(cur & (xx % 6 == 4), "#4e1624"); cv.put(cur & (xx == 351), "#b04850")
    # warm sunbeam across the wall (parallelogram falling down-left from the window)
    beam = ((xx - 352) + (yy * 0.62) > -150) & ((xx - 352) + (yy * 0.62) < -8) & (xx < 334)
    core = ((xx - 352) + (yy * 0.62) > -118) & ((xx - 352) + (yy * 0.62) < -36) & (xx < 334)
    if k > 0.05:
        wall = yy < 128
        cv.put(beam & wall, "#5a4a4a" if k < 0.5 else "#7a5448"); cv.put(beam & wall & (xx % 10 == 3), "#836050" if k >= 0.5 else "#5e4e4c")
        cv.put(beam & ~wall & (yy >= 134), "#6a3a24" if k >= 0.5 else "#52301e")
        cv.put(beam & (yy >= 128) & (yy < 134), "#8a5230")
        if k >= 0.5:
            cv.put(core & wall, "#a06a50"); cv.put(core & wall & (xx % 10 == 3), "#aa7458")
            cv.put(core & (yy >= 134), "#824a2a"); cv.put(core & (yy == 128), "#c07a44")
            # dithered beam edges
            ed = beam & ~core & (np.abs((xx - 352) + yy * 0.62 + 36) < 3) & checker()
            cv.put(ed & wall, "#a06a50")
    return beam
def robot(cv, t, dx, dy, eye, look, bulb, beam):
    X = lambda v: v + dx; Y = lambda v: v + dy
    head = rrect(X(78), Y(38), X(262), Y(178), 20)
    # cast shadow of the head on the wall (light from the right)
    sh = shift(head, -20, 6) & ~head & beam
    cv.put(sh & (yy < 128), "#4a3a40"); cv.put(sh & (yy >= 128), "#3a2016")
    body = rrect(X(112), Y(186), X(248), Y(236), 12)
    neck = rrect(X(150), Y(176), X(210), Y(190), 3)
    cv.put(edge(neck), "#3e2833"); cv.put(neck, "#8e7a6a"); cv.put(neck & (yy >= Y(184)), "#6e5a4c")
    cv.put(edge(body), "#46181a"); cv.put(body, "#e8936c"); cv.put(body & (xx >= X(214)), "#f7a47e"); cv.put(body & (xx >= X(238)), "#ffc49a")
    cv.put(body & (xx <= X(132)), "#d8704f"); cv.put(body & (xx <= X(118)), "#b0503a")
    cv.put(body & (yy == Y(187)), "#ffd2b0")
    pan = rrect(X(150), Y(198), X(206), Y(236), 3)
    cv.put(edge(pan) & body, "#b0503a"); cv.put(pan, "#f3eada"); cv.put(pan & (xx >= X(196)), "#fff6e6"); cv.put(pan & (xx <= X(154)), "#d8cab4")
    led = rrect(X(190), Y(204), X(197), Y(210), 2); cv.put(edge(led), "#5a2a22"); cv.put(led, "#e46e4a"); cv.px(X(191), Y(205), "#ffb89a"); cv.px(X(192), Y(205), "#ffb89a")
    cv.put(pan & (yy >= Y(205)) & (yy <= Y(206)) & (xx >= X(158)) & (xx <= X(180)), "#d8cab4")
    cv.put(pan & (yy >= Y(211)) & (yy <= Y(212)) & (xx >= X(158)) & (xx <= X(174)), "#d8cab4")
    # head shell: cool shadowed left side, warm sunset-lit right
    cv.put(edge(head), "#3e2833")
    cv.put(head, "#f5e2cc")
    side = head & (xx <= X(100))
    cv.put(side, "#c8b8aa"); cv.put(side & (xx <= X(86)), "#a89486"); cv.put(head & (xx == X(101)), "#8e7a6e")
    cv.put(head & (xx > X(101)) & (xx <= X(118)), "#e6d0ba")
    cv.put(head & (yy <= Y(44)) & (xx > X(101)), "#fff4e4"); cv.put(head & (yy <= Y(42)) & (xx > X(120)), "#fffaf0")
    cv.put(head & (yy >= Y(166)) & (xx > X(101)), "#dcc2a8"); cv.put(head & (yy >= Y(173)), "#b89c86")
    if True:                            # sunset light falls across the shell
        hb = head & beam & (xx > X(101)); cv.put(hb, "#ffe6c4"); cv.put(hb & (yy <= Y(44)), "#fff6e6"); cv.put(hb & (yy >= Y(166)), "#f0c8a0")
        cv.put(head & beam & (xx <= X(100)) & (xx > X(86)), "#e0bca4")
        eb = head & beam & ~shift(beam, 2, 0) & (xx > X(101)) & checker(); cv.put(eb, "#ffe6c4")
    rim = head & ~shift(head, -4, 0); cv.put(rim & (xx > X(200)), "#ffd49a"); rim2 = head & ~shift(head, -2, 0); cv.put(rim2 & (xx > X(200)), "#fff0cc")
    cv.put(head & (yy >= Y(166)) & (xx <= X(100)), "#8e7a6e")
    # dithered terminator between side and front
    cv.put(head & (xx == X(102)) & checker(), "#c8b8aa")
    # ear panel on the side
    ear = rrect(X(84), Y(82), X(96), Y(132), 4)
    cv.put(edge(ear) & head, "#7e3322"); cv.put(ear, "#d8704f"); cv.put(ear & (xx >= X(93)), "#f7a47e"); cv.put(ear & (xx <= X(85)), "#b0503a")
    for yb in (92, 102, 112, 122): cv.put(ear & (yy == Y(yb)) & (xx >= X(87)) & (xx <= X(93)), "#b0503a")
    # antenna
    cap = rrect(X(154), Y(31), X(176), Y(40), 4) & (yy <= Y(38))
    cv.put(edge(cap) & ~head, "#3e2833"); cv.put(cap, "#d8cab4"); cv.put(cap & (xx >= X(168)), "#f3eada"); cv.put(cap & (yy == Y(31)), "#fff4e4")
    stalk = (xx >= X(163)) & (xx <= X(167)) & (yy >= Y(14)) & (yy <= Y(30))
    cv.put(edge(stalk) & ~cap, "#40240e"); cv.put(stalk, "#d8902a"); cv.put(stalk & (xx >= X(166)), "#ffd24a"); cv.put(stalk & (xx == X(163)), "#b0701e")
    bl = ell(X(165), Y(8), 6, 6)
    if bulb > 1:                                           # flare
        g2 = ell(X(165), Y(8), 11, 11) & ~bl & ~stalk & checker(); cv.put(g2 & (yy < Y(30)), "#8a4a3a")
    g1 = edge(bl) & ~stalk
    cv.put(g1, "#6a3a2a"); cv.put(bl, "#fc773a"); cv.put(bl & ell(X(163), Y(6), 3, 3), "#fea070"); cv.put(ell(X(162), Y(5), 1, 1), "#fed6b2")
    if bulb > 1: cv.put(bl & ell(X(165), Y(8), 3, 3), "#fed6b2")
    # screen: bezel, glass, reflections
    bez = rrect(X(116), Y(56), X(246), Y(152), 16)
    cv.put(bez, "#cbb9a4"); cv.put(bez & ~shift(bez, 0, -2), "#fff2de"); cv.put(bez & ~shift(bez, 0, 2), "#a8927a")
    scr = rrect(X(120), Y(60), X(242), Y(148), 13)
    cv.put(edge(scr), "#3a2a36"); cv.put(scr, "#15101f"); cv.put(scr & (yy <= Y(70)), "#1d1c34"); cv.put(scr & (yy >= Y(140)), "#0c0814")
    cv.put(scr & (yy == Y(71)) & checker(), "#1d1c34"); cv.put(scr & (yy == Y(139)) & checker(), "#0c0814")
    k = 1.0
    # the window reflected in the glass (upper right), warming as the light arrives
    rw = rrect(X(204), Y(64), X(236), Y(100), 4) & scr
    cv.put(rw, "#2e2238" if k < 0.5 else "#3e2840"); cv.put(rw & (yy <= Y(80)), "#3a2a44" if k < 0.5 else "#6a3a4c")
    cv.put(rw & (yy <= Y(72)), "#4a3048" if k < 0.5 else "#8a4a52")
    cv.put(rw & ((xx == X(220)) | (yy == Y(82))), "#15101f")
    if k >= 0.5:
        gb = scr & beam & ~rw & (yy < Y(140)); cv.put(gb, "#211726"); cv.put(gb & (yy <= Y(70)), "#2a1e30")
    # glints (cool) top-left
    for (a, b, c) in (((126, 82), (140, 68), "#3a4070"), ((129, 86), (145, 70), "#57609a"), ((134, 90), (138, 86), "#3a4070")):
        for (x, y) in line_pts(X(a[0]), Y(a[1]), X(b[0]), Y(b[1])): cv.px(x, y, c)
    # eyes
    ex, ey = look
    for cx in (163, 211):
        cx = X(cx + ex); cy = Y(100 + ey)
        if eye == "blink":
            m = rrect(cx - 11, cy + 3, cx + 11, cy + 5, 1)
            cv.put(edge(m) & scr, "#3a2638"); cv.put(m, "#fdf0d8"); cv.put(m & (yy == cy + 2), "#ffffff"); continue
        rx, ry = (12, 19) if eye == "wide" else (10, 16)
        m = rrect(cx - rx, cy - ry, cx + rx, cy + ry, rx)
        if eye == "soft": m &= (yy >= cy - ry + 9) & ~((yy == cy - ry + 9) & ((xx == cx - rx) | (xx == cx + rx)))
        if eye == "half": m &= yy >= cy - 3
        halo = edge(m) | edge(edge(m) | m)
        cv.put(halo & scr & checker(), "#3a2638"); cv.put(edge(m) & scr, "#5a3a4a")
        cv.put(m, "#fdf0d8"); cv.put(m & ~shift(m, -2, -2), "#fcc794")
        hl = rrect(cx - rx + 3, cy - ry + 3, cx - rx + 6, cy - ry + 8, 1) & m
        cv.put(hl, "#ffffff")
        if eye == "wide": cv.put(rrect(cx + 3, cy + 6, cx + 4, cy + 7, 0) & m, "#ffffff")
    return head
def motes(cv, t, beam):
    rng = np.random.RandomState(7)
    for i in range(14):
        x0, y0 = rng.randint(40, 340), rng.randint(0, 200); sp = rng.randint(3, 6)
        x = (x0 - t // sp) % 340; y = (y0 - t // (sp + 2)) % 210
        if beam[y, x] or rng.rand() < 0.3:
            cv.px(x, y, "#ffe8b8" if i % 3 else "#fff6dc")
            if i % 4 == 0: cv.px(x + 1, y, "#c89070")
def frame(t):
    cv = Cv("#2a333d"); beam = background(cv, t)
    if t < 5: look = (1, 0)
    elif t < 8: look = (2, -2)
    else: look = (3, -3)
    eye = "open"
    if 10 <= t < 31: eye = "wide"
    if 31 <= t < 34: eye = "blink"
    if 34 <= t < 36: eye = "half"
    if t >= 36: eye = "soft"
    if t == 9: eye = "half"
    dy = -1 if t >= 38 else 0; dy += 0 if not (10 <= t < 13) else -1
    bulb = 2 if 10 <= t < 16 else 1
    robot(cv, t, 0, dy, eye, look, bulb, beam)
    motes(cv, t, beam)
    return cv
if __name__ == "__main__":
    for t in range(N): frame(t).save(OUT + f"f{t:03d}.png")
    print("face frames", N)
