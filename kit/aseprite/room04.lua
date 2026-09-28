-- room04.lua : Stardew-density 3/4 interior at dusk (To the Moon mood). 384x216 native.
-- Layers: bg (void, walls, floor, rug), shadows (1-colour, drawn semi-transparent in engine), props, emit, robot, robot_emit
local pk = dofile("/workspace/robot2d/kit/aseprite/pk.lua")
local OUT = "/workspace/robot2d/kit/v04/"
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
  wd0="#2e1410", wd1="#4e2418", wd2="#6e3620", wd3="#8e4c2a", wd4="#ad6436", wd5="#c9824a", wd6="#e0a462",
  fl0="#3a1c12", fl1="#5a2e1a", fl2="#7a4426", fl3="#955a32", fl4="#ad6e3e", fl5="#c4864c",
  cur0="#3a1420", cur1="#5e2230", cur2="#83323c", cur3="#a64a4a",
  sk0="#3a2e5e", sk1="#6a4a7a", sk2="#b0607a", sk3="#e8866a", sk4="#f8b870", sk5="#fde0a0",
  rug0="#4a2230", rug1="#6e3440", rug2="#8e4a50", rug3="#b0685e", rugc="#e8c8a0", rugc2="#c09878",
  gl0="#2a3a3a", book1="#8e3a3a", book2="#3a5a7a", book3="#b08a3a", book4="#4a6a3a", book5="#6a3a6a",
  leaf0="#1e3226", leaf1="#2e5034", leaf2="#46723e", leaf3="#6a9a4e", leaf4="#9ac266",
  pot0="#5a2418", pot1="#8a3a24", pot2="#b45a34", pot3="#d47e4c",
  brass0="#5a3a14", brass1="#8a6424", brass2="#c09a3a", brass3="#f0d070",
  paper="#f4e6c8", paper2="#d8c4a0", lamp0="#8a4a2a", lamp1="#f0b060", lamp2="#ffe0a0", lamp3="#fff6d8",
  box0="#5a3a22", box1="#7a5230", box2="#9a6c40", box3="#b88a54", box4="#d4aa70" }
for k,v in pairs(X) do pk.P[k]=v end
pk.material({"wd1","wd2","wd3","wd4","wd5","wd6","box1","box2","box3","box4","fl2","fl3","fl4","fl5"},"wd0","wd0")
pk.material({"cur1","cur2","cur3"},"cur0","cur0")
pk.material({"leaf1","leaf2","leaf3","leaf4"},"leaf0","leaf0")
pk.material({"pot1","pot2","pot3"},"pot0","pot0")
pk.material({"brass1","brass2","brass3"},"brass0","brass0")
pk.material({"rug1","rug2","rug3","rugc","rugc2"},"rug0","rug0")
pk.material({"paper","paper2"},"wd1","wd1")
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
    local tone=({"fl3","fl3","fl4","fl3","fl3","fl2","fl4"})[1+math.floor(hsh(course,bi)*7)]
    local c=tone
    if yy==4 then c="fl1" elseif yy==0 and tone~="fl2" then c=(tone=="fl4") and "fl5" or "fl4" end
    if bxx==0 then c="fl1" end
    -- sparse grain: 1px darker dashes of 3-6px inside boards
    local g=hsh(course,bi,math.floor(bxx/6))
    if yy==2 and g<0.22 and bxx%6<4 then c=(tone=="fl2") and "fl1" or "fl2" end
    P(x,y,c)
  end
end
-- floor/wall contact shadow line
for x=RX0,RX1 do P(x,FY0,"fl1") end
-- bottom wall edge (front)
for y=FY1+1,FY1+8 do for x=RX0-8,RX1+8 do P(x,y, y==FY1+1 and "wd2" or (y==FY1+2 and "wd4" or (y==FY1+8 and "wd0" or "wd1"))) end end
-- rug (rectangular, top-down), border + inner field with simple medallion pattern
local R0x,R1x,R0y,R1y=124,267,122,181
for y=R0y,R1y do for x=R0x,R1x do
  local dx=math.min(x-R0x,R1x-x); local dy=math.min(y-R0y,R1y-y); local d=math.min(dx,dy)
  local c
  if d==0 then c="rug0" elseif d<=2 then c="rugc2" elseif d<=3 then c="rugc" elseif d<=6 then c="rug1"
    if d==5 and ((x+y)%6==0) then c="rugc2" end
  elseif d==7 then c="rugc2" else c="rug2"
    local cx,cy=(R0x+R1x)/2,(R0y+R1y)/2; local md=math.abs(x-cx)/2.2+math.abs(y-cy)
    if md<9 then c="rug3" end; if md<5 then c="rugc2" end; if md<2 then c="rug1" end
    if math.abs(md-14)<0.6 then c="rug1" end
  end
  P(x,y,c)
