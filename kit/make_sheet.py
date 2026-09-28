from PIL import Image, ImageDraw
P='/workspace/robot2d/kit/sprites/parts/'; SP='/workspace/robot2d/kit/sprites/'
def L(n): return Image.open(P+n+'.png').convert('RGBA')
def comp(ns):
    im=Image.new('RGBA',(128,128))
    for n in ns: im.alpha_composite(L(n))
    return im
Z=4; BG=(40,32,48,255)
rows=[]
heads=['head_front','head_34','head_34L','head_tilt','head_tilt_r','head_squash','head_stretch']
rows.append(('HEADS (front, 3/4 R, 3/4 L, tilt L, tilt R, squash, stretch)',[comp([h,'face_neutral_'+h]).crop((24,16,104,72)) for h in heads],heads))
ex=['neutral','happy','curious','surprised','sleepy','annoyed','sparkle']
rows.append(('SCREEN-FACE EXPRESSIONS (emissive layer)',[comp(['head_front','face_%s_head_front'%e]).crop((24,16,104,72)) for e in ex],ex))
arms=['arm_down','arm_wave','arm_raised','arm_reach','arm_back','arm_cheer']
rows.append(('BODY + ARM POSES (pivot = shoulder, right arm = flip)',[L('body').crop((40,32,88,72))]+[L(a).crop((40,40,80,80)) for a in arms],['body']+[a[4:] for a in arms]))
legs=['legs_stand','legs_step','legs_crouch','legs_jump','legs_tuck']
rows.append(('LEGS (pivot = hip)',[L(l).crop((44,56,84,84)) for l in legs],[l[5:] for l in legs]))
sa=Image.open(SP+'robot_sheet_albedo.png').convert('RGBA'); se=Image.open(SP+'robot_sheet_emit.png').convert('RGBA'); sa.alpha_composite(se)
import json; J=json.load(open(SP+'robot_anim.json')); tags={t['name']:(t['from'],t['to']) for t in J['meta']['frameTags']}
fr=J['frames']
def frame(i): r=fr[i]['frame']; return sa.crop((r['x']+24,r['y']+20,r['x']+104,r['y']+118))
for tg in ['hop','look']:
    a,b=tags[tg]; rows.append((f'ANIMATION TAG "{tg}" (Aseprite frames @12 fps)',[frame(i) for i in range(a,b+1)],[str(i) for i in range(a,b+1)]))
W=1920; y=70; blocks=[]
for t,ims,labs in rows:
    h=max(i.height for i in ims)*Z; blocks.append((t,ims,labs,y)); y+=h+70
out=Image.new('RGBA',(W,y+20),BG); d=ImageDraw.Draw(out)
d.text((20,20),'ROBOT - character sheet  (native pixels, shown 4x nearest; drawn with Aseprite Lua tools, palette: attic.gpl)',fill=(240,230,210))
for t,ims,labs,yy in blocks:
    d.text((20,yy-24),t,fill=(250,210,150)); x=20
    for im,lb in zip(ims,labs):
        s=im.resize((im.width*Z,im.height*Z),Image.NEAREST)
        if x+s.width>W-10: s=im.resize((im.width*3,im.height*3),Image.NEAREST)
        out.alpha_composite(s,(x,yy)); d.text((x+4,yy+s.height+2),lb,fill=(190,180,200)); x+=s.width+12
out.convert('RGB').save('/workspace/robot2d/robot_sheet.png'); print(out.size)
