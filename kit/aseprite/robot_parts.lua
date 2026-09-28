-- Builds robot_parts.aseprite: one layer per part on a 128x128 canvas, part pivot at (64,64).
local pk = dofile("/workspace/robot2d/kit/aseprite/pk.lua")
local OUTDIR = "/workspace/robot2d/kit/sprites/"
local spr = Sprite(128,128,ColorMode.RGB)
spr:setPalette(Palette{fromFile="/workspace/robot2d/kit/palette/attic.gpl"})
local PX,PY = 64,64
pk.material({"rw1","rw2","rw3","rw4"},"rw0","rw1")
pk.material({"rp1","rp2","rp3","rp4","rp5"},"rp0","rp1")
pk.material({"s0","s1","s2","s3"},"rw1","rw1")
pk.material({"e_gold","e_gold2"},"rp1","rp1")
local anchors = {}
local function part(name) local l=pk.newlayer(spr,name); pk.setT(PX,PY,0,1,1); return l end
local function done(l, dark) pk.unclip(); pk.selfoutline(l:cel(1), dark or "ink") end

----------------------------------------------------------------- HEAD
-- view: "front" | "34" ; w,h = head size ; ang = tilt radians
local function head(name, w, h, ang, view)
  local l=part(name); pk.setT(PX,PY,ang or 0,1,1)
  local x0,x1,y0,y1 = -math.floor(w/2), math.floor(w/2)-1, -h, -1
  local fx0 = x0
  local fx1 = x1
  if view=="34" then fx0 = x0+8 end
  if view=="34L" then fx1 = x1-8 end
  -- ear bolt (behind shell, left side)
  if view=="34" then
    pk.ell(x0+3,y0+h*0.52,3,4.5,"rp3")
  elseif view=="34L" then
    pk.ell(x1-3,y0+h*0.52,3,4.5,"rp2")
  else
    pk.rrect(x0-3,y0+11,x0+1,y0+h-10,1,"rp3"); pk.rect(x0-3,y0+11,x0-2,y0+17,"rp4"); pk.rect(x0-2,y0+15,x0-1,y0+19,"#6a4a18")
  end
  pk.rrect(x0,y0,x1,y1,4,"rw3")
  pk.clip()
    pk.rect(x0,y0,x1,y0+5,"rw4")                 -- lit top face
    if view=="34" then
      pk.rect(x0,y0+6,fx0-1,y1,"rw4")          -- lit left side panel
      pk.rect(x0,y1-8,fx0-1,y1,"rw3"); pk.rect(x0,y1-3,fx0-2,y1,"rw2")
      pk.rect(fx0,y0+6,fx0,y1,"rw2")            -- panel edge (form change)
      pk.ell(x0+3,y0+h*0.52,2.5,3.5,"rp3"); pk.rect(x0+2,y0+h*0.52-1,x0+3,y0+h*0.52+2,"rp1"); pk.px(x0+2,y0+h*0.52-3,"rp5")
    elseif view=="34L" then
      pk.rect(fx1+1,y0+6,x1,y1,"rw2"); pk.rect(fx1+1,y1-6,x1,y1,"rw1")
      pk.rect(fx1,y0+6,fx1,y1,"rw4")
      pk.rect(x0,y0+6,x0+3,y1-9,"rw4")
      pk.ell(x1-3,y0+h*0.52,2.5,3.5,"rp2"); pk.rect(x1-3,y0+h*0.52-1,x1-2,y0+h*0.52+2,"rp1")
    else
      pk.rect(x0,y0+6,x0+6,y1-9,"rw4")          -- lit left bevel
      pk.rect(x0,y1-8,x0+4,y1,"rw2"); pk.rect(x0,y1-4,x0+2,y1,"rw1")
    end
    pk.rect(fx0+1,y0+6,x1,y0+6,"rw3")
    pk.rect(x0,y1-2,x1,y1,"rw2")                 -- underside
    if view~="34L" then pk.rect(x1-2,y0+6,x1,y1,"rw2"); pk.rect(x1-2,y1-2,x1,y1,"rw1") end
  pk.unclip()
  -- screen: dark bevel top/left, bright lip bottom/right
  local sx0,sx1,sy0,sy1 = fx0+ (view=="34" and 4 or 9), fx1-(view=="34L" and 3 or 5), y0+8, y1-6
  if view=="34L" then sx0=fx0+5 end
  pk.rect(sx0-1,sy0-1,sx1,sy1,"rw1")
  pk.rect(sx0,sy0,sx1+1,sy1+1,"rw4")
  pk.rrect(sx0,sy0,sx1,sy1,1,"s1")
  pk.px(sx0+1,sy0+1,"s3"); pk.px(sx0+2,sy0+1,"s2"); pk.px(sx0+1,sy0+2,"s2")
  pk.line(sx1-3,sy1-1,sx1-1,sy1-1,"s0")
  -- antenna base + stalk
  pk.rect(-4,y0-1,2,y0-1,"#f6d88a"); pk.rect(1,y0-1,2,y0-1,"e_gold2")
  pk.line(-1,y0-2,-1,y0-8,"e_gold2"); pk.line(-1,y0-6,-1,y0-8,"e_gold")
  done(l,"rw0")
  anchors[name] = {pivot={PX,PY}, screen={sx0,sy0,sx1,sy1}, ang=ang or 0, bulb={-1,y0-11}, view=view or "front"}
  return l