end end
-- rug fringe on short sides
for y=R0y+2,R1y-2,2 do P(R0x-1,y,"rugc"); P(R1x+1,y,"rugc") end
bg:cel(1).image=img; bg:cel(1).position=Point(0,0)
------------------------------------------------------------------ SHADOWS (soft-edged by being 1 colour at partial alpha in engine)
local sh=layer("shadows")
local SH="#000000"
pk.rect(44,80,79,84,SH)              -- bookshelf
pk.rect(164,80,188,83,SH)            -- clock
pk.ell(285,96,17,4,SH)               -- armchair
pk.ell(311,96,8,2,SH)                -- side table
pk.ell(331,96,9,2,SH)                -- plant
pk.ell(135,97,10,2,SH)               -- telescope
pk.rect(42,186,86,199,SH)            -- crates
pk.rect(296,178,342,185,SH)          -- cabinet
pk.rect(50,125,94,133,SH)            -- desk
pk.ell(257,98,8,2,SH)                -- basket
pk.ell(299,150,9,2,SH)
pk.ell(91,167,12,2.5,SH)
pk.ell(193,168,6,1.5,SH)             -- robot
------------------------------------------------------------------ PROPS
local l
-- windows with curtains (glass on emit layer)
local function window(x0)
  local l=layer("window_"..x0)
  pk.rect(x0-2,28,x0+33,58,"wd4"); pk.clip(); pk.rect(x0-2,28,x0+33,28,"wd6"); pk.rect(x0-2,57,x0+33,58,"wd2"); pk.unclip()
  pk.rect(x0-4,59,x0+35,61,"wd4"); pk.clip(); pk.rect(x0-4,59,x0+35,59,"wd6"); pk.rect(x0-4,61,x0+35,61,"wd2"); pk.unclip()   -- sill
  fin(l)
  local c=layer("curtain_"..x0)
  for _,side in ipairs({{x0-8,x0-1},{x0+32,x0+39}}) do
    pk.rect(side[1],26,side[2],63,"cur2")
    pk.clip(); for x=side[1],side[2],3 do pk.line(x,26,x,63,"cur1") end; pk.line(side[1]+1,26,side[1]+1,63,"cur3"); pk.unclip()
    pk.rect(side[1],44,side[2],45,"brass2")
  end
  pk.rect(x0-10,25,x0+41,25,"brass1"); pk.px(x0-10,25,"brass3"); pk.px(x0+41,25,"brass3")
  fin(c,"cur0")
end
window(92); window(236)
-- bookshelf (3/4: top face + front)
l=layer("bookshelf")
pk.rect(44,30,79,80,"wd2"); pk.clip(); pk.rect(44,30,79,32,"wd4"); pk.rect(44,30,45,80,"wd3"); pk.rect(78,33,79,80,"wd1"); pk.unclip()
for i,y in ipairs({36,48,60,72}) do
  pk.rect(47,y,76,y+9,"wd0")
  local x=47
  while x<75 do local w=2+math.floor(hsh(x,y)*2); local h=6+math.floor(hsh(y,x)*4); local cs={"book1","book2","book3","book4","book5","paper2"}
    local c=cs[1+math.floor(hsh(x*3,y)*6)]
    if hsh(x,y,9)<0.12 then x=x+3 else pk.rect(x,y+10-h,x+w-1,y+9,c); pk.px(x,y+10-h,"paper") end
    x=x+w end
  pk.rect(46,y+10,77,y+11,"wd4")
