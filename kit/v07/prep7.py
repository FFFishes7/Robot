# v07 composites: albedo, split emitters (windows vs lamps), reminder states, calendar pages, sky overlays, dust stages
from PIL import Image
import random
props=['stringlights','door','doormat','braidrug','coatrack','dresser','wardrobe','lampcord','floorlamp','hamper','flowertable','shoebench','sideplant','rh_base','rockinghorse','boxes','bigplant','window_92','window_236','curtain_92','curtain_236','bookshelf','clock','frames','telescope','floorbits','stars','desk','chair','basket','yarn','slippers','armchair','sidetable','plant','bookstack','globe','windowseat','calendar','alarm','dustpan','pouf','crate','trunk','sleeves','cabinet']
def L(n): return Image.open(f'layer_{n}.png').convert('RGBA')
def shade(name,k,col=(20,8,16)):
    im=L(name); a=im.getchannel('A').point(lambda v:int(v*k)); s=Image.new('RGBA',im.size,col+(0,)); s.putalpha(a); return s
base=L('bg')
base.alpha_composite(shade('shadows',0.36)); base.alpha_composite(shade('shadows_ext',0.36)); base.alpha_composite(shade('contact',0.5))
for n in props: base.alpha_composite(L(n))
base.save('albedo07.png')
em=L('emit'); win=Image.new('RGBA',em.size,(0,0,0,0)); lamps=Image.new('RGBA',em.size,(0,0,0,0))
WINR=[(92+56,30+26,123+56,56+26),(236+56,30+26,267+56,56+26)]
for y in range(em.height):
    for x in range(em.width):
        p=em.getpixel((x,y))
        if p[3]==0: continue
        (win if any(a<=x<=c and b<=y<=d for a,b,c,d in WINR) else lamps).putpixel((x,y),p)
lamps.alpha_composite(L('emit_ext'))
win.save('emit_win07.png'); lamps.save('emit_lamps07.png')
for s,d in [('alarm_emit','alarm_idle07'),('alarm_ring','alarm_ring07'),('alarm_off','alarm_off07'),('alarm_task','alarm_task07'),('alarm_btn_down','alarm_btn07'),('cal_12','cal_1207'),('cal_13','cal_1307')]:
    L(s).save(d+'.png')
Image.new('RGBA',em.size,(0,0,0,0)).save('alarm_dark07.png')
sky=Image.new('RGBA',em.size,(0,0,0,0)); day=Image.new('RGBA',em.size,(0,0,0,0))
for (a,b,c,d) in WINR:
    for y in range(b,d+1):
        for x in range(a,c+1):
            if win.getpixel((x,y))[3]>0:
                t=(y-b)/(d-b)
                sky.putpixel((x,y),(int(34+30*t),int(22+10*t),int(64-10*t),int(255*(1.0-0.45*t))))
                day.putpixel((x,y),(int(196+20*t),int(214+10*t),int(226-6*t),int(255*(0.85-0.25*t))))
sky.save('sky_dim07.png'); day.save('sky_day07.png')
# dust: specks scattered over the sweep zone gather leftward into a pile at the dustpan lip, then vanish into the pan
random.seed(7); N=46
start=[(random.uniform(222,252),random.uniform(78,87)) for _ in range(N)]
target=[(random.gauss(226,1.6),random.gauss(82,0.8)) for _ in range(N)]
cols=['#a88a68','#c09878','#8e7458','#b8a080','#d8c4a0']
order=sorted(range(N),key=lambda i:start[i][0])        # the leftmost specks go into the pan first
STAGES=8
for k in range(STAGES):
    t=k/(STAGES-1); im=Image.new('RGBA',em.size,(0,0,0,0))
    gone=set(order[:int(N*max(0,(t-0.45)/0.55)*0.92)])
    for i in range(N):
        if i in gone: continue
        tt=min(1,t*1.6); x=start[i][0]+(target[i][0]-start[i][0])*tt; y=start[i][1]+(target[i][1]-start[i][1])*tt
        X,Y=round(x)+56,round(y)+26
        im.putpixel((X,Y),Image.new('RGBA',(1,1),cols[i%len(cols)]).getpixel((0,0)))
    # clump shading: pixels with 2+ neighbours get a darker underside
    px=im.load(); add=[]
    for y in range(1,em.height-1):
        for x in range(1,em.width-1):
            if px[x,y][3] and px[x,y+1][3]==0 and px[x-1,y][3] and px[x+1,y][3]: add.append((x,y+1))
    for q in add: px[q]=(90,52,36,255)
    im.save(f'dust{k}07.png')
f=base.copy(); f.alpha_composite(win); f.alpha_composite(lamps); f.alpha_composite(L('alarm_task')); f.alpha_composite(L('cal_12')); f.alpha_composite(Image.open('dust007.png')); f.save('flat07.png')
print('ok')
