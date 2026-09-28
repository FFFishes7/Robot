import sys, json
from PIL import Image
sys.path.insert(0, '.')
from robot07 import robot
def sheet(drs, out, bg='../v06/albedo06.png', S=8):
    bgi = Image.open(bg).convert('RGBA'); cells = []
    for P in drs:
        f = robot(P); f.save('_pv')
        wx, wy = P['cx'] + 56, P['by'] + 26; box = (wx - 20, wy - 36, wx + 20, wy + 4)
        im = bgi.crop(box)
        for s in 'sae':
            l = Image.open(f'frames/_pv_{s}.png').crop(box)
            if s == 's': a = l.getchannel('A').point(lambda v: int(v * 0.4)); l = Image.new('RGBA', l.size, (20, 8, 16, 0)); l.putalpha(a)
            im.alpha_composite(l)
        cells.append(im.resize((40 * S, 40 * S), Image.NEAREST))
    cols = min(8, len(cells)); rows = (len(cells) + cols - 1) // cols
    sh = Image.new('RGB', (cols * (40 * S + 4), rows * (40 * S + 4)), (20, 16, 20))
    for i, c in enumerate(cells): sh.paste(c, ((i % cols) * (40 * S + 4), (i // cols) * (40 * S + 4)))
    sh.save(out)
if __name__ == '__main__':
    B = dict(cx=236, by=80)
    drs = [dict(B, face=f) for f in ["front", "qr", "r", "br", "back", "bl", "l", "ql"]]
    drs += [dict(B, eye=(e, 0, 0)) for e in ["open", "blink", "wide", "soft", "happy", "squint", "dim", "off"]]
    sheet(drs, '/tmp/r7_t1.png', S=6)