end
fin(l)
-- grandfather clock (face on emit? no: brass, not emissive)
l=layer("clock")
pk.rect(166,32,186,80,"wd2"); pk.clip(); pk.rect(166,32,168,80,"wd4"); pk.rect(185,32,186,80,"wd1"); pk.rect(166,32,186,33,"wd5"); pk.unclip()
pk.ell(176,40,6,6,"brass2"); pk.ell(176,40,5,5,"paper"); pk.line(176,40,176,36,"wd0"); pk.line(176,40,179,41,"wd0")
pk.rect(171,52,181,72,"wd0"); pk.line(176,52,176,66,"brass1"); pk.ell(176,67,2,2,"brass3")
pk.rect(164,78,188,81,"wd3"); pk.clip(); pk.rect(164,78,188,78,"wd5"); pk.unclip()
fin(l)
-- framed pictures cluster (between clock and window 2)
l=layer("frames")
pk.rect(196,32,214,46,"brass1"); pk.rect(198,34,212,44,"sk2"); pk.clip(); pk.rect(198,40,212,44,"leaf2"); pk.ell(208,37,2,2,"sk5"); pk.unclip()
pk.rect(218,36,228,50,"wd3"); pk.rect(220,38,226,48,"paper"); pk.ell(223,42,2,2,"cur2"); pk.rect(221,45,225,48,"book2")
fin(l)
-- telescope on tripod aimed at window 1
l=layer("telescope")
pk.line(134,70,127,96,"wd3"); pk.line(135,70,142,96,"wd3"); pk.line(134,70,135,97,"wd2")
pk.poly({{122,58},{150,50},{152,56},{124,64}},"brass2")
pk.clip(); pk.line(122,58,150,50,"brass3"); pk.line(124,64,152,56,"brass1"); pk.unclip()
pk.rect(150,49,153,57,"brass1"); pk.rect(132,62,137,68,"wd1")
fin(l,"brass0")
-- armchair (3/4 view)
l=layer("armchair")
pk.rrect(270,64,300,84,4,"cur2")            -- back
pk.clip(); pk.rect(270,64,300,66,"cur3"); pk.rect(296,64,300,84,"cur1"); pk.unclip()
pk.rrect(268,76,302,96,3,"cur2")            -- seat block
pk.clip(); pk.rect(268,76,302,78,"cur3"); pk.rect(268,92,302,96,"cur1"); pk.unclip()
pk.rrect(266,72,272,96,2,"cur3"); pk.rrect(298,72,304,96,2,"cur1")   -- arms
pk.poly({{276,80},{292,78},{296,92},{280,94}},"rugc")               -- blanket
pk.clip(); pk.line(276,84,294,82,"rugc2"); pk.line(278,88,295,86,"rugc2"); pk.unclip()
fin(l,"cur0")
-- side table + lamp (shade glows -> emit)
l=layer("sidetable")
pk.rect(304,82,318,85,"wd4"); pk.clip(); pk.rect(304,82,318,82,"wd6"); pk.unclip()
pk.rect(305,86,306,96,"wd2"); pk.rect(316,86,317,96,"wd2")
pk.rect(310,74,312,81,"brass1"); pk.rect(307,80,315,81,"brass2")
pk.rect(330-24,90,330-20,90,"wd3")
fin(l)
-- tall plant
l=layer("plant")
pk.rect(324,84,338,96,"pot2"); pk.clip(); pk.rect(324,84,326,96,"pot3"); pk.rect(336,84,338,96,"pot1"); pk.rect(324,84,338,85,"pot3"); pk.unclip()
for i=0,9 do local a=math.rad(-150+i*13); local r=14+hsh(i,4)*8
  pk.line(331,84,331+math.cos(a)*r*0.8,84+math.sin(a)*r*1.6,(i%3==0) and "leaf3" or "leaf2") end
for _,q in ipairs({{324,62},{338,60},{330,52},{326,70},{337,72},{333,58}}) do pk.ell(q[1],q[2],2,1.5,"leaf3"); pk.px(q[1]-1,q[2]-1,"leaf4") end
fin(l,"leaf0")
-- crates cluster (bottom-left foreground)
l=layer("crates")
local function crate(x0,y0,w,h,t)
  pk.rect(x0,y0,x0+w,y0+t,"box3"); pk.rect(x0,y0+t+1,x0+w,y0+h,"box2")
  pk.clip(); pk.rect(x0,y0,x0+w,y0,"box4"); pk.rect(x0,y0+t+1,x0+w,y0+t+1,"box1"); pk.line(x0+2,y0+t+3,x0+w-2,y0+h-2,"box1"); pk.rect(x0+w-1,y0+t+1,x0+w,y0+h,"box1"); pk.unclip()
