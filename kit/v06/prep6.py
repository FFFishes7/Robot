from PIL import Image
props=['stringlights','door','doormat','braidrug','coatrack','dresser','wardrobe','lampcord','floorlamp','hamper','flowertable','shoebench','sideplant','rockinghorse','boxes','bigplant','window_92','window_236','curtain_92','curtain_236','bookshelf','clock','frames','telescope','floorbits','stars','desk','chair','basket','yarn','slippers','armchair','sidetable','plant','bookstack','globe','windowseat','alarm','dustpan','dust','pouf','crate','trunk','sleeves','cabinet']
def shade(name,k,col=(20,8,16)):
    im=Image.open(f'layer_{name}.png').convert('RGBA'); a=im.getchannel('A').point(lambda v:int(v*k))
    s=Image.new('RGBA',im.size,col+(0,)); s.putalpha(a); return s
base=Image.open('layer_bg.png').convert('RGBA')
base.alpha_composite(shade('shadows',0.36)); base.alpha_composite(shade('shadows_ext',0.36)); base.alpha_composite(shade('contact',0.5))
for n in props: base.alpha_composite(Image.open(f'layer_{n}.png').convert('RGBA'))
base.save('albedo06.png')
em=Image.open('layer_emit.png').convert('RGBA'); em.alpha_composite(Image.open('layer_emit_ext.png').convert('RGBA')); em.save('emit06_static.png')
for s,d in [('alarm_emit','alarm_idle06.png'),('alarm_ring','alarm_ring06.png'),('alarm_off','alarm_off06.png')]:
    Image.open(f'layer_{s}.png').convert('RGBA').save(d)
f=base.copy(); f.alpha_composite(Image.open('emit06_static.png')); f.alpha_composite(Image.open('alarm_idle06.png')); f.save('flat06.png')
# sky-dim overlay for the full cut: window glass pixels only, deep indigo, stronger toward the top of the glass
em0=Image.open('layer_emit.png').convert('RGBA'); sky=Image.new('RGBA',em0.size,(0,0,0,0))
for x0 in (92,236):
    for y in range(30,57):
        for x in range(x0,x0+32):
            X,Y=x+56,y+26
            if em0.getpixel((X,Y))[3]>0:
                t=(y-30)/26; sky.putpixel((X,Y),(int(34+30*t),int(22+10*t),int(64-10*t),int(255*(1.0-0.45*t))))
sky.save('sky_dim06.png')
