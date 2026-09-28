import sys, json
from PIL import Image
F = 'frames/'; V = '../v07/'
def sheet(names, out, S=5, cols=8, box=None, alarm='alarm_idle07.png'):
    dj = json.load(open(F + 'drawings.json'))
    bg = Image.open(V + 'albedo07.png').convert('RGBA')
    for e in ('emit_win07.png', 'emit_lamps07.png', alarm): bg.alpha_composite(Image.open(V + e).convert('RGBA'))
    cells = []
    for n in names:
        if box: b = box
        else: wx, wy = dj[n]['cx'], dj[n]['by']; b = (wx - 24, wy - 40, wx + 24, wy + 6)
        bb = (b[0] + 56, b[1] + 26, b[2] + 56, b[3] + 26)
        im = bg.copy()
        for s in 'sae':
            l = Image.open(F + f'{n}_{s}.png').convert('RGBA')
            if s == 's': a = l.getchannel('A').point(lambda v: int(v * 0.42)); l = Image.new('RGBA', l.size, (20, 8, 16, 0)); l.putalpha(a)
            im.alpha_composite(l)
        cells.append(im.crop(bb).resize(((bb[2] - bb[0]) * S, (bb[3] - bb[1]) * S), Image.NEAREST))
    W, H = cells[0].size; cols = min(cols, len(cells)); rows = (len(cells) + cols - 1) // cols
    sh = Image.new('RGB', (cols * (W + 4), rows * (H + 4)), (20, 16, 20))
    for i, c in enumerate(cells): sh.paste(c, ((i % cols) * (W + 4), (i // cols) * (H + 4)))
    sh.save(out)
if __name__ == '__main__':
    box = tuple(map(int, sys.argv[4].split(','))) if len(sys.argv) > 4 else None
    sheet(sys.argv[2].split(','), sys.argv[1], S=int(sys.argv[3]) if len(sys.argv) > 3 else 5, box=box)
