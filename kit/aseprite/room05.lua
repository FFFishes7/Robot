-- room05.lua : Stardew-density 3/4 interior at dusk (To the Moon mood). 384x216 native.
-- Layers: bg (void, walls, floor, rug), shadows (1-colour, drawn semi-transparent in engine), props, emit, robot, robot_emit
local pk = dofile("/workspace/robot2d/kit/aseprite/pk.lua")
local OUT = "/workspace/robot2d/kit/v05/"
local pc = app.pixelColor
local function rgba(h) local c=pk.C(h); return pc.rgba(c.red,c.green,c.blue,255) end
local function hsh(a,b,c)
  local h=0
  for _,v in ipairs({a or 0,b or 0,c or 0}) do h=((h*1000003) ~ (math.floor(v) & 0xffffffff)) & 0xffffffff end
  h = h ~ (h>>13); h=(h*0x5bd1e995) & 0xffffffff; h = h ~ (h>>15)
  return (h & 0xffff)/65535.0
end
local W,H=384,216
local spr=Sprite(W,H,ColorMode.RGB)
pk.setT(0,0,0,1,1)
-- extra named colours for this room
local X={ void="#120a10", ceil="#2a1720", wp0="#3e5048", wp1="#4c6256", wp2="#5c7462", wp3="#6f8870", wp_m="#86a07e",
  wd0="#2e1410", wd1="#4e2418", wd2="#6e3620", wd3="#8e4c2a", wd4="#ad6436", wd5="#c9824a", wd6="#e0a462", wd7="#f4c88a",
  fl0="#3a1c12", fl1="#5a2e1a", fl2="#7a4426", fl3="#955a32", fl4="#ad6e3e", fl5="#c4864c",
  cur0="#2a0c1c", cur1="#4e1628", cur2="#762636", cur3="#9c3c3e", cur4="#c2604a",
  sk0="#3a2e5e", sk1="#6a4a7a", sk2="#b0607a", sk3="#e8866a", sk4="#f8b870", sk5="#fde0a0",
  rug0="#4a2230", rug1="#6e3440", rug2="#8e4a50", rug3="#b0685e", rugc="#e8c8a0", rugc2="#c09878", rugd="#823f4a",
  gl0="#2a3a3a",
  leaf0="#142630", leaf1="#1c4638", leaf2="#336a3a", leaf3="#5a923c", leaf4="#98bc4a", leaf5="#d0dc78",
  pot0="#40161a", pot1="#702c22", pot2="#9e4a2c", pot3="#c46c40", pot4="#e2945c", soil="#2a1a14",
  brass0="#40240e", brass1="#76501c", brass2="#ab842c", brass3="#dab84a", brass4="#fbeb9c",
  paper="#f4e6c8", paper2="#d8c4a0", paper3="#a88a68", lamp0="#8a4a2a", lamp1="#f0b060", lamp2="#ffe0a0", lamp3="#fff6d8",
  box0="#43261c", box1="#6a4026", box2="#8e5e32", box3="#b28248", box4="#d2a664", box5="#ecca84",
  r0="#5c1e2a", r1="#9a3c34", r2="#c05a44", b0="#243450", b1="#3c6282", b2="#5a86a2", g0="#2a4430", g1="#4e7a3e", g2="#76a050",
  y0="#7c5a26", y1="#c09a3e", y2="#e2c262", p0="#3e2448", p1="#744476", p2="#9a6490", t0="#20404a", t1="#3c7a74", t2="#62a08c",
  vn0="#140e18", vn1="#2a2234", vn2="#4a4058",
  tr0="#18262a", tr1="#27403f", tr2="#3a5c58", tr3="#56806f",
  mu0="#5a3418", mu1="#8a5a24", mu2="#b8842e", mu3="#dcac44", mu4="#f2d072",
  nv0="#141a38", nv1="#22305e", nv2="#34508a", nv3="#5a7cb0" }
for k,v in pairs(X) do pk.P[k]=v end
pk.material({"wd1","wd2","wd3","wd4","wd5","wd6","wd7","fl2","fl3","fl4","fl5"},"wd0","wd0")
pk.material({"box1","box2","box3","box4","box5"},"box0","box0")
pk.material({"cur1","cur2","cur3","cur4"},"cur0","cur0")
pk.material({"leaf1","leaf2","leaf3","leaf4","leaf5"},"leaf0","leaf0")
pk.material({"pot1","pot2","pot3","pot4","soil"},"pot0","pot0")
pk.material({"brass1","brass2","brass3","brass4"},"brass0","brass0")
pk.material({"rug1","rug2","rug3","rugc","rugc2","rugd"},"rug0","rug0")
pk.material({"paper","paper2","paper3"},"wd1","wd1")
pk.material({"r1","r2"},"r0","r0"); pk.material({"b1","b2"},"b0","b0"); pk.material({"g1","g2"},"g0","g0")
pk.material({"y1","y2"},"y0","y0"); pk.material({"p1","p2"},"p0","p0"); pk.material({"t1","t2"},"t0","t0")
pk.material({"vn1","vn2"},"vn0","vn0"); pk.material({"tr1","tr2","tr3"},"tr0","tr0")
pk.material({"mu1","mu2","mu3","mu4"},"mu0","mu0"); pk.material({"nv1","nv2","nv3"},"nv0","nv0")
pk.material({"wp1","wp2","wp3","wp_m"},"wp0","wp0")
local function layer(n) return pk.newlayer(spr,n) end
local function fin(l,d) pk.unclip(); pk.selfoutline(l:cel(1), d or "wd0") end
local RX0,RX1=40,343       -- room interior x
local WY0,WY1=24,71        -- back wall
local FY0,FY1=72,199       -- floor
------------------------------------------------------------------ BG
local bg=layer("bg")
local img=Image(W,H,ColorMode.RGB)
local function P(x,y,c) img:drawPixel(x,y,rgba(c)) end
for y=0,H-1 do for x=0,W-1 do P(x,y,"void") end end
-- wallpaper: sage, 8px vertical stripe pair + small diamond motif every 16px
for y=WY0,WY1 do for x=RX0,RX1 do
  local c="wp1"; local sx=(x-RX0)%16
  if sx==0 or sx==8 then c="wp0" elseif sx==1 then c="wp2" end
  local my=(y-WY0)%12
  if (sx==4 or sx==12) and my==5 then c="wp_m" end
  if (sx==4 or sx==12) and (my==4 or my==6) then c="wp2" end
  if (sx==3 or sx==5 or sx==11 or sx==13) and my==5 then c="wp2" end
  P(x,y,c)
end end
-- crown moulding + ceiling edge
for x=RX0-8,RX1+8 do P(x,WY0-6,"wd0"); for y=WY0-5,WY0-3 do P(x,y,"ceil") end; P(x,WY0-2,"wd2"); P(x,WY0-1,"wd1") end
-- wainscot (vertical boards) y 50..71 with top rail
for y=50,71 do for x=RX0,RX1 do
  local c="wd3"; local bx=(x-RX0)%10
  if bx==0 then c="wd1" elseif bx==1 then c="wd4" elseif bx==9 then c="wd2" end
  if y>=69 then c="wd1" end
  P(x,y,c)
end end
for x=RX0,RX1 do P(x,48,"wd1"); P(x,49,"wd5"); P(x,50,"wd4") end
-- side walls (thin dark strips with lit top trim)
for y=WY0-6,FY1+8 do for x=RX0-8,RX0-1 do P(x,y, x==RX0-1 and "wd1" or (x==RX0-8 and "wd0" or "ceil")) end
  for x=RX1+1,RX1+8 do P(x,y, x==RX1+1 and "wd1" or (x==RX1+8 and "wd0" or "ceil")) end end
