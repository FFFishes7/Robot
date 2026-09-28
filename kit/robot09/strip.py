import subprocess, sys
from PIL import Image, ImageDraw, ImageFont
# strip.py video a b step out [crop] [cols] [cellw]
v, a, b, st, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
crop = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] != '-' else None
cols = int(sys.argv[7]) if len(sys.argv) > 7 else 6; cw = int(sys.argv[8]) if len(sys.argv) > 8 else 320
fs = list(range(a, b + 1, st))
subprocess.run(['rm', '-rf', '/tmp/strip']); subprocess.run(['mkdir', '-p', '/tmp/strip'])
sel = '+'.join(f'eq(n\\,{f})' for f in fs)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', v, '-vf', f'select={sel}', '-vsync', '0', '/tmp/strip/%04d.png'], check=True)
ims = []
for k in range(len(fs)):
    im = Image.open('/tmp/strip/%04d.png' % (k + 1)).convert('RGB')
    if crop: im = im.crop(tuple(map(int, crop.split(','))))
    ims.append(im)
ch = int(cw * ims[0].height / ims[0].width)
rows = (len(ims) + cols - 1) // cols
S = Image.new('RGB', (cols * cw, rows * (ch + 16)), (0, 0, 0)); d = ImageDraw.Draw(S)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
for k, im in enumerate(ims):
    x, y = (k % cols) * cw, (k // cols) * (ch + 16)
    S.paste(im.resize((cw, ch)), (x, y + 16)); d.text((x + 2, y + 1), f'{fs[k]} {fs[k]/24:.2f}s', font=F, fill=(255, 230, 120))
S.save(out)