end
local HW,HH = 46,34
head("head_front", HW,HH, 0, "front")
head("head_squash",HW+4,HH-4,0,"front")
head("head_stretch",HW-4,HH+3,0,"front")
head("head_34",    HW,HH, 0, "34")
head("head_34L",   HW,HH, 0, "34L")
head("head_tilt",  HW,HH, math.rad(-11), "front")
head("head_tilt_r",HW,HH, math.rad(9), "front")

----------------------------------------------------------------- FACES (emissive layer, drawn in screen space)
local function eyering(cx,cy,rx,ry)
  pk.ell(cx,cy,rx+1,ry+1,"e_ring")
end
local function oval(cx,cy,rx,ry,bot)
  eyering(cx,cy,rx,ry); pk.ell(cx,cy,rx,ry,"e_hi")
  pk.clip(); pk.rect(cx-rx,cy+ry-(bot or 2)+1,cx+rx,cy+ry,"e_low"); pk.unclip()
end
local EXPR = {}
EXPR.neutral=function(a,b,c,d,W,H) local ey=math.floor(b+H*0.28)
  for _,ex in ipairs({a+W*0.3,a+W*0.7}) do ex=math.floor(ex) oval(ex-2,ey+1,2.5,3.5); pk.px(ex-3,ey,"e_core") end end
EXPR.happy=function(a,b,c,d,W,H) local ey=math.floor(b+H*0.45)
  for _,ex in ipairs({a+W*0.3,a+W*0.7}) do ex=math.floor(ex)
    pk.line(ex-4,ey+1,ex-2,ey-2,"e_ring"); pk.line(ex-2,ey-2,ex,ey+1,"e_ring")
    pk.line(ex-3,ey+1,ex-2,ey-1,"e_hi"); pk.line(ex-2,ey-1,ex-1,ey+1,"e_hi"); pk.px(ex-4,ey+1,"e_hi"); pk.px(ex,ey+1,"e_hi"); pk.px(ex-2,ey-2,"e_core") end
  local mx=math.floor(a+W*0.5); pk.line(mx-3,ey+5,mx-2,ey+6,"e_low"); pk.line(mx-1,ey+6,mx+1,ey+6,"e_low"); pk.line(mx+2,ey+6,mx+2,ey+5,"e_low") end
EXPR.curious=function(a,b,c,d,W,H) local ey=math.floor(b+H*0.3)
  local e1,e2=math.floor(a+W*0.3),math.floor(a+W*0.72)
  oval(e1-2,ey,2,3); pk.px(e1-1,ey+1,"e_core")
  oval(e2-2,ey+1,2,2,1); pk.px(e2-1,ey+2,"e_core")
  pk.line(e2-5,ey-3,e2,ey-4,"e_low") end
EXPR.surprised=function(a,b,c,d,W,H) local ey=math.floor(b+H*0.26)
  for _,ex in ipairs({a+W*0.3,a+W*0.7}) do ex=math.floor(ex) oval(ex-2,ey,3,3.5,2); pk.px(ex-3,ey-1,"e_core") end
  local mx=math.floor(a+W*0.5); pk.ell(mx-1,ey+7,1.2,1.5,"e_low") end
EXPR.sleepy=function(a,b,c,d,W,H) local ey=math.floor(b+H*0.5)
  for _,ex in ipairs({a+W*0.3,a+W*0.7}) do ex=math.floor(ex) pk.line(ex-4,ey,ex,ey,"e_hi"); pk.line(ex-4,ey+1,ex,ey+1,"e_low"); pk.line(ex-4,ey-1,ex,ey-1,"e_ring") end
  local zx,zy=c-4,b+2; pk.line(zx,zy,zx+2,zy,"e_low"); pk.px(zx+1,zy+1,"e_low"); pk.line(zx,zy+2,zx+2,zy+2,"e_low") end
