import json
from PIL import Image, ImageDraw
# Ramps (dark -> light), extracted from the reference frames (style_analysis.md) — hue shifts toward
# purple/red in shadows and toward yellow/peach in lights.
R = {
 "outline":      {"ink":"#2a1a22","wood_ink":"#3a1a12","warm_ink":"#4a1a10"},
 "wood":         {"w0":"#3a1a10","w1":"#5e3018","w2":"#7a4222","w3":"#935430","w4":"#ad6a3c","w5":"#c8864c","w6":"#e0a862"},
 "plaster":      {"p0":"#8f6a4c","p1":"#b48f6a","p2":"#d4b48a","p3":"#e2c69a","p4":"#e9d0a6","p5":"#f6e6c2"},
 "robot_white":  {"rw0":"#6e5a4c","rw1":"#a8927a","rw2":"#d8cab4","rw3":"#f3eada","rw4":"#fffdf2"},
 "robot_peach":  {"rp0":"#4a1a10","rp1":"#7e3322","rp2":"#b0503a","rp3":"#d8704f","rp4":"#f39a78","rp5":"#fed6b2"},
 "screen":       {"s0":"#0c0814","s1":"#15101f","s2":"#1d1c34","s3":"#2e3154"},
 "eye":          {"e_ring2":"#2c1c26","e_ring":"#4a2c2a","e_low":"#fcc794","e_hi":"#fdf0d8","e_core":"#ffffff","e_gold":"#ffd24a","e_gold2":"#f0a830"},
 "rug":          {"r_dk":"#6a2a1e","r_red2":"#8c2e22","r_red":"#b0402c","r_red_hi":"#cf5a36","r_teal2":"#1f4a52","r_teal":"#2f6a6e","r_teal_hi":"#3f7e76","r_cream":"#e7c3a0","r_cream2":"#b88768","r_ochre":"#d9a441","r_orange":"#e8843a"},
 "light":        {"l_sun3":"#fefd98","l_sun2":"#fbd236","l_sun1":"#fc773a","l_sun0":"#fb552a","l_spark":"#fff4c8","l_spark2":"#ffd970"},
 "shadow_purple":{"sh0":"#1c1224","sh1":"#2e1f3a","sh2":"#46304f","sh3":"#5e4262","sh4":"#7a5a74"},
 "sky":          {"sky0":"#6f8cc0","sky1":"#86b4dc","sky2":"#a6cde8","sky3":"#c6e2ee","sky4":"#e6f0e8","sky5":"#fbf4dc"},
 "accent_lospec_resurrect64": {},
}
res=[l.strip() for l in open('resurrect-64.hex') if l.strip()]
for i in [8,12,20,26,31,36,40,45,50]: R["accent_lospec_resurrect64"]["acc%d"%i]="#"+res[i]
json.dump(R,open('attic_palette.json','w'),indent=1)
flat=[(n,c) for g in R.values() for n,c in g.items()]
with open('attic.gpl','w') as f:
    f.write("GIMP Palette\nName: attic (robot2d)\nColumns: 8\n#\n")
    for n,c in flat:
        r,g,b=(int(c[i:i+2],16) for i in (1,3,5)); f.write(f"{r:3d} {g:3d} {b:3d}\t{n}\n")
open('attic.hex','w').write("\n".join(c[1:] for n,c in flat)+"\n")
# swatch sheet
rows=list(R.items()); im=Image.new('RGB',(40+8*28*2,len(rows)*34+10),(24,20,28)); d=ImageDraw.Draw(im)
for i,(g,cs) in enumerate(rows):
    d.text((4,i*34+12),g[:14],fill=(220,220,220))
    for j,(n,c) in enumerate(cs.items()): d.rectangle([110+j*36,i*34+6,110+j*36+30,i*34+34],fill=c)
im.save('attic_palette.png'); print(len(flat),'colours')
