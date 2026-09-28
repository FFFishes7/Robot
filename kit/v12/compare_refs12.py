import sys, numpy as np

sys.path.insert(0,'/workspace/robot2d/kit/v12'); sys.path.insert(0,'/workspace/robot2d/kit/v10')
from PIL import Image, ImageDraw
import panorama12 as PN, sunset10 as S
R='/workspace/robot2d/refs_games/stardew_closeups/'
LUT={'A': (50, 35, 78), 'F': (91, 61, 101), 'G': (145, 79, 104), 'H': (192, 110, 96), 'I': (214, 152, 102), 'D': (219, 181, 137)}  # band_lut(1430) of the wide
p=PN.Pano({k:np.array(v,float) for k,v in LUT.items()})
ours={f:Image.fromarray(p.frame(f)) for f in (0,70,104,167)}
for f,n in ((0,'sunset'),(70,'dusk'),(104,'night'),(167,'night_sky')): ours[f].resize((1920,1080),Image.NEAREST).save(f'/workspace/robot2d/robot_2d_12_panorama_{n}.png')
def ref(n):
    im=Image.open(R+n).convert('RGB'); w,h=im.size; s=max(384/w,216/h); im=im.resize((round(w*s),round(h*s)),Image.LANCZOS if 'jpg' in n else Image.NEAREST)
    x=(im.width-384)//2; y=(im.height-216)//2; return im.crop((x,y,x+384,y+216))
pairs=[('alan_ref_stardew_sky.png',0,'ref: Stardew title (÷5)','v12 sunset f0'),('alan_ref_beach_milkyway.jpg',70,'ref: beach Milky Way','v12 dusk f70'),('alan_ref_moon_night.jpg',104,'ref: moon night','v12 night f104')]
out=Image.new('RGB',(1536+12,3*432+24),(20,16,24)); d=ImageDraw.Draw(out)
for i,(rn,f,a,b) in enumerate(pairs):
    y=i*(432+12)
    out.paste(ref(rn).resize((768,432),Image.NEAREST),(0,y)); out.paste(ours[f].resize((768,432),Image.NEAREST),(780,y))
    d.text((6,y+4),a,fill=(255,255,255)); d.text((786,y+4),b,fill=(255,255,255))
out.save('/workspace/robot2d/robot_2d_12_panorama_vs_ref.png'); print('ok')
