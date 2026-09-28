from PIL import Image, ImageDraw, ImageFont
R='refs_games/'
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22)
f2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
W,H=1920,1080+60+400+40
C=Image.new('RGB',(W,H),(18,14,20)); d=ImageDraw.Draw(C)
def lab(x,y,t,s=None):
    d.text((x+8,y+6),t,font=F,fill=(240,228,210)); 
    if s: d.text((x+8,y+32),s,font=f2,fill=(190,178,170))
ours=Image.open('robot_2d_04.png').convert('RGB')
C.paste(ours.resize((1280,720),Image.LANCZOS),(0,40)); lab(0,0,'robot_2d_04  (384x216 native, shown 3.33x)')
sd=Image.open(R+'stardew_Saloon_Interior.png').convert('RGB').crop((20,0,284,149))  # native px
C.paste(sd.resize((640,361),Image.NEAREST).crop((0,0,640,360)),(1280,40)); lab(1280,0,'Stardew Valley - Saloon interior (wiki map)')
tm=Image.open(R+'tothemoon_study_lamp_night.jpg').convert('RGB').crop((460,300,1460,863))
C.paste(tm.resize((640,360),Image.LANCZOS),(1280,440)); d.text((1288,406),'To the Moon - Johnny\'s house (Steam)',font=F,fill=(240,228,210))
lh=Image.open(R+'tothemoon_lighthouse_interior_lamp_room.jpg').convert('RGB')
lh=lh.crop((112,60,512,285)).resize((640,360),Image.NEAREST)
# bottom row: detail crops at 4x game-pixel scale
y0=812; d.text((8,y0-2),'Detail crops, nearest-neighbour (ours 3x, Stardew 3x, To the Moon 2x game pixels):',font=F,fill=(240,228,210))
nat=Image.open('robot_2d_04.png').convert('RGB')
crops=[(nat.crop((567,550,1367,1000)),'ours: robot in the dusk window pool'),
       (Image.open(R+'stardew_Saloon_Interior.png').convert('RGB').crop((40,20,200,110)),'Stardew: density, outlines, planks'),
       (Image.open(R+'tothemoon_house_bedroom_rabbits_piano.jpg').convert('RGB').crop((160,135,400,270)),'To the Moon: house bedroom props'),
       (Image.open(R+'tothemoon_lighthouse_interior_lamp_room.jpg').convert('RGB').crop((192,185,432,320)),'To the Moon: lighthouse lamp room')]
for i,(im,t) in enumerate(crops):
    C.paste(im.resize((480,270),Image.NEAREST),(i*480,y0+30+60)); d.text((i*480+8,y0+34),t,font=f2,fill=(200,190,180))
C=C.crop((0,0,W,y0+30+60+270+10))
C.save('compare_04.png'); print(C.size)
