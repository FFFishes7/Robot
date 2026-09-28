import json, subprocess, sys, edl08
from PIL import Image, ImageDraw, ImageFont
tl = json.load(open('frames/timeline08.json')); R = tl['robot']
def first(n, k=0):
    idx = [i for i, r in enumerate(R) if r == n]; return idx[min(k, len(idx) - 1)]
items = json.loads(sys.argv[1]); out = sys.argv[2]; crop = sys.argv[3] if len(sys.argv) > 3 else None
fr = []
for lab, spec in items:
    if isinstance(spec, str) and spec.startswith('clip:'):
        _, c, o = spec.split(':'); f = edl08.clip_start(c) + int(o)
    elif isinstance(spec, str): f = edl08.out_of_wide(first(*spec.split('@')) if '@' not in spec else first(spec.split('@')[0], int(spec.split('@')[1])))
    else: f = edl08.out_of_wide(spec)
    fr.append((lab, f))
sel = '+'.join(f'eq(n\\,{f})' for _, f in fr)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '/workspace/robot2d/robot_story_full_08.mp4', '-vf', f'select={sel}', '-vsync', '0', '/tmp/v8_%03d.png'], check=True)
order = sorted(range(len(fr)), key=lambda i: fr[i][1])
W, H = 480, 270; cols = 4; rows = (len(fr) + cols - 1) // cols
S = Image.new('RGB', (cols * W, rows * (H + 22)), (20, 20, 20)); d = ImageDraw.Draw(S)
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
for k, i in enumerate(order):
    im = Image.open('/tmp/v8_%03d.png' % (k + 1)).convert('RGB')
    if crop: im = im.crop(tuple(map(int, crop.split(','))))
    x, y = (k % cols) * W, (k // cols) * (H + 22)
    S.paste(im.resize((W, H)), (x, y + 22)); d.text((x + 4, y + 3), f'{fr[i][1]/24:5.2f}s {fr[i][0]}', font=F, fill=(255, 230, 150))
S.save(out); print([(l, f, round(f / 24, 2)) for l, f in sorted(fr, key=lambda t: t[1])])
