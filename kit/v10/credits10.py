"""End credits at the film's native grain (384x216, 1-px pixel font Pixelify Sans OFL, no antialiasing),
palette-stepped fades (4 steps, like a game fade) over a dark plum night with a few twinkling stars."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
PX = '/usr/share/fonts/truetype/sand-box/google/Pixelify Sans/PixelifySans-VariableFont_wght.ttf'
BG = (22, 13, 22); CREAM = (243, 234, 218); SAL = (247, 164, 126); SALD = (126, 51, 34); MUTE = (168, 146, 122); OUT = (46, 20, 26)
N = 156
def text_layer(txt, size, col, shadow=None, outline=None):
    f = ImageFont.truetype(PX, size); bb = f.getbbox(txt)
    w, h = bb[2] - bb[0] + 4, bb[3] - bb[1] + 5
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.fontmode = '1'
    ox, oy = 2 - bb[0], 2 - bb[1]
    if shadow: d.text((ox + 1, oy + 1), txt, font=f, fill=shadow)
    if outline:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)): d.text((ox + dx, oy + dy), txt, font=f, fill=outline)
    d.text((ox, oy), txt, font=f, fill=col)
    return im
def brackets(h, col, dark):
    """hand-drawn 《 》 at the title height (1-px strokes)"""
    w = 8; L = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0)); p = L.load()
    mid = h // 2
    for y in range(h):
        dx = abs(y - mid) * (w - 3) // max(1, mid)
        for off in (0, 3):
            x = 1 + dx + off
            if 0 <= x < w + 2: p[x, y] = col + (255,)
            if 0 <= x + 1 < w + 2 and y + 1 < h + 2 and p[x + 1, y + 1][3] == 0: p[x + 1, y + 1] = dark + (255,)
    R = L.transpose(Image.FLIP_LEFT_RIGHT)
    return L, R
def title_img():
    t = text_layer('Robot', 16, CREAM, shadow=SALD, outline=OUT)
    a = np.array(t); h = a.shape[0]
    # warm lower half on the letter faces (cream -> salmon light), like the robot's own two-tone palette
    face = (a[..., 0] == CREAM[0]) & (a[..., 1] == CREAM[1])
    rows = np.arange(h)[:, None] > h * 0.62
    a[face & rows, :3] = (252, 214, 180)
    t = Image.fromarray(a)
    L, R = brackets(h - 6, SAL, SALD)
    W = L.width + 3 + t.width + 3 + R.width
    im = Image.new('RGBA', (W, h), (0, 0, 0, 0)); im.alpha_composite(L, (0, 3)); im.alpha_composite(t, (L.width + 3, 0)); im.alpha_composite(R, (L.width + 6 + t.width, 3))
    return im
LINES = [("made with", "Aseprite, Godot & Python"),
         ("sound effects", "Kenney (CC0)"),
         ("font", "Pixelify Sans (OFL)"),
         ("motion reference", "Bilibili repost, original author unknown"),
         ("inspired by", "Stardew Valley & To the Moon")]
N = 168
BG_arr = np.array(BG, np.float32)
def head_icon():
    RF = "/workspace/robot2d/kit/robot09/frames/"
    im = Image.new('RGBA', (448, 288), (0, 0, 0, 0))
    for s_ in 'ae': im.alpha_composite(Image.open(RF + f"attention_{s_}.png").convert('RGBA'))
    a = np.array(im); box = (227 + 56 - 2, 53 + 26 - 5, 245 + 56 + 3, 66 + 26 + 1)
    return Image.fromarray(a).crop(box)
def steps(i, a, b):
    """palette step 0..4 for a card visible in [a, b)"""
    return max(0, min(4, (i - a) // 3, (b - 1 - i) // 3))
def apply(im, L_, k):
    if k <= 0: return
    a = np.array(L_).astype(np.float32); m = a[..., 3] > 0
    a[..., :3] = np.array(BG) + (a[..., :3] - np.array(BG)) * (k / 4.0)
    a[..., 3] = np.where(m, 255, 0); im.alpha_composite(Image.fromarray(a.astype(np.uint8)))
_cache = {}
def cards():
    if _cache: return _cache["A"], _cache["B"]
    A = Image.new('RGBA', (384, 216), (0, 0, 0, 0))
    H = head_icon(); A.alpha_composite(H, ((384 - H.width) // 2, 70))
    T = title_img(); A.alpha_composite(T, ((384 - T.width) // 2, 96))
    s_ = text_layer("a short film by Alan Yu", 12, MUTE); A.alpha_composite(s_, ((384 - s_.width) // 2, 124))
    B = Image.new('RGBA', (384, 216), (0, 0, 0, 0)); y = 44
    for lab, name in LINES:
        a = text_layer(lab, 12, MUTE); b = text_layer(name, 12, CREAM, shadow=OUT)
        B.alpha_composite(a, ((384 - a.width) // 2, y)); B.alpha_composite(b, ((384 - b.width) // 2, y + 11)); y += 27
    _cache["A"], _cache["B"] = A, B
    return A, B
def frame(i, backdrop=None):
    im = Image.new('RGBA', (384, 216), BG + (255,))
    if backdrop is not None:                       # v10: the ending's night sky (Milky Way + moon), dimmed for legibility
        b = BG_arr + (backdrop.astype(np.float32) - BG_arr) * 0.5
        im = Image.fromarray(np.concatenate([b.astype(np.uint8), np.full((216, 384, 1), 255, np.uint8)], -1))
    st = np.random.RandomState(11); p = im.load()
    gk = max(0, min(4, i // 3, (N - 1 - i) // 3))
    for s in range(38 if backdrop is None else 0):
        x, y, ph = st.randint(4, 380), st.randint(4, 212), st.randint(0, 40)
        on = ((i + ph) // 20) % 3 != 0
        c = np.array((120, 104, 140) if on else (58, 44, 64))
        if s % 7 == 0 and on: c = np.array((214, 196, 170))
        c = np.array(BG) + (c - np.array(BG)) * gk / 4.0
        p[x, y] = tuple(int(v) for v in c) + (255,)
    A, B = cards()
    apply(im, A, steps(i, 2, 76)); apply(im, B, steps(i, 78, N))
    if backdrop is not None:
        ko = max(0, min(4, (N - 1 - i) // 4))
        if ko < 4:
            a = np.array(im).astype(np.float32); a[..., :3] *= ko / 4.0; im = Image.fromarray(a.astype(np.uint8))
    return im.convert('RGB')
if __name__ == '__main__':
    import sys
    for i in (40, 120): frame(i).resize((1152, 648), Image.NEAREST).save(f'/tmp/v9chk/cred_{i}.png')
