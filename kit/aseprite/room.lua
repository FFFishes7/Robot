-- room.lua : attic tileset (8x8), perspective plank floor, and props (one layer each, drawn in place on 384x216)
local pk = dofile("/workspace/robot2d/kit/aseprite/pk.lua")
local OUT = "/workspace/robot2d/kit/sprites/"
local pc = app.pixelColor
local function rgba(h) local c=pk.C(h); return pc.rgba(c.red,c.green,c.blue,255) end
local function hsh(a,b,c,d)
  local h=0
  for _,v in ipairs({a or 0,b or 0,c or 0,d or 0}) do h=((h*1000003) ~ (math.floor(v) & 0xffffffff)) & 0xffffffff end
  h = h ~ (h>>13); h=(h*0x5bd1e995) & 0xffffffff; h = h ~ (h>>15)
  return (h & 0xffff)/65535.0
end
------------------------------------------------------------------ TILESET 8x8 (16 tiles in a row)
local ts = Sprite(8*16, 8, ColorMode.RGB)
local timg = Image(8*16,8,ColorMode.RGB)
local P = pk.P
local function tpx(t,x,y,h) timg:drawPixel(t*8+x,y,rgba(h)) end
for t=0,15 do for y=0,7 do for x=0,7 do tpx(t,x,y,"p4") end end end
-- 1..3 plaster with 1px streaks (clusters), 4..5 sparse checker speckle (plaster texture)
for x=1,5 do tpx(1,x,3,"p2") end
for x=0,2 do tpx(2,x,5,"p2") end; for x=4,7 do tpx(2,x,1,"p2") end
for x=2,7 do tpx(3,x,6,"p2") end; tpx(3,0,2,"p5"); tpx(3,1,2,"p5")
for y=0,7 do for x=0,7 do if (x+y)%2==0 and hsh(x,y,4)<0.28 then tpx(4,x,y,"p3") end end end
for y=0,7 do for x=0,7 do if (x+y)%2==0 and hsh(x,y,5)<0.18 then tpx(5,x,y,"p3") end end end; tpx(5,2,4,"p5"); tpx(5,3,4,"p5")
-- 6..8 beam
for y=0,7 do for x=0,7 do tpx(6,x,y, y==0 and "w2" or (y==7 and "wood_ink" or "w1")) end end
for x=0,7 do if (x+ (x//4))%3==0 then tpx(6,x,3,"w0") end end
-- 9..11 baseboard (top lip / body / bottom)
for y=0,7 do for x=0,7 do local c="w3"; if y==0 then c="wood_ink" elseif y==1 then c="w5" elseif y==7 then c="w0" elseif y==6 then c="w2" end; tpx(9,x,y,c) end end
-- 12..14 support post (left edge / mid / right edge), 15 post with groove
for y=0,7 do tpx(12,0,y,"wood_ink"); tpx(12,1,y,"w4"); for x=2,7 do tpx(12,x,y,"w3") end end
for y=0,7 do for x=0,7 do tpx(13,x,y,"w3") end; tpx(13,3,y,"w2") end
for y=0,7 do for x=0,5 do tpx(14,x,y,"w3") end; tpx(14,6,y,"w2"); tpx(14,7,y,"wood_ink") end
for y=0,7 do for x=0,7 do tpx(15,x,y,"w3") end end; for x=1,6 do tpx(15,x,4,"w2") end
ts.cels[1].image = timg
timg:saveAs(OUT.."attic_tiles.png")
ts:saveAs(OUT.."attic_tiles.aseprite")
------------------------------------------------------------------ FLOOR (perspective planks, image layer)
local W,H,FY = 384,216,128
local floor = Image(W,H-FY,ColorMode.RGB)
local FL={"w0","w1","w2","w3","w4","w5"}
local VPX,HZ=170,30
local function fc(x,y) local z=y-HZ; return (x+0.5-VPX)/z*44.0, 1400.0/z end
for y=FY,H-1 do for x=0,W-1 do
  local u,v=fc(x,y); local b=math.floor(u/4.6); local s=u/4.6-b
  local L=24.0; local off=hsh(b,3)*L; local t=(v+off)/L; local pl=math.floor(t)
  local tone = (hsh(b,pl)>0.35) and 4 or ((hsh(b,pl,1)>0.4) and 3 or 5)
  local cs=math.floor(s*3); local ct=math.floor(t*7+hsh(b,pl,cs)*3); local r=hsh(b,pl,cs,ct)
  if r<0.2 then tone=tone-1 elseif r>0.84 then tone=tone+1 end
  local u2=fc(x+1,y); local b2=math.floor(u2/4.6)
  local _,v3=fc(x,y+1); local t3=(v3+off)/L
  if b2~=b or math.floor(t3)~=pl then tone=1 end
  tone=math.max(1,math.min(6,tone))
  floor:drawPixel(x,y-FY,rgba(FL[tone]))
end end
floor:saveAs(OUT.."floor.png")
------------------------------------------------------------------ PROPS (one layer each, in place)
local spr = Sprite(W,H,ColorMode.RGB)
pk.material({"w1","w2","w3","w4","w5","w6"},"wood_ink","wood_ink")
local function L(name) return pk.newlayer(spr,name) end
local function fin(l,d) pk.unclip(); pk.selfoutline(l:cel(1), d or "wood_ink") end
pk.setT(0,0,0,1,1)
-- round window (frame, sky, clouds, hills, mullions) + sill + plant
local l=L("window")
local WX,WY,WR=72,46,23
pk.ell(WX,WY,WR,WR,"w3")
pk.clip(); pk.ell(WX-3,WY-3,WR,WR,"w5"); pk.ell(WX+2,WY+2,WR,WR,"w2"); pk.unclip()
pk.ell(WX,WY,WR-2,WR-2,"w4")
pk.ell(WX,WY,WR-3,WR-3,"sky2")
pk.clip()
  pk.rect(WX-WR,WY-WR,WX+WR,WY-WR+10,"sky1")
  pk.rect(WX-WR,WY+2,WX+WR,WY+10,"sky3"); pk.rect(WX-WR,WY+11,WX+WR,WY+WR,"sky4")
  for x=WX-WR,WX+WR,2 do pk.px(x,WY-WR+11,"sky1"); pk.px(x+1,WY+1,"sky3"); pk.px(x,WY+10,"sky4") end
  pk.ell(WX-10,WY-12,8,2,"#ffffff"); pk.rect(WX-17,WY-10,WX-3,WY-10,"sky3"); pk.ell(WX+9,WY-5,6,1.5,"#ffffff")
  for x=WX-WR,WX+WR do local h=math.floor(6+3*math.sin(x*0.35)+2*math.sin(x*0.9)); pk.line(x,WY+WR-2-h,x,WY+WR,"sky0"); pk.px(x,WY+WR-2-h,"sky1") end
  pk.rect(WX-1,WY-WR,WX,WY+WR,"w4"); pk.rect(WX,WY-WR,WX,WY+WR,"w3")
  pk.rect(WX-WR,WY-1,WX+WR,WY,"w4"); pk.rect(WX-WR,WY,WX+WR,WY,"w3")
pk.unclip()
pk.rect(44,WY+WR+1,102,WY+WR+4,"w3"); pk.clip(); pk.rect(44,WY+WR+1,102,WY+WR+1,"w5"); pk.rect(44,WY+WR+4,102,WY+WR+4,"w2"); pk.unclip()
fin(l)
l=L("plant")
local SY=WY+WR
pk.rect(84,SY-7,92,SY,"#c4553a"); pk.clip(); pk.rect(84,SY-7,85,SY,"#e27a50"); pk.rect(91,SY-7,92,SY,"#8c3226"); pk.unclip()
pk.rect(83,SY-9,93,SY-8,"#e27a50"); pk.rect(83,SY-9,93,SY-9,"#f09a68")
for _,q in ipairs({{88,SY-10,"#3e7a3a"},{87,SY-11,"#5a9a44"},{89,SY-12,"#5a9a44"},{86,SY-13,"#7ab850"},{90,SY-14,"#7ab850"},{88,SY-13,"#3e7a3a"},{88,SY-15,"#3e7a3a"},{88,SY-16,"#5a9a44"},{85,SY-12,"#3e7a3a"},{91,SY-11,"#3e7a3a"},{87,SY-17,"#7ab850"},{89,SY-17,"#5a9a44"},{88,SY-18,"#a0d060"},{86,SY-14,"#5a9a44"},{90,SY-13,"#5a9a44"}}) do pk.px(q[1],q[2],q[3]) end
pk.material({"#c4553a","#e27a50","#8c3226","#f09a68"},"#5a1c14","#5a1c14"); pk.material({"#3e7a3a","#5a9a44","#7ab850","#a0d060"},"#1f3a24","#1f3a24")
fin(l,"#1f3a24")
-- shelves with jars / books / palette
local function shelf(name,x0,x1,y)
  local l=L(name)
  pk.rect(x0,y,x1,y+2,"w3"); pk.clip(); pk.rect(x0,y,x1,y,"w5"); pk.unclip()
  pk.rect(x0+3,y+3,x0+4,y+7,"w1"); pk.rect(x1-4,y+3,x1-3,y+7,"w1")
  return l
end
l=shelf("shelf_top",4,36,62)
local function jar(x,y,body,lid) pk.rect(x,y-7,x+5,y-1,body); pk.clip(); pk.rect(x,y-7,x,y-1,"#dfeaf0"); pk.rect(x+5,y-7,x+5,y-1,"#5a6a8a"); pk.unclip(); pk.rect(x,y-9,x+5,y-8,lid) end
jar(7,62,"#8fb0c8","#c4553a"); jar(16,62,"#a8c4d4","#3e6aa0")
for i,c in ipairs({{"#c4553a",11},{"#3e6aa0",9},{"#d9a441",12},{"#5a9a44",10}}) do local x=25+(i-1)*3; pk.rect(x,62-c[2],x+2,61,c[1]); pk.px(x+1,62-c[2]+2,"p5") end
fin(l)
l=shelf("shelf_low",4,36,88)
pk.ell(15,83,7,4,"w5"); for _,q in ipairs({{11,82,"#c4553a"},{14,81,"#3e6aa0"},{17,82,"#d9a441"},{12,85,"#5a9a44"},{18,85,"#ffffff"}}) do pk.rect(q[1],q[2],q[1]+1,q[2],q[3]) end
pk.rect(26,78,27,87,"#c4553a"); pk.rect(26,76,27,77,"#d9a441"); pk.rect(30,80,31,87,"#3e6aa0"); pk.rect(30,78,31,79,"#ffffff")
fin(l)
-- papers pinned
local function paper(name,x0,y0,w,h,pin,fn)
  local l=L(name); pk.rect(x0,y0,x0+w-1,y0+h-1,"#fbf4e6"); pk.rect(x0,y0+h-1,x0+w-1,y0+h-1,"#e0d4c0"); if fn then fn(x0,y0) end
  pk.unclip(); pk.selfoutline(l:cel(1),"p1"); pk.px(x0+w//2,y0,pin); pk.px(x0+w//2,y0-1,pin)
end
paper("paper_flower",232,20,16,20,"#c4553a",function(x,y) for _,q in ipairs({{8,6},{7,8},{9,8},{8,10},{8,12},{8,14}}) do pk.px(x+q[1],y+q[2],"#5a4a3a") end; pk.px(x+4,y+10,"#d9a441"); pk.px(x+12,y+7,"#3e6aa0") end)
paper("paper_swatch",256,16,20,16,"#3e6aa0",function(x,y) local cs={"#c4553a","#d9a441","#5a9a44","#3e6aa0","#b05090","#e27a50"}; for i=0,5 do pk.rect(x+3+(i%3)*5,y+3+(i//3)*5,x+5+(i%3)*5,y+5+(i//3)*5,cs[i+1]) end end)
paper("paper_mount",262,44,22,14,"#d9a441",function(x,y) pk.line(x+4,y+9,x+10,y+4,"#3e6aa0"); pk.line(x+10,y+4,x+17,y+9,"#3e6aa0") end)
paper("paper_list",290,30,14,18,"#5a9a44",function(x,y) for _,yy in ipairs({5,8,11,14}) do pk.line(x+3,y+yy,x+10,y+yy,"#8a7a6a") end end)
-- door
l=L("door")
pk.rect(334,34,378,126,"w2"); pk.clip(); pk.rect(334,34,334,126,"w4"); pk.rect(378,34,378,126,"w1")
for _,r in ipairs({{40,74},{80,120}}) do pk.rect(339,r[1],373,r[2],"w1"); pk.rect(340,r[1]+1,372,r[2]-1,"w2"); pk.rect(339,r[2],373,r[2],"w4"); pk.rect(373,r[1],373,r[2],"w4") end
pk.unclip(); pk.rect(338,86,339,88,"#e0b050"); pk.px(338,86,"#fff0a0")
fin(l)
-- rug (procedural concentric weave, pixel loop)
l=L("rug")
local img=Image(W,H,ColorMode.RGB)
local RC={196,184}; local RX,RY=100,24
for y=RC[2]-RY-1,H-1 do for x=RC[1]-RX-1,RC[1]+RX+1 do
  local e=math.sqrt(((x+0.5-RC[1])/RX)^2+((y+0.5-RC[2])/RY)^2)
  if e<=1 then
    local ang=math.atan((y-RC[2])/RY,(x-RC[1])/RX); local c
    if e>0.955 then c="r_dk" elseif e>0.9 then c=(math.floor((ang+4)*40)%3~=0) and "r_cream" or "r_cream2"
    elseif e>0.86 then c="r_red2" elseif e>0.72 then c="r_teal"
      if e>0.77 and e<0.81 and math.floor((ang+3.2)*22)%4==0 then c="r_orange" elseif e>0.84 or e<0.74 then c="r_teal2" end
    elseif e>0.68 then c="r_cream" elseif e>0.28 then c="r_red"
      if e>0.4 and e<0.44 and math.floor((ang+3.2)*16)%2==0 then c="r_ochre" elseif e>0.56 and e<0.6 then c="r_red2" end
    elseif e>0.16 then c="#d9c29a" else c=(e>0.07) and "r_ochre" or "#c4553a" end
    if (c=="r_red" or c=="r_red2") then local r=hsh(x,y,77); if (x+y)%2==0 and r<0.28 then c=(c=="r_red") and "r_red2" or "r_red" elseif r>0.95 then c="r_red_hi" end end
    if (c=="r_teal" or c=="r_teal2") and (x+y)%2==0 and hsh(x,y,5)<0.25 then c="r_teal_hi" end
    img:drawPixel(x,y,rgba(c))
  end
end end
l:cel(1).image=img; l:cel(1).position=Point(0,0)
-- stool
l=L("stool")
local sx,sy=40,146
pk.rect(sx,sy,sx+22,sy+3,"w3"); pk.clip(); pk.rect(sx,sy,sx+22,sy,"w5"); pk.unclip()
for _,lx in ipairs({sx+2,sx+18}) do pk.rect(lx,sy+4,lx+2,sy+20,"w2"); pk.px(lx,sy+5,"w4") end
pk.rect(sx+5,sy+13,sx+17,sy+14,"w1")
fin(l)
-- paper balls
l=L("paper_balls")
for _,p in ipairs({{96,198},{304,172},{338,202},{22,192},{262,210},{128,164}}) do
  local x,y=p[1],p[2]
  for _,q in ipairs({{0,0,"#fbf4e6"},{1,0,"#fbf4e6"},{2,0,"#d8ccbc"},{0,1,"#e8dccc"},{1,1,"#fbf4e6"},{2,1,"#b8a898"},{-1,1,"#d8ccbc"},{0,2,"#b8a898"},{1,2,"#a09080"},{1,-1,"#ffffff"},{0,-1,"#e8dccc"}}) do pk.px(x+q[1],y+q[2],q[3]) end
end
pk.unclip(); pk.selfoutline(l:cel(1),"#6a5a4a")
spr:deleteLayer(spr.layers[1])
spr:saveAs(OUT.."room_props.aseprite")
print("room ok")
