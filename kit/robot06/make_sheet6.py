from PIL import Image, ImageDraw, ImageFont
import os
D=os.path.dirname(os.path.abspath(__file__)); F=D+'/frames/'; V=D+'/../v06/'
rows=[("Turnaround",["turn_front","turn_qr","turn_ql","turn_back"]),
("Expressions (screen eyes)",["expr_open","expr_blink","expr_wide","expr_happy","expr_soft","expr_squint","expr_lookL","expr_lookR","expr_lookU"]),
("Sweep cycle (8 drawings @12fps)",[f"sweep{i}" for i in range(1,9)]),
("Stop & look up at the sunset (broom drifts)",["stop","notice","antic","look1","look2","look3","look4","look4_blink"]),
("Alarm: startle, turn, anticipation, reach, press, release, look back",["startle1","startle2","turn","reach_antic","reach","press","release","lookback","lookback2"]),
("Walk cycle (8 phases, 1 drawing per frame @24fps, moving 2px/frame)",[f"walk{i:02d}" for i in range(8,16)]),
("Epilogue: lean the broom, walk to the seat, hop up",["place1","place2","turnL","arrive","arrive_up","hop_antic","hop","land"]),
("Sitting on the window seat (drawn over the glass)",["sit","sit_lookup","sit_lean"])]
import json
DJ=json.load(open(F+'drawings.json'))
S=6; CW=36; cell=CW*S; LAB=24; HDR=30; cols=9
Fb=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20); Fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
Hh=sum(HDR+LAB+cell+10 for _ in rows)
sheet=Image.new('RGB',(cols*(cell+4)+4,Hh+10),(30,22,28)); d=ImageDraw.Draw(sheet)
alb=Image.open(V+'albedo06.png').convert('RGBA'); em=Image.open(V+'emit06_static.png').convert('RGBA'); al=Image.open(V+'alarm_idle06.png').convert('RGBA')
y=6
for title,names in rows:
    d.text((8,y+4),title,font=Fb,fill=(245,232,210)); y+=HDR
    for i,n in enumerate(names):
        fr=DJ[n]['front']; wx=DJ[n]['cx']+56; wy=DJ[n]['by']+26
        if n.startswith('sit') or n=='land': wx,wy=164,95
        box=(wx-19,wy-31,wx+17,wy+5)
        im=alb.crop(box)
        sh=Image.open(F+n+'_s.png').crop(box); a=sh.getchannel('A').point(lambda v:int(v*0.42)); s2=Image.new('RGBA',sh.size,(20,8,16,0)); s2.putalpha(a); im.alpha_composite(s2)
        if fr: im.alpha_composite(em.crop(box))
        im.alpha_composite(Image.open(F+n+'_a.png').crop(box))
        if not fr: im.alpha_composite(em.crop(box))
        im.alpha_composite(Image.open(F+n+'_e.png').crop(box)); im.alpha_composite(al.crop(box))
        x=4+i*(cell+4)
        d.text((x+4,y+2),n,font=Fs,fill=(210,196,180))
        sheet.paste(im.resize((cell,cell),Image.NEAREST),(x,y+LAB))
    y+=LAB+cell+10
out=D+'/../../robot_sheet_06.png'; sheet.save(out); print(sheet.size)
sheet.resize((sheet.width//2,sheet.height//2),Image.NEAREST).save('/tmp/sheet06_half.png')