end
crate(44,172,26,24,7); crate(68,182,16,14,5); crate(48,160,18,13,5)
fin(l)
-- record player cabinet (bottom-right foreground)
l=layer("cabinet")
pk.rect(298,160,340,184,"wd3"); pk.clip(); pk.rect(298,160,340,166,"wd4"); pk.rect(298,160,340,160,"wd6"); pk.rect(298,167,340,167,"wd1"); pk.unclip()
pk.rect(302,170,317,181,"wd2"); pk.rect(321,170,336,181,"wd2"); pk.px(316,175,"brass3"); pk.px(322,175,"brass3")
pk.ell(314,162,7,2.5,"gl0"); pk.px(314,162,"cur3"); pk.line(328,159,322,162,"brass2"); pk.rect(327,158,329,159,"brass1")
fin(l)
-- floor story props: open book + scattered paper stars near the telescope
l=layer("floorbits")
pk.poly({{150,106},{158,104},{158,111},{150,113}},"paper"); pk.poly({{158,104},{166,106},{166,113},{158,111}},"paper2")
pk.line(152,108,156,107,"wd2"); pk.line(160,107,164,108,"wd2")
fin(l,"wd1")
-- writing desk + chair (left, mid floor) with letters and a small lamp-less candle
l=layer("desk")
pk.rect(50,104,94,110,"wd4"); pk.clip(); pk.rect(50,104,94,104,"wd6"); pk.rect(50,110,94,110,"wd2"); pk.unclip()
pk.rect(52,111,92,124,"wd2"); pk.clip(); pk.rect(52,111,92,112,"wd1"); pk.unclip()
pk.rect(56,114,70,120,"wd3"); pk.rect(74,114,88,120,"wd3"); pk.px(63,117,"brass3"); pk.px(81,117,"brass3")
pk.rect(52,125,54,130,"wd2"); pk.rect(90,125,92,130,"wd2")
pk.poly({{58,101},{68,100},{69,104},{59,105}},"paper"); pk.poly({{70,102},{78,101},{78,104},{70,105}},"paper2")
pk.rect(84,98,86,103,"brass2"); pk.px(85,97,"paper")
fin(l)
l=layer("chair")
pk.rect(66,120,80,122,"wd4"); pk.rect(66,112,80,119,"wd3"); pk.clip(); pk.rect(66,112,80,113,"wd5"); pk.rect(78,112,80,119,"wd2"); pk.unclip()
pk.rect(67,123,68,132,"wd2"); pk.rect(78,123,79,132,"wd2")
fin(l)
-- basket of yarn/blanket by the armchair
l=layer("basket")
pk.rect(250,88,264,97,"box3"); pk.clip(); for x=250,264,2 do pk.line(x,88,x,97,"box2") end; pk.rect(250,88,264,88,"box4"); pk.unclip()
pk.ell(254,86,3,2,"cur3"); pk.ell(260,86,3,2,"book2"); pk.px(253,85,"rugc")
fin(l)
l=layer("bookstack")
pk.rect(292,146,306,149,"book1"); pk.rect(293,142,305,145,"book2"); pk.rect(291,138,303,141,"book3"); pk.rect(294,134,304,137,"book4")
pk.clip(); pk.line(292,146,292,149,"paper"); pk.line(293,142,293,145,"paper"); pk.line(291,138,291,141,"paper"); pk.line(294,134,294,137,"paper"); pk.unclip()
pk.ell(299,131,3,2,"gl0")
fin(l)
l=layer("pouf")
pk.ell(90,160,11,6,"cur2"); pk.clip(); pk.ell(88,158,8,3,"cur3"); pk.rect(79,163,101,167,"cur1"); pk.unclip(); pk.px(90,159,"cur0")
fin(l)
------------------------------------------------------------------ EMIT (window glass at dusk, lamp shade)
local em=layer("emit")
for _,x0 in ipairs({92,236}) do
  pk.rect(x0,30,x0+31,56,"sk2")
  pk.clip()
  pk.rect(x0,30,x0+31,35,"sk0"); pk.rect(x0,36,x0+31,41,"sk1"); pk.rect(x0,47,x0+31,51,"sk3"); pk.rect(x0,52,x0+31,56,"sk4")
  for x=x0,x0+31,2 do pk.px(x,36,"sk0"); pk.px(x+1,47,"sk2"); pk.px(x,52,"sk3") end
  pk.line(x0+3,44,x0+14,44,"sk3"); pk.line(x0+18,39,x0+27,39,"sk1")
  pk.line(x0,55,x0+31,55,"sk5")
  pk.unclip()
  pk.rect(x0+15,30,x0+16,56,"wd4"); pk.rect(x0,42,x0+31,43,"wd4")    -- mullions (drawn on emit so they stay crisp over glass)
