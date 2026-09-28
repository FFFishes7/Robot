import sys
from PIL import Image, ImageDraw
A='/workspace/robot2d/analysis/'
def frame(p): return Image.open(p).convert('RGB').resize((1920,1080),Image.LANCZOS)
mine=Image.open(sys.argv[1]).convert('RGB')
r3=frame(A+'r3_game.png'); r2=frame(A+'r2_game.png'); r4=frame(A+'r4_game.png')
def z(im,box,s=3): c=im.crop(box); return c.resize((c.width*s,c.height*s),Image.NEAREST)
rows=[(z(r3,(700,390,1000,630)), z(mine,(640,500,940,740)), 'robot head + sparkles: ref r3 | mine'),
      (z(r2,(60,480,360,720)), z(mine,(330,420,630,660)), 'dithered light bands on wall / shaft: ref r2 | mine'),
      (z(r3,(1300,800,1600,1040)), z(mine,(560,840,860,1080)), 'lit rug + floor: ref r3 | mine')]
out=Image.new('RGB',(1830,sum(a.height+40 for a,_,_ in rows)),(20,20,24)); d=ImageDraw.Draw(out); y=0
for a,b,t in rows:
    d.text((10,y+12),t+'  (both at 1920x1080 frame scale, 300x240 crop, 3x nearest)',fill=(230,230,230))
    out.paste(a,(0,y+40)); out.paste(b,(930,y+40)); y+=a.height+40
out.save(sys.argv[2])
