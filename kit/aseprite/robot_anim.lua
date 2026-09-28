-- robot_anim.lua : composes robot poses from robot_parts.aseprite into an animated sprite with tags.
-- Layers: "robot" (albedo, lit by the scene) and "emit" (screen face + antenna bulb, self-lit/glow source).
local SP="/workspace/robot2d/kit/sprites/"
local parts = app.open(SP.."robot_parts.aseprite")
local IMG={}
for _,l in ipairs(parts.layers) do
  local cel=l:cel(1)
  if cel then local im=Image(128,128,ColorMode.RGB); im:drawImage(cel.image, cel.position); IMG[l.name]=im end
end
local f=io.open(SP.."robot_parts_anchors.json"); local AJ=f:read("a"); f:close()
local function num(s) return tonumber(s) end
-- tiny anchor lookups (only what we need)
local NECK={0,-19}; local SHL={-13,-14}; local SHR={13,-14}
local HEADH={head_front=34,head_squash=30,head_stretch=37,head_34=34,head_34L=34,head_tilt=34,head_tilt_r=34}
local HEADA={head_tilt=math.rad(-11), head_tilt_r=math.rad(9)}
local W,H=128,128; local HX,HY=64,100
local spr=Sprite(W,H,ColorMode.RGB)
spr.layers[1].name="robot"; local emit=spr:newLayer(); emit.name="emit"
local FL=Image(128,128,ColorMode.RGB)
local function flipped(im) local c=im:clone(); c:flip(FlipType.HORIZONTAL); return c end
-- pose: {legs, head, face, armL, armR, dy(body), hdy(head extra), dx}
local function compose(p)
  local a=Image(W,H,ColorMode.RGB); local e=Image(W,H,ColorMode.RGB)
  local hx,hy=HX+(p.dx or 0), HY+(p.dy or 0)
  local function put(img,name,x,y,flip) local im=IMG[name]; assert(im,name); if flip then im=flipped(im); x=x+1 end; img:drawImage(im, Point(x-64,y-64)) end
  put(a,"legs_"..p.legs, HX+(p.dx or 0), HY)
  put(a,"body",hx,hy)
  local nx,ny=hx+NECK[1], hy+NECK[2]+(p.hdy or 0)
  put(a,"arm_"..p.armL, hx+SHL[1], hy+SHL[2])
  put(a,"arm_"..p.armR, hx+SHR[1], hy+SHR[2], true)
  put(a,p.head,nx,ny)
  put(e,"face_"..p.face.."_"..p.head,nx,ny)
  local ang=HEADA[p.head] or 0; local bx,by=-1,-(HEADH[p.head])-11
  local rx=math.floor(nx+bx*math.cos(ang)-by*math.sin(ang)+0.5); local ry=math.floor(ny+bx*math.sin(ang)+by*math.cos(ang)+0.5)
  put(e,"bulb",rx,ry)
  return a,e
end
local POSES = {
  idle1 ={legs="stand", head="head_front", face="neutral", armL="down", armR="down"},
  idle2 ={legs="stand", head="head_front", face="neutral", armL="down", armR="down", dy=1, hdy=0},
  antic ={legs="crouch",head="head_squash",face="happy",  armL="back", armR="back", dy=4},
  launch={legs="jump",  head="head_stretch",face="sparkle",armL="cheer",armR="raised", dy=-2},
  air   ={legs="tuck",  head="head_tilt",  face="sparkle", armL="cheer",armR="wave", dy=-1},
  fall  ={legs="jump",  head="head_stretch",face="happy", armL="wave", armR="wave", dy=-1},
  land  ={legs="crouch",head="head_squash",face="happy",  armL="reach",armR="reach", dy=4},
  lookL ={legs="stand", head="head_34L",   face="curious", armL="down", armR="down"},
  lookR ={legs="step",  head="head_34",    face="curious", armL="down", armR="back"},
  tiltR ={legs="stand", head="head_tilt_r",face="surprised",armL="down",armR="reach"},
  sleepy={legs="stand", head="head_front", face="sleepy",  armL="down", armR="down", dy=1},
  annoy ={legs="stand", head="head_front", face="annoyed", armL="back", armR="back"},
}
-- timeline @12 fps (each entry = one frame); tags cover ranges
local SEQ = {
  {"idle",  {"idle1","idle1","idle2","idle2"}},
  {"hop",   {"antic","antic","launch","air","air","air","air","fall","land","land","idle1"}},
  {"look",  {"lookL","lookL","lookL","idle1","lookR","lookR","lookR","tiltR","tiltR","idle1"}},
  {"expr",  {"sleepy","annoy"}},
}
local fi=0; local tags={}
for _,s in ipairs(SEQ) do
  local from=fi+1
  for _,pn in ipairs(s[2]) do
    fi=fi+1; if fi>1 then spr:newEmptyFrame() end
    local a,e=compose(POSES[pn])
    spr:newCel(spr.layers[1], fi, a, Point(0,0)); spr:newCel(emit, fi, e, Point(0,0))
    spr.frames[fi].duration = 1/12
  end
  local t=spr:newTag(from,fi); t.name=s[1]
end
spr:saveAs(SP.."robot_anim.aseprite")
-- export a per-frame pose list for the engine
local out=io.open(SP.."robot_anim_poses.txt","w")
for _,s in ipairs(SEQ) do out:write(s[1]..":"..table.concat(s[2],",").."\n") end; out:close()
print("anim frames: "..#spr.frames)
