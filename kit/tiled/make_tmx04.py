# v04 map: image layers from Aseprite exports + a "lights" object layer the Godot composer reads.
import subprocess
def poly(id,name,pts,props=None):
    x0,y0=pts[0]; s=' '.join(f'{x-x0},{y-y0}' for x,y in pts)
    pr=''.join(f'<property name="{k}" type="float" value="{v}"/>' for k,v in (props or {}).items())
    pr=f'<properties>{pr}</properties>' if pr else ''
    return f'<object id="{id}" name="{name}" x="{x0}" y="{y0}">{pr}<polygon points="{s}"/></object>'
def ell(id,name,cx,cy,rx,ry,v):
    return f'<object id="{id}" name="{name}" x="{cx-rx}" y="{cy-ry}" width="{2*rx}" height="{2*ry}"><properties><property name="intensity" type="float" value="{v}"/></properties><ellipse/></object>'
objs=[
 poly(1,'pool_1',[(84,74),(126,74),(84,174),(38,174)],{'intensity':0.55}),
 poly(2,'pool_2',[(228,74),(270,74),(228,174),(182,174)],{'intensity':0.55}),
 poly(3,'shaft_1',[(92,30),(124,30),(84,174),(38,174)]),
 poly(4,'shaft_2',[(236,30),(268,30),(228,174),(182,174)]),
 ell(5,'lamp',311,72,52,36,0.5),
 ell(6,'lamp_core',311,70,18,12,0.35),
 ell(7,'win_glow_1',108,52,40,26,0.3),
 ell(8,'win_glow_2',252,52,40,26,0.3),
 ell(9,'robot_glow',193,152,10,7,0.12),
 f'<object id="10" name="robot" x="186" y="146"><point/></object>',
]
layers=['albedo04','emit04','robot04','robot_emit04']
il=''.join(f'<imagelayer id="{i+1}" name="{n}"><image source="../v04/{n}.png" width="384" height="216"/></imagelayer>' for i,n in enumerate(layers))
tmx=f'''<?xml version="1.0" encoding="UTF-8"?>
<map version="1.10" tiledversion="1.11.0" orientation="orthogonal" renderorder="right-down" width="24" height="14" tilewidth="16" tileheight="16" infinite="0" nextlayerid="7" nextobjectid="11">
{il}<objectgroup id="6" name="lights">{''.join(objs)}</objectgroup>
</map>'''
open('attic04.tmx','w').write(tmx)
subprocess.run(['tiled','--export-map','json','attic04.tmx','attic04.json'],env={'QT_QPA_PLATFORM':'offscreen','PATH':'/usr/bin:/bin'},check=True)
print('ok')
