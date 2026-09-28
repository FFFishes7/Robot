# v09 albedo: v07 composite with the new window bench, relocated telescope and matching shadows
from PIL import Image
import re
src = open('../v07/prep7.py').read()
props = eval(re.search(r"props=(\[.*?\])", src).group(1))
# v11: painter's order by base line -- the side table (base y125) goes behind the armchair (base y126)
props.remove('sidetable'); props.insert(props.index('armchair'), 'sidetable')
# the basket and its yarn stand in front of the armchair (base y133 vs y125)
for n in ('yarn', 'basket'): props.remove(n); props.insert(props.index('armchair') + 1, n)
def L(n): return Image.open(f'layer_{n}.png').convert('RGBA')
def shade(name, k, col=(20, 8, 16)):
    im = L(name); a = im.getchannel('A').point(lambda v: int(v * k)); s = Image.new('RGBA', im.size, col + (0,)); s.putalpha(a); return s
base = L('bg')
base.alpha_composite(shade('shadows', 0.36)); base.alpha_composite(shade('shadows_ext', 0.36)); base.alpha_composite(shade('contact', 0.5))
for n in props: base.alpha_composite(L(n))
base.save('albedo09.png')
f = base.copy()
for o in ['emit_win07', 'emit_lamps07', 'alarm_task07', 'cal_1207', 'dust007']: f.alpha_composite(Image.open(f'../v07/{o}.png').convert('RGBA'))
f.save('flat09.png'); print('ok')
