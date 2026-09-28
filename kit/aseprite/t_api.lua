local spr = Sprite(64,64,ColorMode.RGB)
local lay = spr.layers[1]; lay.name="test"
app.activeLayer = lay
app.useTool{tool="filled_ellipse", color=Color{r=200,g=100,b=80}, points={Point(10,10),Point(40,30)}, layer=lay, frame=spr.frames[1]}
app.command.MaskContent()
app.useTool{tool="filled_ellipse", color=Color{r=90,g=40,b=30}, points={Point(20,18),Point(50,40)}, layer=lay, frame=spr.frames[1]}
app.command.DeselectMask()
app.useTool{tool="contour", color=Color{r=40,g=160,b=90}, points={Point(44,44),Point(60,48),Point(52,62),Point(42,58)}, layer=lay, frame=spr.frames[1]}
app.command.Outline{ui=false, color=Color{r=30,g=10,b=10}, matrix="circle", place="outside"}
spr:saveCopyAs("/tmp/t_api.png")
local f=io.open("/tmp/t_api.txt","w"); f:write("io ok\n"); f:close()
print("done")