end
pk.px(92+24,33,"#ffffff"); pk.px(92+6,32,"sk5")      -- first star
-- lamp shade (trapezoid) + bulb glow
pk.poly({{306,66},{316,66},{319,74},{303,74}},"lamp1"); pk.clip(); pk.line(306,67,315,67,"lamp3"); pk.line(304,73,318,73,"lamp0"); pk.unclip()
------------------------------------------------------------------ ROBOT (small game sprite, ~15x22), standing on the rug looking up at window 1
local rb=layer("robot")
local rx,ry=186,146   -- top-left of sprite box
pk.material({"rw1","rw2","rw3","rw4"},"#3a2a2a","#3a2a2a"); pk.material({"rp1","rp2","rp3","rp4","rp5"},"#3a1410","#3a1410")
-- legs
pk.rect(rx+4,ry+17,rx+5,ry+20,"rp3"); pk.rect(rx+9,ry+17,rx+10,ry+20,"rp2"); pk.rect(rx+3,ry+21,rx+6,ry+21,"rp4"); pk.rect(rx+8,ry+21,rx+11,ry+21,"rp3")
-- body
pk.rrect(rx+2,ry+11,rx+12,ry+17,2,"rp3"); pk.clip(); pk.rect(rx+2,ry+11,rx+5,ry+13,"rp4"); pk.rect(rx+10,ry+11,rx+12,ry+17,"rp2"); pk.rect(rx+2,ry+17,rx+12,ry+17,"rp2"); pk.unclip()
pk.rect(rx+6,ry+13,rx+9,ry+15,"rw3"); pk.px(rx+7,ry+14,"#e46e4a")
-- arms (left arm raised pointing at window)
pk.line(rx+1,ry+12,rx-1,ry+8,"rp3"); pk.rect(rx-2,ry+6,rx,ry+7,"rw4")
pk.line(rx+13,ry+12,rx+14,ry+15,"rp2"); pk.rect(rx+13,ry+16,rx+15,ry+17,"rw3")
-- head (3/4 turned to its right = toward window at left), slight upward tilt
pk.rrect(rx,ry,rx+14,ry+10,2,"rw3")
pk.clip(); pk.rect(rx,ry,rx+14,ry+1,"rw4"); pk.rect(rx+11,ry+2,rx+14,ry+10,"rw2"); pk.rect(rx,ry+10,rx+14,ry+10,"rw2"); pk.unclip()
pk.rect(rx+2,ry+3,rx+10,ry+8,"s1"); pk.px(rx+2,ry+3,"s2")
pk.rect(rx+12,ry+4,rx+13,ry+6,"rp3")         -- ear bolt on the side
pk.line(rx+6,ry-1,rx+6,ry-3,"e_gold2")
fin(rb,"#3a2a2a")
local re=layer("robot_emit")
pk.rect(rx+3,ry+4,rx+4,ry+5,"e_hi"); pk.rect(rx+7,ry+4,rx+8,ry+5,"e_hi"); pk.px(rx+3,ry+4,"e_core"); pk.px(rx+7,ry+4,"e_core")
pk.px(rx+6,ry-4,"l_sun1"); pk.px(rx+6,ry-5,"rp5"); pk.px(rx+5,ry-4,"rp2"); pk.px(rx+7,ry-4,"rp2")
spr:deleteLayer(spr.layers[1])
spr:saveAs(OUT.."room04.aseprite")
print("room04 ok")