EXPR.annoyed=function(a,b,c,d,W,H) local ey=math.floor(b+H*0.38)
  for i,ex in ipairs({a+W*0.3,a+W*0.7}) do ex=math.floor(ex) oval(ex-2,ey,2,2,1)
    local s=(i==1) and 1 or -1
    pk.clip(); pk.rect(ex-5,ey-4,ex+1,ey-1,"s1"); pk.unclip()
    pk.line(ex-4,ey-2+(s>0 and -1 or 1),ex,ey-2+(s>0 and 1 or -1),"e_ring") end
  local mx=math.floor(a+W*0.5); pk.line(mx-2,ey+6,mx+1,ey+6,"e_low") end
EXPR.sparkle=function(a,b,c,d,W,H) local ey=math.floor(b+H*0.4)
  for _,ex in ipairs({a+W*0.3,a+W*0.7}) do ex=math.floor(ex)-2
    for _,q in ipairs({{-2,-2},{2,-2},{-2,2},{2,2},{-1,-3},{1,-3},{-3,-1},{3,-1},{-3,1},{3,1},{-1,3},{1,3}}) do pk.px(ex+q[1],ey+q[2],"e_ring") end
    pk.line(ex,ey-4,ex,ey+4,"e_gold2"); pk.line(ex-4,ey,ex+4,ey,"e_gold2")
    pk.line(ex,ey-3,ex,ey+3,"e_gold"); pk.line(ex-3,ey,ex+3,ey,"e_gold")
    pk.rect(ex-1,ey-1,ex+1,ey+1,"e_gold"); pk.line(ex,ey-1,ex,ey+1,"e_hi"); pk.line(ex-1,ey,ex+1,ey,"e_hi"); pk.px(ex,ey,"e_core")
    -- dark warm halo pixels around the star (glow drawn on the grid, like the refs)
    for _,q in ipairs({{-2,-2},{2,-2},{-2,2},{2,2},{-1,-3},{1,-3},{-3,-1},{3,-1},{-3,1},{3,1},{-1,3},{1,3},{-4,-4},{4,-4},{-4,4},{4,4},{0,-5},{-5,0},{5,0},{0,5}}) do
      pk.px(ex+q[1],ey+q[2],(math.abs(q[1])+math.abs(q[2])>=5) and "e_ring2" or "e_ring") end end end
local order={"neutral","happy","curious","surprised","sleepy","annoyed","sparkle"}
for _,hn in ipairs({"head_front","head_squash","head_stretch","head_34","head_34L","head_tilt","head_tilt_r"}) do
  local A=anchors[hn]; local s=A.screen
  for _,e in ipairs(order) do
    local l=part("face_"..e.."_"..hn); pk.setT(PX,PY,A.ang,1,1)
    local a,b,c,d=s[1],s[2],s[3],s[4]
    EXPR[e](a+1,b+1,c-1,d-1,c-a-1,d-b-1)
    anchors["face_"..e.."_"..hn]={pivot={PX,PY}, emissive=true}
  end
end
-- antenna bulb (emissive)
local l=part("bulb"); pk.setT(PX,PY,0,1,1)
pk.rect(-2,-2,2,2,"rp2"); pk.rect(-1,-2,1,2,"l_sun1"); pk.rect(-2,-1,2,1,"l_sun1"); pk.rect(-1,-1,1,1,"rp5"); pk.px(0,0,"e_core")
pk.px(-2,-2,"rp1"); pk.px(2,2,"rp1"); pk.px(2,-2,"rp4"); pk.px(-2,2,"rp1")
anchors.bulb={pivot={PX,PY},emissive=true}

----------------------------------------------------------------- BODY (pivot = hip centre)
l=part("body")
pk.rrect(-14,-21,13,0,8,"rp2")
pk.clip()
  pk.ell(-3,-12,14,10,"rp3")
  pk.ell(-7,-15,7,5,"rp4"); pk.ell(-8,-16,3,2,"rp5")
  pk.rect(-14,-1,13,0,"rp1"); pk.rect(11,-12,13,0,"rp1")
