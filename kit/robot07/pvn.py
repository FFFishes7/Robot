import sys, json
from PIL import Image
F = 'frames/'
def sheet(names, out, S=6, cols=8, bg='../v06/albedo06.png', em='../v06/emit06_static.png'):
    dj = json.load(open(F + 'drawings.json')); bgi = Image.open(bg).convert('RGBA'); emi = Image.open(em).convert('RGBA')
    cells = []
    for n in names:
        wx, wy = dj[n]['cx'] + 56, dj[n]['by'] + 26
        if dj[n]['front'] and n != 'hop': wx, wy = 164, 101
        box = (wx - 20, wy - 36, wx + 20, wy + 4); im = bgi.crop(box)
        fr = True
        if fr: im.alpha_composite(emi.crop(box))
        for s in 'sae':
            if s == 'e' and not fr: im.alpha_composite(emi.crop(box))
            l = Image.open(F + f'{n}_{s}.png').crop(box)
            if s == 's': a = l.getchannel('A').point(lambda v: int(v * 0.4)); l = Image.new('RGBA', l.size, (20, 8, 16, 0)); l.putalpha(a)
            im.alpha_composite(l)
        cells.append(im.resize((40 * S, 40 * S), Image.NEAREST))
    cols = min(cols, len(cells)); rows = (len(cells) + cols - 1) // cols
    sh = Image.new('RGB', (cols * (40 * S + 4), rows * (40 * S + 4)), (20, 16, 20))
    for i, c in enumerate(cells): sh.paste(c, ((i % cols) * (40 * S + 4), (i // cols) * (40 * S + 4)))
    sh.save(out)
if __name__ == '__main__': sheet(sys.argv[2].split(','), sys.argv[1], S=int(sys.argv[3]) if len(sys.argv) > 3 else 6)
