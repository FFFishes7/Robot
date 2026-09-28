import sys, json
from PIL import Image
F='frames/'; bgp=sys.argv[1]; names=sys.argv[2].split(','); out=sys.argv[3]
bg=Image.open(bgp).convert('RGBA'); S=8; cols=min(6,len(names))
cells=[]
for n in names:
    sit=n.startswith('sit'); box=(146,64,182,100) if sit else (int(__import__('os').environ.get('BX','274')),76,int(__import__('os').environ.get('BX','274'))+36,112)
    im=bg.crop(box)
    for suf in ('s','a','e'):
        l=Image.open(F+f'{n}_{suf}.png').crop(box)
        if suf=='s': a=l.getchannel('A').point(lambda v:int(v*0.4)); l=Image.new('RGBA',l.size,(20,8,16,0)); l.putalpha(a)
        im.alpha_composite(l)
    cells.append(im.resize((36*S,36*S),Image.NEAREST))
rows=(len(cells)+cols-1)//cols
sheet=Image.new('RGB',(cols*36*S+cols*4,rows*36*S+rows*4),(20,16,20))
for i,c in enumerate(cells): sheet.paste(c,((i%cols)*(36*S+4),(i//cols)*(36*S+4)))
sheet.save(out)
