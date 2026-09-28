from PIL import Image
import sys
order=['bg','shadows','window_92','window_236','curtain_92','curtain_236','bookshelf','clock','frames','telescope','floorbits','desk','chair','basket','bookstack','pouf','armchair','sidetable','plant','cabinet','crates','emit','robot','robot_emit']
base=Image.open('layer_bg.png').convert('RGBA')
for n in order[1:]:
    im=Image.open(f'layer_{n}.png').convert('RGBA')
    if n=='shadows':
        a=im.getchannel('A').point(lambda v: int(v*0.38)); sh=Image.new('RGBA',im.size,(20,8,16,0)); sh.putalpha(a); base.alpha_composite(sh)
    else: base.alpha_composite(im)
base.save('flat_native.png'); base.resize((1152,648),Image.NEAREST).save('/tmp/flat04.png')
