# Writes the attic room as a Tiled map (TMX + TSX); Tiled CLI then exports JSON / raster.
import json, random
from PIL import Image
random.seed(3)
SP='/workspace/robot2d/kit/sprites/'
props=json.load(open(SP+'props.json'))['frames']
# image-collection tileset for props (trimmed per-layer PNGs from Aseprite)
sheet=Image.open(SP+'props_sheet.png')
import os; os.makedirs(SP+'props',exist_ok=True)
tiles=[]
for i,f in enumerate(props):
    r=f['frame']; im=sheet.crop((r['x'],r['y'],r['x']+r['w'],r['y']+r['h'])); p=SP+'props/'+f['filename']+'.png'; im.save(p)
    tiles.append((i,f['filename'],r['w'],r['h'],f['spriteSourceSize']))
with open('props.tsx','w') as t:
    t.write('<?xml version="1.0" encoding="UTF-8"?>\n<tileset version="1.10" name="props" tilewidth="200" tileheight="95" tilecount="%d" columns="0">\n <grid orientation="orthogonal" width="1" height="1"/>\n'%len(tiles))
    for i,n,w,h,_ in tiles: t.write(f' <tile id="{i}" type="{n}">\n  <image source="../sprites/props/{n}.png" width="{w}" height="{h}"/>\n </tile>\n')
    t.write('</tileset>\n')
with open('attic_tiles.tsx','w') as t:
    t.write('<?xml version="1.0" encoding="UTF-8"?>\n<tileset version="1.10" name="attic_tiles" tilewidth="8" tileheight="8" tilecount="16" columns="16">\n <image source="../sprites/attic_tiles.png" width="128" height="8"/>\n</tileset>\n')
MW,MH=48,27
g=[[0]*MW for _ in range(MH)]
for y in range(MH):
    for x in range(MW):
        if y<16:
            r=random.random(); t=0 if r<0.45 else (1+int(r*10)%3 if r<0.75 else 4+int(r*10)%2)
            g[y][x]=t+1
g[0]=[7]*MW
for x in range(MW): g[15][x]=10
for y in range(1,15): g[y][40]=13; g[y][41]=16 if y%3==0 else 15
g[15][40]=13; g[15][41]=15
FIRST_PROPS=17
objs=[]
oid=1
for i,n,w,h,ss in tiles:
    objs.append(f'  <object id="{oid}" name="{n}" gid="{FIRST_PROPS+i}" x="{ss["x"]}" y="{ss["y"]+h}" width="{w}" height="{h}"/>'); oid+=1
lights=[
 ('sun_pool','ellipse',dict(x=106,y=172,width=84,height=28),dict(intensity=4.2,mullions=True)),
 ('wall_patch','ellipse',dict(x=96,y=70,width=34,height=96),dict(intensity=1.3,angle=-33.0)),
 ('window_glow','ellipse',dict(x=20,y=-4,width=104,height=100),dict(intensity=0.6)),
 ('robot_shadow','ellipse',dict(x=138,y=183,width=44,height=8),dict(intensity=-3.6)),
 ('stool_shadow','ellipse',dict(x=36,y=164,width=32,height=6),dict(intensity=-0.9)),
]
lo=[]
for n,typ,geo,pr in lights:
    ps=''.join(f'<property name="{k}" type="{"bool" if isinstance(v,bool) else "float"}" value="{str(v).lower() if isinstance(v,bool) else v}"/>' for k,v in pr.items())
    lo.append(f'  <object id="{oid}" name="{n}" x="{geo["x"]}" y="{geo["y"]}" width="{geo["width"]}" height="{geo["height"]}"><properties>{ps}</properties><ellipse/></object>'); oid+=1
lo.append(f'  <object id="{oid}" name="sun_shaft" x="0" y="0"><polygon points="54,34 88,28 186,186 114,190"/></object>'); oid+=1
lo.append(f'  <object id="{oid}" name="robot_still" x="158" y="170"><point/></object>'); oid+=1
lo.append(f'  <object id="{oid}" name="robot_home" x="214" y="196"><point/></object>'); oid+=1
csv=',\n'.join(','.join(str(v) for v in row) for row in g)
tmx=f'''<?xml version="1.0" encoding="UTF-8"?>
<map version="1.10" tiledversion="1.11" orientation="orthogonal" renderorder="right-down" width="{MW}" height="{MH}" tilewidth="8" tileheight="8" infinite="0" nextlayerid="6" nextobjectid="{oid+1}">
 <properties>
  <property name="native_w" type="int" value="384"/><property name="native_h" type="int" value="216"/>
  <property name="floor_y" type="int" value="128"/>
 </properties>
 <tileset firstgid="1" source="attic_tiles.tsx"/>
 <tileset firstgid="{FIRST_PROPS}" source="props.tsx"/>
 <layer id="1" name="wall" width="{MW}" height="{MH}">
  <data encoding="csv">
{csv}
</data>
 </layer>
 <imagelayer id="2" name="floor" offsetx="0" offsety="128">
  <image source="../sprites/floor.png" width="384" height="88"/>
 </imagelayer>
 <objectgroup id="3" name="props">
{chr(10).join(objs)}
 </objectgroup>
 <objectgroup id="4" name="lights" visible="0">
{chr(10).join(lo)}
 </objectgroup>
</map>
'''
open('attic.tmx','w').write(tmx); print('tmx ok', len(objs),'props')
