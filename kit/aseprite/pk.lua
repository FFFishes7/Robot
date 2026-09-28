-- pk.lua : thin helpers over Aseprite's own drawing tools (useTool / MaskContent / selection clipping)
local pk = {}
local DIR = "/workspace/robot2d/kit/aseprite/"
pk.P = dofile(DIR.."palette.lua")
function pk.C(h)
  if type(h)=="string" and pk.P[h] then h = pk.P[h] end
  return Color{r=tonumber(h:sub(2,3),16), g=tonumber(h:sub(4,5),16), b=tonumber(h:sub(6,7),16), a=255}
end
pk.T = {ox=0, oy=0, a=0, sx=1, sy=1}
function pk.setT(ox,oy,a,sx,sy) pk.T={ox=ox,oy=oy,a=a or 0,sx=sx or 1,sy=sy or 1} end
local function tp(x,y)
  local T=pk.T; local ca,sa=math.cos(T.a),math.sin(T.a)
  local X,Y=x*T.sx,y*T.sy
  return Point(math.floor(T.ox+X*ca-Y*sa+0.5), math.floor(T.oy+X*sa+Y*ca+0.5))
end
pk.tp = tp
function pk.target(spr, layer, frame) pk.spr=spr; pk.layer=layer; pk.frame=frame or spr.frames[1]; app.activeSprite=spr; app.activeLayer=layer; app.activeFrame=pk.frame end
local function tool(name, pts, col)
  app.useTool{tool=name, color=pk.C(col), points=pts, layer=pk.layer, frame=pk.frame, brush=Brush(1), ink=Ink.SIMPLE, opacity=255}
end
function pk.poly(pts, col) local P={} for i,p in ipairs(pts) do P[i]=tp(p[1],p[2]) end; P[#P+1]=P[1]; tool("contour", P, col) end
function pk.rect(x0,y0,x1,y1,col)
  if pk.T.a==0 and pk.T.sx==1 and pk.T.sy==1 then tool("filled_rectangle",{tp(x0,y0),tp(x1,y1)},col)
  else pk.poly({{x0,y0},{x1+0.99,y0},{x1+0.99,y1+0.99},{x0,y1+0.99}},col) end
end
function pk.ell(cx,cy,rx,ry,col)
  if pk.T.a==0 then tool("filled_ellipse",{tp(cx-rx,cy-ry),tp(cx+rx,cy+ry)},col)
  else local P={} for i=0,23 do local t=i/24*2*math.pi; P[#P+1]={cx+0.5+rx*math.cos(t), cy+0.5+ry*math.sin(t)} end; pk.poly(P,col) end
end
function pk.rrect(x0,y0,x1,y1,r,col)
  do
    local P={}; local cs={{x1+1-r,y0+r,-90},{x1+1-r,y1+1-r,0},{x0+r,y1+1-r,90},{x0+r,y0+r,180}}
    for _,c in ipairs(cs) do for k=0,4 do local t=math.rad(c[3]+k*22.5); P[#P+1]={c[1]+r*math.cos(t),c[2]+r*math.sin(t)} end end
    pk.poly(P,col)
  end
end
function pk.line(x0,y0,x1,y1,col) tool("line",{tp(x0,y0),tp(x1,y1)},col) end
function pk.px(x,y,col) tool("pencil",{tp(x,y)},col) end
-- clip: Aseprite selection from layer content (MaskContent) + a hard alpha guard restored on unclip
function pk.clip()
  app.command.MaskContent()
  local cel=pk.layer:cel(pk.frame); pk._clip={img=cel.image:clone(), pos=cel.position}
end
function pk.unclip()
  app.command.DeselectMask()
  if not pk._clip then return end
  local cel=pk.layer:cel(pk.frame); local img=cel.image:clone(); local pos=cel.position
  local g=pk._clip; local pc=app.pixelColor
  for y=0,img.height-1 do for x=0,img.width-1 do
    local gx,gy=x+pos.x-g.pos.x, y+pos.y-g.pos.y
    local inside = gx>=0 and gy>=0 and gx<g.img.width and gy<g.img.height and pc.rgbaA(g.img:getPixel(gx,gy))>0
    if not inside then img:drawPixel(x,y,0) end
  end end
  cel.image=img; cel.position=pos; pk._clip=nil
end
-- self-coloured 1px outline from the layer mask: every transparent pixel touching the shape takes the
-- outline colour of the material it touches (dark variant; lighter variant on the lit top/left side).
pk.OUT = {}
function pk.material(list, dark, lit) for _,n in ipairs(list) do local c=pk.C(n); pk.OUT[c.rgbaPixel]={pk.C(dark).rgbaPixel, pk.C(lit or dark).rgbaPixel} end end
function pk.selfoutline(cel, defaultDark)
  local img=cel.image:clone(); local pad=1
  local W,H=img.width+2*pad,img.height+2*pad
  local big=Image(W,H,ColorMode.RGB); big:drawImage(img, Point(pad,pad))
  local out=big:clone()
  local pc=app.pixelColor
  for y=0,H-1 do for x=0,W-1 do
    if pc.rgbaA(big:getPixel(x,y))==0 then
      local best=nil; local lit=false
      for _,d in ipairs({{1,0,true},{0,1,true},{-1,0,false},{0,-1,false}}) do
        local nx,ny=x+d[1],y+d[2]
        if nx>=0 and ny>=0 and nx<W and ny<H then
          local v=big:getPixel(nx,ny)
          if pc.rgbaA(v)>0 and not best then best=v; lit=d[3] end
        end
      end
      if best then
        local m=pk.OUT[best]; local col
        if m then col = lit and m[2] or m[1] else col=pk.C(defaultDark).rgbaPixel end
        out:drawPixel(x,y,col)
      end
    end
  end end
  cel.image=out; cel.position=Point(cel.position.x-pad, cel.position.y-pad)
end
function pk.newlayer(spr,name) local l=spr:newLayer(); l.name=name; spr:newCel(l, spr.frames[1]); pk.target(spr,l); return l end
return pk
