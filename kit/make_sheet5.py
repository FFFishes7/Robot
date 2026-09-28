from PIL import Image, ImageDraw, ImageFont
import os
os.chdir('/workspace/robot2d/kit/v05')
poses=[('stand','robot','robot_emit'),('blink','robot','robot_emit_blink'),('crouch','robot_crouch','robot_emit_crouch'),('hop (air)','robot_air','robot_emit_air'),
 ('sweep 1','robot_sweep1','robot_sweep1_emit'),('sweep 2','robot_sweep2','robot_sweep2_emit'),('sweep 3','robot_sweep3','robot_sweep3_emit'),('sweep 4','robot_sweep4','robot_sweep4_emit'),
 ('stop & look','robot_look','robot_look_emit'),('look blink','robot_look','robot_look_emit_blink'),('reach (alarm off)','robot_reach','robot_reach_emit'),('sit & watch','robot_sit','robot_sit_emit')]
S=8; cw,ch=34,34
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18)
sheet=Image.new('RGB',(4*cw*S,3*(ch*S+30)),(40,30,38)); d=ImageDraw.Draw(sheet)
for i,(t,a,e) in enumerate(poses):
    box=(96,38,96+cw,38+ch) if a=='robot_sit' else (177,139,177+cw,139+ch)
    im=Image.open('albedo05.png').convert('RGBA').crop(box)
    if a=='robot_sit': im.alpha_composite(Image.open('emit05.png').crop(box))
    for n in (a,e): im.alpha_composite(Image.open(f'layer_{n}.png').convert('RGBA').crop(box))
    x=(i%4)*cw*S; y=(i//4)*(ch*S+30)
    sheet.paste(im.resize((cw*S,ch*S),Image.NEAREST),(x,y+30)); d.text((x+8,y+5),t,font=F,fill=(240,228,210))
sheet.save('/workspace/robot2d/robot_sheet_05.png'); sheet.resize((sheet.width//2,sheet.height//2),Image.NEAREST).save('/tmp/sheet5b.png')