-- floor: horizontal planks, 5px courses (4 board + 1 seam), staggered lengths
for y=FY0,FY1 do
  local course=math.floor((y-FY0)/5); local yy=(y-FY0)%5
  for x=RX0,RX1 do
    local off=math.floor(hsh(course,1)*40)
    local L=32+math.floor(hsh(course,2)*3)*8
    local bi=math.floor((x+off)/L); local bxx=(x+off)%L
    local tone=({"fl3","fl3","fl4","fl3","fl3","fl3","fl4","fl2"})[1+math.floor(hsh(course,bi)*8)]
    local c=tone
    if yy==4 then c="fl1" elseif yy==0 and tone~="fl2" then c=(tone=="fl4") and "fl5" or "fl4" end
    if bxx==0 then c="fl1" end
    -- sparse grain: 1px darker dashes of 3-6px inside boards
    local g=hsh(course,bi,math.floor(bxx/6))
    if yy==2 and g<0.1 and bxx%6<4 then c=(tone=="fl2") and "fl1" or "fl2" end
    P(x,y,c)
  end
end
-- floor/wall contact shadow line
for x=RX0,RX1 do P(x,FY0,"fl1") end
-- bottom wall edge (front)
for y=FY1+1,FY1+8 do for x=RX0-8,RX1+8 do P(x,y, y==FY1+1 and "wd2" or (y==FY1+2 and "wd4" or (y==FY1+8 and "wd0" or "wd1"))) end end
-- rug: border band with repeating diamonds, dotted field, octagonal medallion, knotted fringe
local R0x,R1x,R0y,R1y=124,267,122,181
local cx,cy=(R0x+R1x)/2,(R0y+R1y)/2
for y=R0y,R1y do for x=R0x,R1x do
  local dx=math.min(x-R0x,R1x-x); local dy=math.min(y-R0y,R1y-y); local d=math.min(dx,dy)
  local c
  if d==0 then c="rug0" elseif d==1 then c=((x+y)%2==0) and "rugc2" or "rugc" elseif d==2 then c="rugc" elseif d==3 then c="rug0"
  elseif d<=8 then
    c="rug1"; local a=(dy<dx) and x or y; local p=(a-R0x)%10
    local m=math.abs(p-4.5)+math.abs(d-6)*1.2
    if m<0.6 then c="rugc" elseif m<1.6 then c="rugc2" elseif m<2.4 then c="rug3" elseif m<3.2 then c="rugd" end
  elseif d==9 then c="rug0" elseif d==10 then c="rugc2"
  else
    c="rug2"
    if (x-R0x)%8==4 and (y-R0y)%6==3 then c="rug3" end
    local ax,ay=math.abs(x-cx)/2.0,math.abs(y-cy)
    local md=math.max(ax,ay,(ax+ay)*0.74)
    if md<11 then c="rugd" end; if md<10 then c="rug3" end; if md<7.5 then c="rug1" end
    if md<6.5 then c="rugc2" end; if md<4 then c="rug3" end; if md<2 then c="rugc" end
    if md>=13 and md<14 then c="rugd" end
  end
  P(x,y,c)
end end
for y=R0y+2,R1y-2,2 do P(R0x-1,y,"rugc"); P(R0x-2,y,"rugc2"); P(R1x+1,y,"rugc"); P(R1x+2,y,"rugc2") end
bg:cel(1).image=img; bg:cel(1).position=Point(0,0)
------------------------------------------------------------------ helpers
local R,E,L,D=pk.rect,pk.ell,pk.line,pk.px
local function bevel(x0,y0,x1,y1,base,lit,dark) R(x0,y0,x1,y1,base); L(x0,y0,x1,y0,lit); L(x0,y0,x0,y1,lit); L(x0,y1,x1,y1,dark); L(x1,y0,x1,y1,dark) end
local function inset(x0,y0,x1,y1,base,lit,dark) R(x0,y0,x1,y1,base); L(x0,y0,x1,y0,dark); L(x0,y0,x0,y1,dark); L(x0,y1,x1,y1,lit); L(x1,y0,x1,y1,lit) end
local LX,LY=-0.6,-0.8   -- key light direction (from the windows, upper left)
local function leaf(cx,cy,ang,a,b,set)   -- set={edge,lit,shade,rib}
  local ca,sa=math.cos(math.rad(ang)),math.sin(math.rad(ang))
  local nx,ny=-sa,ca; local litv=(nx*LX+ny*LY)>0 and 1 or -1
  local r=math.ceil(math.max(a,b))+1
  for y=math.floor(cy-r),math.ceil(cy+r) do for x=math.floor(cx-r),math.ceil(cx+r) do
    local dx,dy=x-cx,y-cy; local u=dx*ca+dy*sa; local v=-dx*sa+dy*ca
    local bb=b*((u>0) and (1-0.6*(u/a)) or (1-0.15*(-u/a)))
    local q=(u/a)^2+(v/math.max(bb,0.4))^2
    if q<=1 then
      local lit=v*litv>0
      local c=lit and set[2] or set[3]
      if lit and q>0.5 then c=set[1] end
      if math.abs(v)<0.5 and u>-a*0.9 and u<a*0.6 then c=set[4] end
      D(x,y,c)
    end
  end end
end
local function tube(ax,ay,bx,by,ra,rb,bands)
  local vx,vy=bx-ax,by-ay; local len=math.sqrt(vx*vx+vy*vy); local ux,uy=vx/len,vy/len; local nx,ny=-uy,ux
  if ny>0 then nx,ny=-nx,-ny end
  local m=math.ceil(math.max(ra,rb))+1
  for y=math.floor(math.min(ay,by)-m),math.ceil(math.max(ay,by)+m) do for x=math.floor(math.min(ax,bx)-m),math.ceil(math.max(ax,bx)+m) do
    local t=((x-ax)*ux+(y-ay)*uy)/len; local d=(x-ax)*nx+(y-ay)*ny
    if t>=0 and t<=1 then local r=ra+(rb-ra)*t
      if math.abs(d)<=r then local f=d/r
        local c=(f>0.5) and "brass4" or (f>0.05) and "brass3" or (f>-0.5) and "brass2" or "brass1"
        for _,bt in ipairs(bands) do if math.abs(t-bt)<0.035 then c=(f>0.3) and "brass2" or "brass1" end end
        D(x,y,c)
      end end
  end end
