import sys
from PIL import Image
F = 'frames/'; V = '../v07/'
def sheet(names, out, S=5, cols=6, box=(196, 40, 252, 84), extra=('alarm_idle07.png',)):
    box = (box[0] + 56, box[1] + 26, box[2] + 56, box[3] + 26)
    bg = Image.open(V + 'albedo07.png').convert('RGBA')
    for e in ('emit_win07.png', 'emit_lamps07.png') + tuple(extra): bg.alpha_composite(Image.open(V + e).convert('RGBA'))
    W, H = box[2] - box[0], box[3] - box[1]; cells = []
    for n in names:
        extra2 = []
        if n.startswith('press') or n == 'contact': extra2 = ['alarm_btn07.png']
        im = bg.copy()
        for e in extra2: im.alpha_composite(Image.open(V + e).convert('RGBA'))
        for s in 'sae':
            l = Image.open(F + f'{n}_{s}.png').convert('RGBA')
            if s == 's': a = l.getchannel('A').point(lambda v: int(v * 0.4)); l = Image.new('RGBA', l.size, (20, 8, 16, 0)); l.putalpha(a)
            im.alpha_composite(l)
        cells.append(im.crop(box).resize((W * S, H * S), Image.NEAREST))
    cols = min(cols, len(cells)); rows = (len(cells) + cols - 1) // cols
    sh = Image.new('RGB', (cols * (W * S + 4), rows * (H * S + 4)), (20, 16, 20))
    for i, c in enumerate(cells): sh.paste(c, ((i % cols) * (W * S + 4), (i // cols) * (H * S + 4)))
    sh.save(out)
if __name__ == '__main__': sheet(sys.argv[2].split(','), sys.argv[1], S=int(sys.argv[3]) if len(sys.argv) > 3 else 5)
