from PIL import Image
props=['window_92','window_236','curtain_92','curtain_236','bookshelf','clock','frames','telescope','floorbits','stars','desk','chair','basket','yarn','slippers','armchair','sidetable','plant','bookstack','globe','windowseat','alarm','dustpan','dust','pouf','crate','trunk','sleeves','cabinet']
def shade(name,k,col=(20,8,16)):
    im=Image.open(f'layer_{name}.png').convert('RGBA'); a=im.getchannel('A').point(lambda v:int(v*k))
    s=Image.new('RGBA',im.size,col+(0,)); s.putalpha(a); return s
base=Image.open('layer_bg.png').convert('RGBA')
base.alpha_composite(shade('shadows',0.36)); base.alpha_composite(shade('contact',0.5))
for n in props: base.alpha_composite(Image.open(f'layer_{n}.png').convert('RGBA'))
base.save('albedo05.png')
em=Image.open('layer_emit.png').convert('RGBA'); em.alpha_composite(Image.open('layer_alarm_emit.png').convert('RGBA')); em.save('emit05.png')
for s,d in [('robot','robot05_stand.png'),('robot_emit','robot_emit05_stand.png'),('robot_look','robot05.png'),('robot_look_emit','robot_emit05.png'),('robot_look_emit_blink','robot_emit05_look_blink.png'),('alarm_ring','alarm_ring05.png'),('robot_crouch','robot05_crouch.png'),('robot_air','robot05_air.png'),('robot_emit_blink','robot_emit05_blink.png'),('robot_emit_crouch','robot_emit05_crouch.png'),('robot_emit_air','robot_emit05_air.png')]:
    Image.open(f'layer_{s}.png').convert('RGBA').save(d)
f=base.copy(); f.alpha_composite(shade('robot_shadow',0.36)); f.alpha_composite(Image.open('robot05.png')); f.alpha_composite(Image.open('emit05.png')); f.alpha_composite(Image.open('robot_emit05.png'))
f.save('flat05.png'); f.resize((1152,648),Image.NEAREST).save('/tmp/f5a.png')
for i,(b) in enumerate([(40,20,200,104),(190,20,344,104),(40,92,200,200),(230,110,344,200)]):
    c=f.crop(b); c.resize((c.width*6,c.height*6),Image.NEAREST).save(f'/tmp/f5z{i}.png')