pk.unclip()
pk.ell(4,-10,6,5,"rw3")
pk.clip(); pk.ell(2,-12,4,3,"rw4"); pk.rect(-2,-6,10,-5,"rw2"); pk.rect(9,-13,10,-5,"rw2"); pk.unclip()
pk.px(4,-12,"#e46e4a"); pk.px(3,-11,"#e46e4a"); pk.px(5,-11,"#e46e4a"); pk.px(4,-10,"#e46e4a"); pk.px(4,-11,"rw4")
pk.rect(-8,-6,-7,-5,"#9a7ae6"); pk.px(-7,-5,"#6a4ab8"); pk.px(-8,-6,"#c4b0ff")
done(l,"rp0")
anchors.body={pivot={PX,PY}, neck={0,-19}, shoulderL={-13,-14}, shoulderR={13,-14}, hip={0,0}}

----------------------------------------------------------------- ARMS (left arm; right = horizontal flip). pivot = shoulder
local ARM = {down={-3,10}, wave={-10,-9}, raised={-3,-15}, reach={-12,0}, back={-6,8}, cheer={-9,-13}}
for n,h in pairs(ARM) do
  l=part("arm_"..n)
  local hx,hy=h[1],h[2]
  for k=0,5 do local t=k/10; local cx,cy=hx*t,hy*t
    pk.ell(cx-2,cy-2,2.5,2.5,"rp3") end
  pk.clip(); for k=0,5 do local t=k/10; pk.px(math.floor(hx*t)-3,math.floor(hy*t)-3,"rp4") end; pk.unclip()
  pk.ell(hx-4,hy-3,4.5,4,"rw3")
  pk.clip(); pk.ell(hx-5,hy-4,3,2.5,"rw4"); pk.rect(hx-5,hy+1,hx+1,hy+2,"rw2"); pk.px(hx-4,hy-4,"rw4"); pk.unclip()
  done(l,"rp0")
  anchors["arm_"..n]={pivot={PX,PY}}
end

----------------------------------------------------------------- LEGS (pair). pivot = hip centre
local function leg(x,len,fdx,fdy,toeDown)
  pk.rrect(x-3,-2,x+3,len,2,"rp3")
  pk.clip(); pk.rect(x-3,-2,x-2,len,"rp4"); pk.rect(x+2,-2,x+3,len,"rp2"); pk.unclip()
  local fx,fy=x+fdx,len+fdy
  if toeDown then pk.rrect(fx-3,fy-2,fx+3,fy+3,2,"rp4")
  else pk.rrect(fx-5,fy-2,fx+5,fy+2,2,"rp4") end
  pk.clip()
  if toeDown then pk.rect(fx-3,fy+2,fx+3,fy+3,"rp2"); pk.rect(fx+2,fy-2,fx+3,fy+3,"rp3")
  else pk.rect(fx-5,fy+1,fx+5,fy+2,"rp2"); pk.rect(fx+3,fy-2,fx+5,fy+2,"rp3"); pk.rect(fx-4,fy-2,fx-2,fy-2,"rp5") end
  pk.unclip()
end
local LEGS = {
  stand ={{-6,8,-1,1,false},{6,8,1,1,false}},
  step  ={{-7,7,-3,0,false},{6,9,2,1,false}},
  crouch={{-8,3,-2,1,false},{8,3,2,1,false}},
  jump  ={{-4,11,0,1,true},{4,11,0,1,true}},
  tuck  ={{-6,4,1,0,true},{6,3,-1,0,true}},
}
for n,L in pairs(LEGS) do
  l=part("legs_"..n)
  for _,g in ipairs(L) do leg(g[1],g[2],g[3],g[4],g[5]) end
  done(l,"rp0")
  anchors["legs_"..n]={pivot={PX,PY}}
end
-- drop the default empty layer
spr:deleteLayer(spr.layers[1])
spr:saveAs(OUTDIR.."robot_parts.aseprite")
-- anchors json
local f=io.open(OUTDIR.."robot_parts_anchors.json","w")
local function enc(v)
  if type(v)=="table" then
    if #v>0 then local t={} for i,x in ipairs(v) do t[i]=enc(x) end return "["..table.concat(t,",").."]" end
    local t={} for k,x in pairs(v) do t[#t+1]='"'..k..'":'..enc(x) end return "{"..table.concat(t,",").."}"
  elseif type(v)=="string" then return '"'..v..'"' elseif type(v)=="boolean" then return tostring(v) else return tostring(v) end
end
f:write(enc(anchors)); f:close()
print("robot parts ok: "..#spr.layers.." layers")
