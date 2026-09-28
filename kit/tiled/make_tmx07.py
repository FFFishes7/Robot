# v06 map: image layers from Aseprite exports + a "lights" object layer the Godot composer reads.
import glob,os,subprocess,sys
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.dirname(HERE)); from paths import ROOT
OX,OY=56,26    # v06 world offset (room grown to 448x288)
def poly(id,name,pts,props=None):
    pts=[(x+OX,y+OY) for x,y in pts]
    x0,y0=pts[0]; s=' '.join(f'{x-x0},{y-y0}' for x,y in pts)
    pr=''.join(f'<property name="{k}" type="float" value="{v}"/>' for k,v in (props or {}).items())
    pr=f'<properties>{pr}</properties>' if pr else ''
    return f'<object id="{id}" name="{name}" x="{x0}" y="{y0}">{pr}<polygon points="{s}"/></object>'
def ell(id,name,cx,cy,rx,ry,v):
    cx+=OX; cy+=OY
    return f'<object id="{id}" name="{name}" x="{cx-rx}" y="{cy-ry}" width="{2*rx}" height="{2*ry}"><properties><property name="intensity" type="float" value="{v}"/></properties><ellipse/></object>'
objs=[
 poly(1,'pool_1',[(84,74),(126,74),(84,174),(38,174)],{'intensity':0.55}),
 poly(2,'pool_2',[(228,74),(270,74),(228,174),(182,174)],{'intensity':0.55}),
 poly(3,'shaft_1',[(92,30),(124,30),(84,174),(38,174)]),
 poly(4,'shaft_2',[(236,30),(268,30),(228,174),(182,174)]),
 ell(5,'lamp',315,72,52,36,0.5),
 ell(6,'lamp_core',315,70,18,12,0.35),
 ell(7,'win_glow_1',108,52,40,26,0.3),
 ell(8,'win_glow_2',252,52,40,26,0.3),
 ell(9,'robot_glow',236,72,10,7,0.10),
 ell(11,'candle',91,93,16,12,0.22),
 ell(12,'floorlamp',366,146,44,30,0.42),
 ell(13,'floorlamp_core',366,134,16,10,0.3),
 ell(14,'radio',-26,98,10,7,0.12),
 ell(29,'alarm_glow',206,59,16,11,0.3),
 ell(15,'string_0',-2,-6,28,11,0.11),
 ell(16,'string_1',60,-6,28,11,0.11),
 ell(17,'string_2',124,-6,28,11,0.11),
 ell(18,'string_3',188,-6,28,11,0.11),
 ell(19,'string_4',252,-6,28,11,0.11),
 ell(20,'string_5',316,-6,28,11,0.11),
 ell(21,'string_6',380,-6,28,11,0.11),
 f'<object id="10" name="robot" x="292" y="106"><point/></object>',
]
layers=['albedo07','emit_win07','emit_lamps07','alarm_idle07']
il=''.join(f'<imagelayer id="{i+1}" name="{n}"><image source="../v07/{n}.png" width="448" height="288"/></imagelayer>' for i,n in enumerate(layers))
tmx=f'''<?xml version="1.0" encoding="UTF-8"?>
<map version="1.10" tiledversion="1.11.0" orientation="orthogonal" renderorder="right-down" width="28" height="16" tilewidth="16" tileheight="16" infinite="0" nextlayerid="7" nextobjectid="31">
{il}<objectgroup id="6" name="lights">{''.join(objs)}</objectgroup>
</map>'''
open(os.path.join(HERE,'attic07.tmx'),'w').write(tmx)
TILED=os.environ.get('TILED') or (glob.glob(ROOT+'tools/tiled/**/tiled.exe',recursive=True)+['tiled'])[0]
env=dict(os.environ,QT_QPA_PLATFORM='offscreen') if sys.platform.startswith('linux') else None
subprocess.run([TILED,'--export-map','json','attic07.tmx','attic07.json'],cwd=HERE,env=env,check=True)
print('ok')
