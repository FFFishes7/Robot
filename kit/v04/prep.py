from PIL import Image
props=['window_92','window_236','curtain_92','curtain_236','bookshelf','clock','frames','telescope','floorbits','desk','chair','basket','bookstack','pouf','armchair','sidetable','plant','cabinet','crates']
base=Image.open('layer_bg.png').convert('RGBA')
im=Image.open('layer_shadows.png').convert('RGBA')
a=im.getchannel('A').point(lambda v:int(v*0.38)); sh=Image.new('RGBA',im.size,(20,8,16,0)); sh.putalpha(a); base.alpha_composite(sh)
for n in props: base.alpha_composite(Image.open(f'layer_{n}.png').convert('RGBA'))
base.save('albedo04.png')
for s,d in [('emit','emit04.png'),('robot','robot04.png'),('robot_emit','robot_emit04.png')]:
    Image.open(f'layer_{s}.png').convert('RGBA').save(d)