end
local function star(x,y) D(x,y,"y2"); D(x-1,y,"y1"); D(x+1,y,"y1"); D(x,y-1,"y2"); D(x,y+1,"y0") end
------------------------------------------------------------------ SHADOWS (soft, drawn at ~38% alpha) + CONTACT (tight, ~60%)
local sh=layer("shadows"); local SH="#000000"
R(44,81,80,85,SH); E(79,83,3,2,SH)                 -- bookshelf
R(163,82,189,84,SH)                                -- clock
E(286,98,20,4,SH)                                  -- armchair
E(311,98,9,2.5,SH)                                 -- side table
E(332,98,9,2.5,SH)                                 -- plant
E(137,99,12,2.5,SH)                                -- telescope
R(42,196,84,199,SH); E(84,197,6,2,SH)              -- trunk
R(294,184,343,188,SH)                              -- cabinet
E(288,184,6,1.5,SH)                                -- sleeves
R(48,131,97,135,SH)                                -- desk
E(73,134,9,1.5,SH)                                 -- chair
E(258,99,9,2,SH)                                   -- basket
E(300,152,11,2.5,SH)                               -- book stack
E(92,169,13,2.5,SH)                                -- floor cushion
E(329,146,10,2.5,SH)                               -- globe
E(283,106,10,1.5,SH)                               -- slippers
E(158,115,9,1.5,SH)                                -- open book
R(83,76,126,78,SH)                                 -- window seat
E(162,177,7,1.2,SH)                                -- dustpan
local ct=layer("contact")
for _,p in ipairs({{126,98},{137,100},{147,98}}) do R(p[1]-1,p[2],p[1]+1,p[2],SH) end   -- tripod feet
R(49,132,52,132,SH); R(92,132,95,132,SH)           -- desk legs
R(66,134,68,134,SH); R(79,134,81,134,SH)           -- chair legs
R(266,98,270,98,SH); R(301,98,305,98,SH)           -- armchair feet
R(304,98,307,98,SH); R(316,98,319,98,SH)           -- side table legs
R(325,98,338,98,SH)                                -- pot
R(44,198,82,198,SH)                                -- trunk
R(297,186,301,186,SH); R(337,186,341,186,SH)       -- cabinet feet
R(292,151,308,151,SH)                              -- book stack
R(81,169,103,169,SH)                               -- cushion
R(250,99,266,99,SH)                                -- basket
R(323,147,335,147,SH)                              -- globe stand
R(44,86,79,86,SH)                                  -- bookshelf plinth
R(164,83,188,83,SH)                                -- clock plinth
R(296,185,342,185,SH)
------------------------------------------------------------------ PROPS
local l
-- WINDOWS: frame with lit top/left, sill with front face
local function window(x0)
  local l=layer("window_"..x0)
  R(x0-3,27,x0+34,58,"wd3"); L(x0-3,27,x0+34,27,"wd6"); L(x0-3,28,x0+34,28,"wd5"); L(x0-3,27,x0-3,58,"wd5"); L(x0+34,27,x0+34,58,"wd1")
  L(x0-2,29,x0-2,57,"wd4"); L(x0+33,29,x0+33,57,"wd2")
  R(x0-5,58,x0+36,62,"wd4"); L(x0-5,58,x0+36,58,"wd7"); L(x0-5,59,x0+36,59,"wd6"); L(x0-5,61,x0+36,61,"wd2"); L(x0-5,62,x0+36,62,"wd1")
  D(x0-5,58,"wd5"); D(x0+36,58,"wd5")
  fin(l)
  -- curtains: folded velvet with pinch at the brass tieback, flare below, hem
  local c=layer("curtain_"..x0)
  local folds={"cur3","cur4","cur3","cur2","cur1","cur2","cur3","cur2","cur1"}
  for s,side in ipairs({{x0-10,1},{x0+34,-1}}) do
    local xb=side[1]
    for y=26,64 do
      local w=9; local pinch=0
      if y>=40 and y<=48 then pinch=math.floor((4-math.abs(y-44))*0.9) end
      if y>48 then pinch=-math.min(2,math.floor((y-48)/6)) end
      local ww=w-math.max(pinch,0)
      for i=0,ww-1+math.max(-pinch,0) do
        local x = (side[2]==1) and (xb+i) or (xb+w-1-i)
        local f=folds[(i % #folds)+1]
        if y==64 then f="cur1" elseif y==63 then f=(i%3==0) and "cur2" or "cur3" end
        if side[2]==-1 then local j=#folds-(i % #folds); f=(y>=63) and f or folds[j] end
        D(x,y,f)
      end
    end
    local tx=(side[2]==1) and xb or xb+3
    R(tx,43,tx+5,45,"brass2"); L(tx,43,tx+5,43,"brass3"); L(tx,45,tx+5,45,"brass1"); local kx=(side[2]==1) and tx+5 or tx; D(kx,46,"brass2"); D(kx,47,"brass3")
  end
  R(x0-12,24,x0+45,25,"brass2"); L(x0-12,24,x0+45,24,"brass3"); D(x0-13,24,"brass3"); D(x0-13,25,"brass1"); D(x0+46,24,"brass3"); D(x0+46,25,"brass1")
  E(x0-13,24,1,1,"brass3"); E(x0+46,24,1,1,"brass3")
  fin(c,"cur0")
end
window(92); window(236)
-- BOOKSHELF: carcass with 3/4 top, recessed back, 4 shelves of two-tone books, plinth; small trailing plant + books on top
l=layer("bookshelf")
R(44,31,79,80,"wd2")
R(44,31,79,33,"wd5"); L(44,31,79,31,"wd6"); L(44,34,79,34,"wd3")
R(44,35,46,78,"wd4"); L(44,35,44,78,"wd5"); R(77,35,79,78,"wd1"); L(77,35,77,78,"wd2")
local comps={{36,45},{47,56},{58,67},{69,76}}
local bset={{"r1","r0","r2"},{"b1","b0","b2"},{"g1","g0","g2"},{"y1","y0","y2"},{"p1","p0","p2"},{"t1","t0","t2"}}
for ci,cp in ipairs(comps) do
  local y0,y1=cp[1],cp[2]
  R(47,y0,76,y1,"wd1"); L(47,y0,76,y0,"wd0"); L(47,y0,47,y1,"wd0")
  if ci<4 then R(46,y1+1,77,y1+1,"wd4"); L(46,y1+1,77,y1+1,"wd5") end
  local x=48
  while x<75 do
    local k=hsh(x,ci*7)
    if k<0.08 and x<70 then            -- small object: jar / globe / figurine
      E(x+2,y1-2,2,2,(ci%2==0) and "t1" or "y1"); D(x+1,y1-3,(ci%2==0) and "t2" or "y2"); x=x+6
    elseif k<0.16 and x<68 then        -- horizontal stack
      R(x,y1-1,x+5,y1,"r1"); R(x,y1-3,x+4,y1-2,"b1"); L(x,y1-3,x+4,y1-3,"b2"); L(x,y1-1,x+5,y1-1,"r2"); x=x+7
    else
      local w=2+math.floor(hsh(x,ci)*2); local h=(y1-y0-1)-math.floor(hsh(ci,x)*4)
      local s=bset[1+math.floor(hsh(x*3,ci)*6)]
      R(x,y1-h+1,x+w-1,y1,s[1]); L(x,y1-h+1,x,y1,s[3]); if w>2 then L(x+w-1,y1-h+1,x+w-1,y1,s[2]) end
      D(x+1,y1-h+3,"y2"); if w>2 then D(x+1,y1-2,"y2") end
      x=x+w
    end
  end
  if ci==2 then L(73,y1,76,y0+3,"r1"); L(74,y1,76,y0+5,"r2") end   -- leaning book
end
R(44,77,79,80,"wd3"); L(44,77,79,77,"wd5"); L(44,80,79,80,"wd1")
-- top: two lying books + trailing ivy in a small pot
R(62,28,74,30,"b1"); L(62,28,74,28,"b2"); R(63,26,72,27,"y1"); L(63,26,72,26,"y2"); L(74,28,74,30,"paper2")
R(49,26,55,30,"pot2"); L(49,26,55,26,"pot4"); L(49,27,55,27,"pot1"); L(55,28,55,30,"pot1"); L(50,28,50,30,"pot3")
for _,q in ipairs({{48,25,200,3,1.6,"b"},{53,24,280,3,1.6,"f"},{57,25,330,3,1.5,"f"},{47,29,110,2.5,1.4,"b"},{47,34,95,2.5,1.4,"f"},{46,39,100,2.5,1.3,"f"}}) do
  local set=(q[6]=="b") and {"leaf3","leaf2","leaf1","leaf1"} or {"leaf4","leaf3","leaf2","leaf2"}
  leaf(q[1],q[2],q[3],q[4],q[5],set)
end
L(48,28,47,40,"leaf1")
fin(l)
-- GRANDFATHER CLOCK: arched crest + finial, hood with dial, narrow trunk with glass door + pendulum, wide plinth
l=layer("clock")
pk.rrect(167,28,185,34,4,"wd3"); L(169,28,183,28,"wd5"); D(176,26,"brass3"); D(176,27,"brass2"); D(175,27,"brass1"); D(177,27,"brass1")
R(166,33,186,48,"wd3"); L(166,33,186,33,"wd5"); R(166,34,167,48,"wd4"); L(166,34,166,48,"wd5"); R(185,34,186,48,"wd1")
E(176,40,6,6,"brass2"); E(176,40,5,5,"paper"); D(173,36,"brass4"); D(172,37,"brass3"); D(174,35,"brass3")
D(176,36,"wd1"); D(180,40,"wd1"); D(176,44,"wd1"); D(172,40,"wd1")
L(176,40,176,37,"wd0"); L(176,40,174,39,"wd0"); D(176,40,"brass1"); R(166,48,186,49,"wd1"); L(166,49,186,49,"wd5")
R(168,50,184,72,"wd3"); R(168,50,169,72,"wd4"); L(168,50,168,72,"wd5"); R(183,50,184,72,"wd1")
inset(171,52,181,70,"wd0","wd4","wd1"); R(172,53,180,69,"vn0")
L(176,53,176,64,"brass1"); E(176,66,2,2,"brass2"); D(175,65,"brass4"); D(176,65,"brass3")
D(173,55,"vn2"); D(174,54,"vn2")
R(165,73,187,81,"wd3"); L(165,73,187,73,"wd6"); L(165,74,187,74,"wd5"); L(165,73,165,81,"wd5"); R(186,74,187,81,"wd1")
inset(169,76,183,79,"wd3","wd4","wd1"); L(165,81,187,81,"wd1")
R(165,82,167,82,"wd2"); R(185,82,187,82,"wd1")
fin(l)
-- FRAMES: sunset seascape with a tiny lighthouse (brass frame) + couple photo (wood frame)
l=layer("frames")
bevel(196,32,214,46,"brass2","brass3","brass1"); D(196,32,"brass4")
R(198,34,212,44,"sk2"); L(198,34,212,34,"sk1"); L(198,35,212,35,"sk1"); L(198,38,212,38,"sk3"); L(198,39,212,39,"sk4")
E(208,39,2,1,"sk5"); R(198,41,212,44,"b0"); L(198,41,212,41,"sk3"); D(203,42,"sk4"); D(206,43,"sk3")
R(198,38,202,44,"g0"); L(198,38,201,38,"g1"); D(202,39,"g1")
L(200,35,200,37,"paper"); D(200,35,"sk5"); D(201,36,"paper2")
bevel(218,35,229,50,"wd3","wd5","wd1")
R(220,37,227,48,"paper"); R(221,38,226,47,"paper2")
E(222,41,1,1,"wd2"); E(225,41,1,1,"wd1"); R(221,43,223,47,"b1"); R(224,43,226,47,"r1"); D(222,40,"wd1")
fin(l)
-- TELESCOPE: brass tube (cylindrical ramp, rings, dew shield) aimed up-left at window 1, yoke + tripod
l=layer("telescope")
L(136,62,126,97,"wd2"); L(137,62,127,97,"wd4")
L(138,62,147,97,"wd3"); L(139,62,148,97,"wd2")
L(137,62,137,99,"wd2"); L(138,64,138,99,"wd1")
L(129,86,146,86,"wd2"); D(126,98,"brass2"); D(147,98,"brass2"); D(137,100,"brass2")
tube(116,44,152,60,3.4,2.2,{0.1,0.62})
R(113,41,117,47,"brass2"); L(113,41,113,47,"brass1"); D(114,42,"brass4"); D(115,42,"brass3")
D(112,43,"vn1"); D(112,44,"vn1"); D(112,45,"b2")
R(152,59,155,62,"vn1"); D(152,59,"vn2"); D(156,62,"vn0")
R(134,56,140,61,"wd1"); L(134,56,140,56,"wd4"); D(137,58,"brass3")
fin(l,"brass0")
-- ARMCHAIR: tufted rounded back, cushion, scroll arms, turned feet, sage pillow, knitted throw with fringe
l=layer("armchair")
pk.rrect(270,62,300,82,5,"cur2"); pk.clip()
R(270,62,300,64,"cur3"); L(273,62,297,62,"cur4"); R(270,65,272,82,"cur3"); R(297,62,300,82,"cur1"); pk.unclip()
for _,b in ipairs({{278,69},{285,69},{292,69},{281,75},{289,75}}) do D(b[1],b[2],"cur0"); D(b[1]-1,b[2]-1,"cur3"); D(b[1]+1,b[2]+1,"cur1") end
R(271,80,299,88,"cur3"); L(272,80,298,80,"cur4"); L(271,88,299,88,"cur2")
R(271,89,299,94,"cur2"); L(271,89,299,89,"cur3"); L(271,94,299,94,"cur1"); L(285,89,285,94,"cur1")
pk.rrect(264,71,273,95,3,"cur2"); pk.clip(); R(264,71,273,73,"cur4"); L(264,74,273,74,"cur3"); R(272,74,273,95,"cur1"); pk.unclip()
E(268,84,3,3,"cur3"); E(268,84,2,2,"cur2"); D(268,84,"cur1"); D(267,82,"cur4")
pk.rrect(297,71,306,95,3,"cur1"); pk.clip(); R(297,71,306,73,"cur3"); L(297,74,306,74,"cur2"); pk.unclip()
E(302,84,3,3,"cur2"); E(302,84,2,2,"cur1"); D(302,84,"cur0")
R(266,96,269,98,"wd2"); L(266,96,269,96,"wd4"); R(301,96,304,98,"wd1"); L(301,96,304,96,"wd3")
pk.rrect(273,72,283,80,2,"wp2"); L(274,72,282,72,"wp3"); L(273,80,283,80,"wp0"); D(278,76,"wp0"); D(274,73,"wp_m")
pk.poly({{287,78},{296,76},{300,80},{300,93},{289,95}},"rugc")
pk.clip(); L(287,78,296,76,"paper"); L(288,85,300,83,"cur3"); L(288,86,300,84,"cur2"); L(288,90,300,88,"cur3"); L(296,77,299,94,"rugc2"); L(297,78,300,94,"rugc2"); pk.unclip()
for x=290,299,2 do D(x,96,"rugc2") end
fin(l,"cur0")
-- SIDE TABLE + LAMP BASE + TEACUP
l=layer("sidetable")
R(303,80,319,83,"wd5"); L(303,80,319,80,"wd7"); L(303,81,319,81,"wd6"); L(303,84,319,84,"wd2")
R(304,85,318,89,"wd3"); inset(307,86,315,88,"wd4","wd5","wd2"); D(311,87,"brass3")
L(305,90,305,97,"wd4"); L(306,90,306,96,"wd2"); L(317,90,317,97,"wd2"); L(316,90,316,96,"wd3"); L(308,90,308,94,"wd1"); L(314,90,314,94,"wd1")
L(310,72,310,78,"brass3"); L(311,72,311,78,"brass2"); E(310,77,2,1,"brass2"); D(309,76,"brass4"); R(307,79,313,79,"brass1"); L(308,79,312,79,"brass2")
R(315,77,317,79,"paper"); D(318,78,"paper2"); L(314,80,318,80,"paper2"); D(315,77,"wd1"); D(316,77,"wd1")
fin(l)
-- PLANT: fiddle-leaf fig, distinct shaded leaves on stems, terracotta pot with rim + soil
l=layer("plant")
R(324,88,338,97,"pot2"); R(324,88,325,97,"pot3"); L(326,88,326,96,"pot4"); R(336,88,338,97,"pot1"); L(324,97,338,97,"pot1")
R(323,84,339,87,"pot3"); L(323,84,339,84,"pot4"); L(323,87,339,87,"pot1"); R(337,84,339,86,"pot2")
L(325,85,337,85,"soil"); L(326,84,336,84,"soil")
L(331,84,330,70,"wd2"); L(331,78,336,66,"wd2"); L(330,74,325,62,"wd2"); L(330,68,331,56,"wd1")
local back={"leaf3","leaf2","leaf1","leaf1"}; local front={"leaf5","leaf4","leaf3","leaf2"}; local mid={"leaf4","leaf3","leaf2","leaf1"}
for _,q in ipairs({{333,54,-70,5,2.6,back},{323,60,-140,5,2.6,back},{338,63,-30,5,2.6,back},{327,72,160,5,2.4,back}}) do leaf(table.unpack(q)) end
for _,q in ipairs({{329,56,-110,5,2.8,mid},{337,70,20,5,2.6,mid},{323,68,-170,5,2.6,mid},{334,60,-45,4.5,2.5,front},{326,63,-125,4.5,2.5,front},{334,76,15,4.5,2.4,front},{327,78,165,4.5,2.3,front}}) do leaf(table.unpack(q)) end
fin(l,"leaf0")
-- STEAMER TRUNK (teal leather, wood battens, brass corners, travel stickers) + crate with rolled star charts
l=layer("trunk")
R(44,176,82,197,"tr2")
R(44,176,82,179,"tr3"); L(44,176,82,176,"tr3"); L(45,176,81,176,"#7aa08a"); L(44,180,82,180,"tr1"); L(44,181,82,181,"tr0")
R(44,182,45,197,"tr3"); R(81,182,82,197,"tr1"); L(44,197,82,197,"tr1")
for _,bx in ipairs({52,72}) do R(bx,176,bx+2,197,"box3"); L(bx,176,bx,197,"box4"); L(bx+2,176,bx+2,197,"box2"); D(bx+1,178,"brass3"); D(bx+1,186,"brass3"); D(bx+1,195,"brass3") end
for _,c in ipairs({{44,176},{81,176},{44,196},{81,196}}) do R(c[1],c[2],c[1]+1,c[2]+1,"brass2"); D(c[1],c[2],"brass4") end
R(61,180,65,184,"brass2"); L(61,180,65,180,"brass4"); D(63,182,"brass0"); D(63,183,"brass0")
E(58,189,2,2,"paper"); D(58,189,"r1"); D(57,188,"r2")
R(64,187,69,191,"paper2"); L(64,188,69,188,"sk3"); L(64,190,69,190,"b1")
R(75,189,78,192,"y1"); D(76,190,"y2")
fin(l,"tr0")
l=layer("crate")
R(46,163,68,175,"box3")
R(46,163,68,165,"box4"); L(46,163,68,163,"box5"); L(46,166,68,166,"box1")
for _,y in ipairs({167,171}) do R(48,y,66,y+3,"box3"); L(48,y,66,y,"box4"); L(48,y+3,66,y+3,"box2") end
R(46,166,47,175,"box2"); L(46,166,46,175,"box4"); R(67,166,68,175,"box1")
D(48,168,"box0"); D(66,168,"box0"); D(48,172,"box0"); D(66,172,"box0")
R(51,157,54,164,"paper"); L(51,157,51,164,"paper2"); L(54,157,54,164,"paper3"); E(52,157,2,1,"paper2"); D(52,160,"b1"); D(53,161,"b1")
R(56,159,58,164,"b1"); L(56,159,56,164,"b2"); E(57,159,1,1,"paper")
R(60,158,63,164,"paper2"); L(63,158,63,164,"paper3"); D(61,158,"paper"); D(61,161,"r1")
fin(l,"box0")
-- RECORD CABINET with turntable, sleeves leaning at its side
l=layer("cabinet")
R(297,155,341,161,"wd5"); L(297,155,341,155,"wd7"); L(297,156,341,156,"wd6"); L(297,161,341,161,"wd4")
R(297,162,341,181,"wd3"); L(297,162,341,162,"wd1"); L(297,163,341,163,"wd2")
L(297,162,297,181,"wd4"); L(341,162,341,181,"wd1")
bevel(300,165,318,179,"wd3","wd5","wd1"); inset(302,167,316,177,"wd3","wd4","wd2")
bevel(320,165,338,179,"wd3","wd5","wd1"); inset(322,167,336,177,"wd3","wd4","wd2")
R(316,171,317,172,"brass2"); D(316,171,"brass4"); R(321,171,322,172,"brass2"); D(321,171,"brass4")
R(297,181,341,183,"wd2"); L(297,181,341,181,"wd4"); L(297,183,341,183,"wd1")
R(298,184,300,185,"wd2"); D(298,184,"wd4"); R(338,184,340,185,"wd1")
R(301,155,327,158,"wd1"); L(301,155,327,155,"wd2"); L(301,159,327,159,"wd0")
E(311,156,7,2,"vn1"); L(306,155,313,155,"vn2"); D(305,156,"vn2"); R(310,156,312,156,"r1"); D(311,156,"paper")
D(324,155,"brass4"); D(324,156,"brass2"); L(323,156,316,157,"brass3"); D(315,157,"brass1"); D(325,157,"vn2")
R(331,152,337,158,"wd2"); L(331,152,337,152,"wd4"); E(334,155,2,2,"wd1"); D(334,155,"vn2")
fin(l)
l=layer("sleeves")
pk.poly({{286,171},{295,169},{296,183},{287,184}},"b1"); pk.clip(); E(291,176,3,3,"sk3"); E(291,176,1,1,"sk5"); L(286,171,295,169,"b2"); pk.unclip()
pk.poly({{289,173},{297,172},{297,184},{289,184}},"y1"); pk.clip(); L(289,176,297,175,"r1"); L(289,178,297,177,"r1"); L(289,173,297,172,"y2"); pk.unclip()
fin(l,"b0")
-- OPEN BOOK on the floor (3/4, curved pages, gutter, cover edge) + paper stars
l=layer("floorbits")
pk.poly({{149,107},{158,105},{158,113},{149,115}},"paper"); pk.poly({{158,105},{167,107},{167,115},{158,113}},"paper2")
L(149,116,158,114,"b1"); L(158,114,167,116,"b0"); L(158,105,158,113,"paper3")
L(151,108,156,107,"paper3"); L(151,110,156,109,"paper3"); L(151,112,155,111,"paper3")
L(160,107,165,108,"wd4"); L(160,109,165,110,"paper3"); L(160,111,164,112,"paper3")
D(149,107,"paper2"); D(167,107,"paper3")
fin(l,"wd1")
l=layer("stars")
star(143,110); star(173,118); star(281,160); star(112,138)
fin(l,"y0")
-- WRITING DESK: 3/4 top, drawers with bevels + brass pulls, kneehole; ribboned letters, inkwell + quill, candle
l=layer("desk")
R(48,100,96,104,"wd5"); L(48,100,96,100,"wd7"); L(48,101,96,101,"wd6"); L(48,105,96,105,"wd4"); L(48,106,96,106,"wd2")
R(49,107,95,115,"wd3"); L(49,107,95,107,"wd1")
bevel(52,108,67,114,"wd3","wd5","wd1"); R(58,111,61,111,"brass2"); D(58,111,"brass4")
bevel(77,108,92,114,"wd3","wd5","wd1"); R(83,111,86,111,"brass2"); D(83,111,"brass4")
R(69,108,75,115,"wd0")
R(49,116,51,131,"wd3"); L(49,116,49,131,"wd5"); L(51,116,51,131,"wd1"); R(93,116,95,131,"wd2"); L(93,116,93,131,"wd3"); L(95,116,95,131,"wd1")
L(49,131,51,131,"wd1"); L(93,131,95,131,"wd0")
R(55,97,64,101,"paper"); L(55,97,64,97,"paper"); L(55,99,64,99,"paper2"); L(55,101,64,101,"paper3"); L(59,97,59,101,"r1"); L(55,99,64,99,"r1"); D(59,99,"r2"); D(60,102,"r1"); D(58,102,"r1")
pk.poly({{67,99},{76,98},{77,102},{68,103}},"paper"); L(69,100,75,99,"b1"); L(69,101,74,101,"paper3")
R(81,98,84,101,"vn1"); L(81,98,84,98,"vn2"); D(82,97,"vn2"); L(83,96,87,91,"paper"); L(84,96,88,91,"paper2"); D(88,90,"paper")
E(91,101,2,1,"brass2"); D(90,100,"brass4"); R(91,95,92,100,"paper"); L(92,95,92,100,"paper2")
fin(l)
l=layer("chair")
R(66,110,80,112,"wd4"); L(66,110,80,110,"wd6"); L(66,112,80,112,"wd2")
R(67,116,79,117,"wd3"); L(67,116,79,116,"wd5")
R(67,119,79,120,"cur3"); L(67,119,79,119,"cur4")
R(64,121,82,123,"wd4"); L(64,121,82,121,"wd5"); L(64,124,82,124,"wd2")
R(66,110,67,134,"wd3"); L(66,110,66,134,"wd5"); R(79,110,80,134,"wd2"); L(80,110,80,134,"wd1")
L(64,125,64,131,"wd1"); L(82,125,82,131,"wd1"); L(66,128,80,128,"wd2")
fin(l)
-- BASKET: woven body, rope rim, two yarn balls, knitting needles, trailing strand
l=layer("basket")
for y=88,97 do for x=249,265 do
  local c=(((x//2)+(y//2))%2==0) and "box3" or "box2"
  if x<=250 then c=(c=="box3") and "box4" or "box3" end
  if x>=264 then c=(c=="box3") and "box2" or "box1" end
  if y==97 then c="box1" end
  D(x,y,c) end end
R(248,86,266,87,"box4"); L(248,86,266,86,"box5"); for x=249,265,2 do D(x,87,"box3") end
E(254,84,3,3,"cur3"); L(252,82,256,86,"cur2"); L(251,84,254,87,"cur2"); D(253,82,"cur4"); D(252,83,"cur4")
E(260,84,3,3,"t1"); L(258,82,262,86,"t0"); L(262,82,258,86,"t0"); D(259,82,"t2"); D(258,83,"t2")
L(256,84,261,77,"brass3"); D(262,76,"paper"); L(257,85,264,79,"brass2"); D(265,78,"paper")
fin(l)
l=layer("yarn")
L(266,91,268,94,"cur3"); L(268,95,272,97,"cur3"); L(272,98,276,99,"cur3")
fin(l,"cur1")
-- BOOK STACK (flat books, alternating spines / page edges) + mug
l=layer("bookstack")
local stack={{291,146,309,150,"r1","r0","r2","spine"},{292,142,306,145,"paper","paper3","paper","pages"},{290,138,305,141,"b1","b0","b2","spine"},{293,134,307,137,"g1","g0","g2","pages"},{292,131,305,133,"y1","y0","y2","spine"}}
for _,b in ipairs(stack) do
  local x0,y0,x1,y1=b[1],b[2],b[3],b[4]
  if b[8]=="spine" then R(x0,y0,x1,y1,b[5]); L(x0,y0,x1,y0,b[7]); L(x0,y1,x1,y1,b[6]); D(x0+3,y0+1,"y2"); D(x1-3,y0+1,"y2")
  else R(x0,y0,x1,y1,"paper"); L(x0,y0,x1,y0,b[5]); L(x0,y1,x1,y1,b[5]); L(x0,y0,x0,y1,b[6]); for x=x0+2,x1-1,3 do D(x,y0+1,"paper2") end end
end
L(292,130,305,130,"y2")
R(297,124,302,130,"paper"); L(297,124,297,130,"paper"); R(301,124,302,130,"paper2"); E(299,124,2,1,"wd1"); L(297,124,302,124,"paper2")
D(303,126,"paper2"); D(304,127,"paper2"); D(303,128,"paper2"); L(298,127,300,127,"b1")
fin(l)
-- FLOOR CUSHION (mustard, tufted, piping, tassels)
l=layer("pouf")
pk.rrect(80,152,103,162,3,"mu2"); pk.clip(); R(80,152,103,153,"mu3"); L(83,152,100,152,"mu4"); R(80,154,82,162,"mu3"); R(101,154,103,162,"mu1"); pk.unclip()
D(91,157,"mu0"); D(92,158,"mu1"); D(90,156,"mu3"); D(87,157,"mu1"); D(95,157,"mu1")
R(81,163,102,167,"mu1"); L(81,163,102,163,"mu3"); L(81,167,102,167,"mu0")
for _,c in ipairs({{79,163},{104,163}}) do D(c[1],c[2],"mu3"); D(c[1],c[2]+1,"mu2"); D(c[1],c[2]+2,"mu1") end
fin(l,"mu0")
-- CELESTIAL GLOBE on a wooden stand (right floor)
l=layer("globe")
E(329,125,7,7,"nv1"); pk.clip(); E(327,123,5,5,"nv2"); E(326,121,2,2,"nv3"); R(333,118,337,133,"nv0"); pk.unclip()
D(325,124,"y2"); D(330,121,"y2"); D(332,127,"y1"); D(327,128,"y1"); D(331,124,"brass4"); D(324,121,"y2")
L(324,122,328,121,"nv3"); L(327,127,330,128,"nv3")
L(321,122,323,130,"brass2"); L(322,119,325,118,"brass3"); L(333,118,336,122,"brass2"); L(336,123,335,130,"brass1"); L(324,132,333,133,"brass1")
D(329,117,"brass3"); D(329,133,"brass2")
R(328,134,330,139,"wd3"); L(328,134,328,139,"wd5"); L(330,134,330,139,"wd1")
L(323,146,328,139,"wd3"); L(335,146,330,139,"wd2"); L(329,140,329,146,"wd2"); E(329,140,3,1,"wd4")
fin(l,"nv0")
-- SLIPPERS by the armchair (red felt, cream lining)
l=layer("slippers")
pk.rrect(274,101,281,104,2,"r1"); L(275,101,280,101,"r2"); R(275,102,277,103,"paper2"); D(275,102,"paper3")
pk.rrect(284,102,291,105,2,"r1"); L(285,102,290,102,"r2"); R(285,103,287,104,"paper2"); D(285,103,"paper3")
fin(l,"r0")
------------------------------------------------------------------ STORY PROPS: window seat, wall work-reminder, dustpan + dust
l=layer("windowseat")
R(82,63,126,66,"wp2"); L(83,63,125,63,"wp3"); L(82,66,126,66,"wp0"); for x=88,122,8 do D(x,64,"wp0"); D(x-1,63,"wp_m") end
pk.rrect(84,59,94,63,2,"cur3"); L(85,59,93,59,"cur4"); D(89,61,"cur1")
R(82,67,126,75,"wd3"); L(82,67,126,67,"wd5"); L(82,68,126,68,"wd2")
bevel(85,69,102,74,"wd3","wd4","wd1"); bevel(106,69,123,74,"wd3","wd4","wd1")
L(82,67,82,75,"wd4"); L(126,67,126,75,"wd1"); L(82,75,126,75,"wd1")
fin(l)
l=layer("alarm")
R(140,28,158,30,"wd2"); L(140,28,158,28,"wd4")
pk.rrect(141,31,157,42,2,"paper2"); L(142,31,156,31,"paper"); L(141,33,141,40,"paper"); L(157,33,157,40,"paper3"); L(142,42,156,42,"paper3")
R(143,33,153,38,"vn0"); D(155,34,"r1"); D(155,36,"g1"); R(144,40,154,40,"paper3")
pk.rrect(146,25,152,29,2,"r1"); L(147,25,151,25,"r2"); D(147,26,"#f2a080"); D(149,24,"brass2")
fin(l,"wd1")
l=layer("dustpan")
pk.poly({{156,172},{165,171},{167,176},{156,177}},"t1"); L(156,172,165,171,"t2"); L(157,176,166,176,"t0"); L(166,172,171,168,"t0"); L(167,172,171,169,"t1")
fin(l,"t0")
l=layer("dust")
for _,p in ipairs({{172,171,"paper3"},{173,170,"paper3"},{174,171,"rugc2"},{171,172,"paper3"},{175,172,"paper3"},{173,172,"rugc2"},{177,171,"paper3"},{169,172,"rugc2"}}) do D(p[1],p[2],p[3]) end
------------------------------------------------------------------ EMIT additions: reminder screen (idle) + ringing overlay
local ae=layer("alarm_emit")
R(144,34,152,37,"t0"); L(145,35,147,35,"t2"); D(149,35,"t2"); D(150,35,"t2"); L(145,36,151,36,"t1")
local ar=layer("alarm_ring")
R(144,34,152,37,"r0"); L(145,35,151,35,"#ff8a6a"); L(145,36,151,36,"r2")
pk.rrect(146,25,152,29,2,"r2"); L(147,25,151,25,"#ffc0a0"); D(147,26,"#ffffff")
D(144,25,"y2"); D(143,24,"y2"); D(144,28,"y2"); D(142,27,"y1"); D(154,25,"y2"); D(155,24,"y2"); D(154,28,"y2"); D(156,27,"y1")
------------------------------------------------------------------ EMIT (window glass at dusk, lamp shade with pleats, candle flame)
local em=layer("emit")
for _,x0 in ipairs({92,236}) do
  R(x0,30,x0+31,56,"sk2")
  pk.clip()
  R(x0,30,x0+31,35,"sk0"); R(x0,36,x0+31,41,"sk1"); R(x0,47,x0+31,51,"sk3"); R(x0,52,x0+31,56,"sk4")
  for x=x0,x0+31,2 do D(x,36,"sk0"); D(x+1,47,"sk2"); D(x,52,"sk3") end
  L(x0+3,44,x0+14,44,"sk3"); L(x0+18,39,x0+27,39,"sk1")
  L(x0,55,x0+31,55,"sk5")
  pk.unclip()
  R(x0+15,30,x0+16,56,"wd4"); L(x0+15,30,x0+15,56,"wd5"); R(x0,42,x0+31,43,"wd4"); L(x0,42,x0+31,42,"wd5")
end
D(92+24,33,"#ffffff"); D(92+6,32,"sk5"); D(236+10,31,"sk5")
pk.poly({{306,64},{315,64},{319,72},{302,72}},"lamp1")
pk.clip(); L(306,65,315,65,"lamp3"); L(303,71,318,71,"lamp0"); for x=305,317,3 do L(x,66,x-1,70,"lamp2") end; pk.unclip()
D(91,94,"lamp3"); D(91,93,"lamp2"); D(92,93,"lamp1")
------------------------------------------------------------------ ROBOT (small game sprite, ~15x22) + hop poses for the animation
pk.material({"rw1","rw2","rw3","rw4"},"#3a2a2a","#3a2a2a"); pk.material({"rp1","rp2","rp3","rp4","rp5"},"#3a1410","#3a1410")
local function robot(name, pose)
  local rx,ry=186,146
  local lg=4; local dy=0
  if pose=="crouch" then lg=3; dy=1 elseif pose=="air" then lg=2; dy=0 end
  local rb=layer(name)
  local by=ry+21                       -- foot row (fixed baseline)
  local top=by-17-lg+ (pose=="crouch" and 0 or 0)
  local hy=by-21-(lg-4)                -- head top follows leg length
  -- legs
  R(rx+4,by-lg,rx+5,by-1,"rp3"); R(rx+9,by-lg,rx+10,by-1,"rp2"); R(rx+3,by,rx+6,by,"rp4"); R(rx+8,by,rx+11,by,"rp3")
  if pose=="crouch" then R(rx+2,by,rx+6,by,"rp4"); R(rx+8,by,rx+12,by,"rp3") end
  local y=hy
  -- body
  pk.rrect(rx+2,y+11,rx+12,y+17,2,"rp3"); pk.clip(); R(rx+2,y+11,rx+5,y+13,"rp4"); R(rx+10,y+11,rx+12,y+17,"rp2"); R(rx+2,y+17,rx+12,y+17,"rp2"); pk.unclip()
  R(rx+6,y+13,rx+9,y+15,"rw3"); D(rx+7,y+14,"#e46e4a"); D(rx+6,y+13,"rw4")
  -- arms
  if pose=="stand" then
    L(rx+1,y+12,rx-1,y+8,"rp3"); R(rx-2,y+6,rx,y+7,"rw4")
    L(rx+13,y+12,rx+14,y+15,"rp2"); R(rx+13,y+16,rx+15,y+17,"rw3")
  elseif pose=="crouch" then
    L(rx+1,y+12,rx,y+15,"rp3"); R(rx-1,y+16,rx+1,y+17,"rw4")
    L(rx+13,y+12,rx+14,y+15,"rp2"); R(rx+13,y+16,rx+15,y+17,"rw3")
  else
    L(rx+1,y+12,rx-1,y+8,"rp3"); R(rx-2,y+6,rx,y+7,"rw4")
    L(rx+13,y+12,rx+15,y+8,"rp2"); R(rx+15,y+6,rx+17,y+7,"rw3")
  end
  -- head
  pk.rrect(rx,y,rx+14,y+10,2,"rw3")
  pk.clip(); R(rx,y,rx+14,y+1,"rw4"); R(rx+11,y+2,rx+14,y+10,"rw2"); R(rx,y+10,rx+14,y+10,"rw2"); pk.unclip()
  D(rx+1,y,"rw4"); D(rx+2,y+1,"#ffffff")
  R(rx+2,y+3,rx+10,y+8,"s1"); D(rx+2,y+3,"s2"); L(rx+3,y+8,rx+10,y+8,"s0")
  R(rx+12,y+4,rx+13,y+6,"rp3"); D(rx+12,y+4,"rp4")
  L(rx+6,y-1,rx+6,y-3,"e_gold2")
  fin(rb,"#3a2a2a")
  return hy
end
local function reye(name, hy, blink)
  local rx=186; local y=hy
  local re=layer(name)
  if blink then L(rx+3,y+5,rx+4,y+5,"e_hi"); L(rx+7,y+5,rx+8,y+5,"e_hi")
  else R(rx+3,y+4,rx+4,y+5,"e_hi"); R(rx+7,y+4,rx+8,y+5,"e_hi"); D(rx+3,y+4,"e_core"); D(rx+7,y+4,"e_core") end
  D(rx+6,y-4,"l_sun1"); D(rx+6,y-5,"rp5"); D(rx+5,y-4,"rp2"); D(rx+7,y-4,"rp2")
end
local hs=robot("robot","stand"); local hc=robot("robot_crouch","crouch"); local ha=robot("robot_air","air")
reye("robot_emit",hs,false); reye("robot_emit_blink",hs,true); reye("robot_emit_crouch",hc,false); reye("robot_emit_air",ha,false)
------------------------------------------------------------------ ROBOT story poses (sheet + story frames)
local function broom(x0,y0,x1,y1)   -- handle from (x0,y0) to head top (x1,y1); head sits on floor below
  L(x0,y0,x1,y1,"wd5"); L(x0+1,y0,x1+1,y1,"wd3")
  R(x1-2,y1,x1+3,y1+1,"cur3"); L(x1-2,y1,x1+3,y1,"cur4")
  R(x1-3,y1+2,x1+4,y1+4,"box4"); L(x1-3,y1+4,x1+4,y1+4,"box2"); D(x1-1,y1+3,"box2"); D(x1+2,y1+3,"box3"); D(x1-3,y1+2,"box5")
end
local function head(rx,y,look)
  pk.rrect(rx,y,rx+14,y+10,2,"rw3")
  pk.clip(); R(rx,y,rx+14,y+1,"rw4"); R(rx+11,y+2,rx+14,y+10,"rw2"); R(rx,y+10,rx+14,y+10,"rw2"); pk.unclip()
  D(rx+1,y,"rw4"); D(rx+2,y+1,"#ffffff")
  if look=="back" then
    pk.rrect(rx+4,y+3,rx+10,y+7,1,"rw2"); for x=rx+5,rx+9,2 do L(x,y+4,x,y+6,"rw1") end; D(rx+2,y+8,"rp3"); D(rx+12,y+8,"rp2")
  else
    local sx,sy=0,0; if look=="up" then sx,sy=-1,-1 elseif look=="down" then sy=1 end
    R(rx+2+sx,y+3+sy,rx+10+sx,y+8+sy,"s1"); D(rx+2+sx,y+3+sy,"s2"); L(rx+3+sx,y+8+sy,rx+10+sx,y+8+sy,"s0")
    R(rx+12,y+4,rx+13,y+6,"rp3"); D(rx+12,y+4,"rp4")
  end
  L(rx+6,y-1,rx+6,y-3,"e_gold2")
end
local function body(rx,y,back)
  pk.rrect(rx+2,y+11,rx+12,y+17,2,"rp3"); pk.clip(); R(rx+2,y+11,rx+5,y+13,"rp4"); R(rx+10,y+11,rx+12,y+17,"rp2"); R(rx+2,y+17,rx+12,y+17,"rp2"); pk.unclip()
  if back then R(rx+5,y+13,rx+9,y+15,"rp2"); D(rx+7,y+14,"rp1") else R(rx+6,y+13,rx+9,y+15,"rw3"); D(rx+7,y+14,"#e46e4a"); D(rx+6,y+13,"rw4") end
end
local function legs(rx,by) R(rx+4,by-4,rx+5,by-1,"rp3"); R(rx+9,by-4,rx+10,by-1,"rp2"); R(rx+3,by,rx+6,by,"rp4"); R(rx+8,by,rx+11,by,"rp3") end
local function eyes(name,rx,y,look,blink)
  local e=layer(name)
  local sx,sy=0,0; if look=="up" then sx,sy=-1,-1 elseif look=="down" then sy=1 end
  if look~="back" then
    if blink then L(rx+3+sx,y+5+sy,rx+4+sx,y+5+sy,"e_hi"); L(rx+7+sx,y+5+sy,rx+8+sx,y+5+sy,"e_hi")
    else R(rx+3+sx,y+4+sy,rx+4+sx,y+5+sy,"e_hi"); R(rx+7+sx,y+4+sy,rx+8+sx,y+5+sy,"e_hi"); D(rx+3+sx,y+4+sy,"e_core"); D(rx+7+sx,y+4+sy,"e_core") end
  end
  D(rx+6,y-4,"l_sun1"); D(rx+6,y-5,"rp5"); D(rx+5,y-4,"rp2"); D(rx+7,y-4,"rp2")
end
local RX,BY=186,167; local HY=146
-- sweeping: 4 frames, broom head swings left/right on the floor, head looking down
for i,off in ipairs({-3,0,3,0}) do
  local n="robot_sweep"..i; local rb=layer(n)
  legs(RX,BY); body(RX,HY,false); head(RX,HY,"down")
  broom(RX+13-math.floor(off/3),HY+9,RX-3+off,BY-4)
  R(RX+5+math.floor(off/3),HY+12,RX+6+math.floor(off/3),HY+13,"rw4"); R(RX+9,HY+10,RX+10,HY+11,"rw4")
  fin(rb,"#3a2a2a"); eyes(n.."_emit",RX,HY,"down",false)
end
-- stopped mid-sweep: broom upright in right hand, head tilted up toward the window light
do local rb=layer("robot_look")
  legs(RX,BY); broom(RX+16,HY+2,RX+16,BY-4)
  body(RX,HY,false); head(RX,HY,"up")
  L(RX+1,HY+12,RX,HY+15,"rp3"); R(RX-1,HY+16,RX+1,HY+17,"rw4")
  R(RX+14,HY+12,RX+15,HY+13,"rw4"); L(RX+13,HY+12,RX+14,HY+12,"rp2")
  fin(rb,"#3a2a2a"); eyes("robot_look_emit",RX,HY,"up",false); eyes("robot_look_emit_blink",RX,HY,"up",true)
end
-- reaching up to switch the reminder off
do local rb=layer("robot_reach")
  legs(RX,BY); body(RX,HY,false); head(RX,HY,"up")
  L(RX+13,HY+12,RX+15,HY+3,"rp2"); R(RX+14,HY+1,RX+16,HY+2,"rw4")
  L(RX+1,HY+12,RX,HY+15,"rp3"); R(RX-1,HY+16,RX+1,HY+17,"rw4")
  fin(rb,"#3a2a2a"); eyes("robot_reach_emit",RX,HY,"up",false)
end
-- sitting on the window seat, back to camera, watching the sunset (drawn in place on the seat)
do local sx,sy=101,45; local rb=layer("robot_sit")
  body(sx,sy,true); head(sx,sy,"back")
  L(sx+1,sy+12,sx,sy+16,"rp3"); R(sx-1,sy+16,sx+1,sy+17,"rw3")
  L(sx+13,sy+12,sx+14,sy+16,"rp2"); R(sx+13,sy+16,sx+15,sy+17,"rw2")
  R(sx+3,sy+18,sx+11,sy+18,"rp2")
  fin(rb,"#3a2a2a"); eyes("robot_sit_emit",sx,sy,"back",false)
end
local rsh=layer("robot_shadow"); E(193,168,6,1.5,"#000000")
spr:deleteLayer(spr.layers[1])
spr:saveAs(OUT.."room05.aseprite")
print("room05 ok")
