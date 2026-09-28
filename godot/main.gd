extends Node2D
# Attic scene composer: Tiled map (raster + JSON objects) + Aseprite sheets -> native 384x216 lit viewport
# -> 5x nearest upscale -> smooth overlays (shaft, emitter glow, dust, vignette). Driven by Movie Maker.
const KIT := "/workspace/robot2d/kit/"
const NW := 384
const NH := 216
const S := 5
var mode := "still"
var lightvp: SubViewport
var litvp: SubViewport
var roomvp: SubViewport
var emitvp: SubViewport
var robot_a: AnimatedSprite2D
var robot_e: AnimatedSprite2D
var robot_root: Node2D
var shadow_spr: Sprite2D
var objects := {}

func tex(path: String) -> ImageTexture:
	var img := Image.load_from_file(path)
	return ImageTexture.create_from_image(img)

func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--mode="): mode = a.substr(7)
	var mj = JSON.parse_string(FileAccess.get_file_as_string(KIT + "tiled/attic.json"))
	for L in mj["layers"]:
		if L.get("type") == "objectgroup":
			for o in L["objects"]:
				objects[o["name"]] = o
	_build_lightmap()
	_build_lit()
	_build_emit()
	_build_screen()
	if mode == "anim":
		_build_anim()
	else:
		_pose_still()

# ---------------------------------------------------------------- light map (value/6 in red channel)
func _radial() -> GradientTexture2D:
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1)); g.set_color(1, Color(0, 0, 0))
	g.add_point(0.6, Color(0.85, 0.85, 0.85))
	var t := GradientTexture2D.new()
	t.gradient = g; t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5); t.fill_to = Vector2(1.0, 0.5); t.width = 128; t.height = 128
	return t

func prop(o: Dictionary, k: String, d):
	if o.has("properties"):
		for p in o["properties"]:
			if p["name"] == k: return p["value"]
	return d

func _light_sprite(parent: Node, o: Dictionary, inten: float) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = _radial(); s.centered = true
	s.position = Vector2(o["x"] + o["width"] / 2.0, o["y"] + o["height"] / 2.0)
	s.scale = Vector2(o["width"] / 128.0, o["height"] / 128.0)
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD if inten > 0 else CanvasItemMaterial.BLEND_MODE_SUB
	s.material = m
	var v: float = abs(inten) / 6.0
	s.modulate = Color(v, v, v)
	parent.add_child(s)
	return s

func _build_lightmap() -> void:
	lightvp = SubViewport.new(); lightvp.size = Vector2i(NW, NH); lightvp.transparent_bg = false
	lightvp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(lightvp)
	var amb := ColorRect.new(); amb.size = Vector2(NW, NH)
	var sh := Shader.new()
	sh.code = """shader_type canvas_item;
void fragment(){
  vec2 p = UV * vec2(384.0, 216.0); float v;
  if (p.y < 128.0) { v = 2.35 - 0.004*abs(p.x-110.0) - 0.006*max(0.0,p.x-240.0) - 0.35*max(0.0,12.0-p.y)/12.0; }
  else { v = 2.05 - 0.006*abs(p.x-150.0) - 0.0036*(p.y-128.0) - 0.004*max(0.0,p.x-250.0); }
  COLOR = vec4(v/6.0, 0.0, 0.0, 1.0);
}"""
	var sm := ShaderMaterial.new(); sm.shader = sh; amb.material = sm
	lightvp.add_child(amb)
	for n in ["window_glow", "wall_patch", "sun_pool", "stool_shadow"]:
		var o: Dictionary = objects[n]
		var ls := _light_sprite(lightvp, o, prop(o, "intensity", 1.0))
		ls.rotation_degrees = prop(o, "angle", 0.0)
	# window mullion shadows inside the sun pool (thin subtractive strips)
	var pool: Dictionary = objects["sun_pool"]
	var c := Vector2(pool["x"] + pool["width"] / 2.0, pool["y"] + pool["height"] / 2.0)
	for seg in [[c + Vector2(-34, 0), c + Vector2(34, 0)], [c + Vector2(8, -13), c + Vector2(-8, 13)]]:
		var ln := Line2D.new(); ln.points = PackedVector2Array(seg); ln.width = 1.6
		ln.default_color = Color(1.4 / 6.0, 0, 0)
		var m := CanvasItemMaterial.new(); m.blend_mode = CanvasItemMaterial.BLEND_MODE_SUB; ln.material = m
		lightvp.add_child(ln)
	shadow_spr = _light_sprite(lightvp, objects["robot_shadow"], prop(objects["robot_shadow"], "intensity", -1.8))

# ---------------------------------------------------------------- lit native viewport
func _build_lit() -> void:
	litvp = SubViewport.new(); litvp.size = Vector2i(NW, NH); litvp.transparent_bg = false
	litvp.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	litvp.snap_2d_transforms_to_pixel = true
	litvp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(litvp)
	var room := Sprite2D.new(); room.centered = false
	room.texture = tex(KIT + "tiled/attic_raster.png")
	var sm := ShaderMaterial.new(); sm.shader = load("res://shaders/light_dither.gdshader")
	sm.set_shader_parameter("lightmap", lightvp.get_texture())
	var T := [Vector3(0.42,0.34,0.46),Vector3(0.60,0.50,0.58),Vector3(0.80,0.70,0.70),Vector3(1.0,0.92,0.84),Vector3(1.22,1.02,0.78),Vector3(1.42,1.12,0.80)]
	var A := [Vector3.ZERO,Vector3.ZERO,Vector3.ZERO,Vector3.ZERO,Vector3(28,12,0),Vector3(60,30,6)]
	var tints := PackedVector3Array(); var adds := PackedVector3Array()
	for i in 11:
		var lo: int = i / 2; var hi: int = min(5, lo + 1); var f := 0.5 if i % 2 == 1 else 0.0
		tints.append(T[lo].lerp(T[hi], f)); adds.append(A[lo].lerp(A[hi], f))
	sm.set_shader_parameter("tints", tints); sm.set_shader_parameter("adds", adds)
	room.material = sm
	roomvp = SubViewport.new(); roomvp.size = Vector2i(NW, NH); roomvp.transparent_bg = false
	roomvp.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	roomvp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(roomvp); roomvp.add_child(room)
	var rs := Sprite2D.new(); rs.centered = false; rs.texture = roomvp.get_texture(); litvp.add_child(rs)
	robot_root = Node2D.new(); litvp.add_child(robot_root)
	robot_a = _robot_sprite("robot_sheet_albedo.png")
	robot_a.modulate = Color(1.0, 0.96, 0.9)
	robot_root.add_child(robot_a)

func _robot_frames(sheet: String) -> SpriteFrames:
	var j = JSON.parse_string(FileAccess.get_file_as_string(KIT + "sprites/robot_anim.json"))
	var t := tex(KIT + "sprites/" + sheet)
	var sf := SpriteFrames.new()
	sf.set_animation_speed("default", 12.0); sf.set_animation_loop("default", true)
	for fr in j["frames"]:
		var at := AtlasTexture.new(); at.atlas = t
		var r = fr["frame"]; at.region = Rect2(r["x"], r["y"], r["w"], r["h"])
		sf.add_frame("default", at)
	return sf

func _robot_sprite(sheet: String) -> AnimatedSprite2D:
	var s := AnimatedSprite2D.new()
	s.sprite_frames = _robot_frames(sheet); s.centered = false
	s.offset = Vector2(-64, -112)   # node origin = point between the feet on the floor
	return s

# ---------------------------------------------------------------- emitters (sharp on top + glow source)
func _sparkle_tex() -> ImageTexture:
	# 5-frame strip 7x7: dot, small cross, big cross, small cross, dot (pixel crosses on the grid)
	var img := Image.create(35, 7, false, Image.FORMAT_RGBA8)
	var W := Color("#ffffff"); var Y1 := Color("#fff4c8"); var Y2 := Color("#ffd970")
	for f in 5:
		var cx := f * 7 + 3; var cy := 3
		var size: int = [0, 1, 2, 1, 0][f]
		img.set_pixel(cx, cy, W)
		for d in range(1, size + 1):
			var col: Color = Y1 if d == 1 else Y2
			img.set_pixel(cx + d, cy, col); img.set_pixel(cx - d, cy, col)
			img.set_pixel(cx, cy + d, col); img.set_pixel(cx, cy - d, col)
	return ImageTexture.create_from_image(img)

func _build_emit() -> void:
	emitvp = SubViewport.new(); emitvp.size = Vector2i(NW, NH); emitvp.transparent_bg = true
	emitvp.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	emitvp.snap_2d_transforms_to_pixel = true
	emitvp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(emitvp)
	robot_e = _robot_sprite("robot_sheet_emit.png")
	var rr := Node2D.new(); rr.name = "robot_e_root"; emitvp.add_child(rr); rr.add_child(robot_e)
	var p := CPUParticles2D.new(); p.name = "sparkles"
	p.texture = _sparkle_tex()
	var m := CanvasItemMaterial.new(); m.particles_animation = true; m.particles_anim_h_frames = 5; m.particles_anim_v_frames = 1; m.particles_anim_loop = false
	p.material = m
	p.amount = 14; p.lifetime = 1.6; p.preprocess = 3.0; p.randomness = 1.0
	p.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE; p.emission_rect_extents = Vector2(34, 30)
	p.direction = Vector2(0, -1); p.spread = 180; p.initial_velocity_min = 0.0; p.initial_velocity_max = 4.0
	p.gravity = Vector2(0, -2); p.anim_speed_min = 1.0; p.anim_speed_max = 1.0
	p.local_coords = false; p.fixed_fps = 12; p.fract_delta = false
	emitvp.add_child(p)

# ---------------------------------------------------------------- 1920x1080 compositor
func _full(t: Texture2D, filt: int) -> TextureRect:
	var r := TextureRect.new(); r.texture = t; r.size = Vector2(NW * S, NH * S)
	r.stretch_mode = TextureRect.STRETCH_SCALE; r.texture_filter = filt
	return r

func _build_screen() -> void:
	var lit := _full(litvp.get_texture(), CanvasItem.TEXTURE_FILTER_NEAREST); add_child(lit)
	# sun shaft (smooth, additive, off-grid)
	var sh: Dictionary = objects["sun_shaft"]
	var pts := PackedVector2Array()
	for q in sh["polygon"]: pts.append(Vector2(sh["x"] + q["x"], sh["y"] + q["y"]) * S)
	var poly := Polygon2D.new(); poly.polygon = pts
	poly.uv = PackedVector2Array([Vector2(0, 0), Vector2(384, 0), Vector2(384, 216), Vector2(0, 216)])
	var ssm := ShaderMaterial.new(); ssm.shader = load("res://shaders/shaft.gdshader"); poly.material = ssm
	poly.texture = tex(KIT + "tiled/attic_raster.png")  # any texture so UV is interpolated
	add_child(poly)
	# hot-spot glow from the lit image, masked to the brightest light band (sun pool) only
	var hot := _full(roomvp.get_texture(), CanvasItem.TEXTURE_FILTER_LINEAR)
	var hm := ShaderMaterial.new(); hm.shader = load("res://shaders/glow.gdshader")
	hm.set_shader_parameter("radius", 3.0); hm.set_shader_parameter("strength", 0.3); hm.set_shader_parameter("threshold", 0.55)
	hm.set_shader_parameter("use_mask", true); hm.set_shader_parameter("mask", lightvp.get_texture())
	hot.material = hm; add_child(hot)
	# window sky: weak glow source
	var skyvp := SubViewport.new(); skyvp.size = Vector2i(NW, NH); skyvp.transparent_bg = true
	skyvp.render_target_update_mode = SubViewport.UPDATE_ALWAYS; add_child(skyvp)
	var win := Sprite2D.new(); win.centered = false; win.texture = tex(KIT + "tiled/attic_raster.png")
	var skm := ShaderMaterial.new(); skm.shader = load("res://shaders/sky_mask.gdshader"); win.material = skm; skyvp.add_child(win)
	var skyg := _full(skyvp.get_texture(), CanvasItem.TEXTURE_FILTER_LINEAR)
	var sg := ShaderMaterial.new(); sg.shader = load("res://shaders/glow.gdshader"); sg.set_shader_parameter("radius", 4.0); sg.set_shader_parameter("strength", 0.6)
	skyg.material = sg; add_child(skyg)
	# emitters: sharp pixels on top, then two glow radii (additive)
	add_child(_full(emitvp.get_texture(), CanvasItem.TEXTURE_FILTER_NEAREST))
	for rs in [[1.2, 0.35], [3.5, 0.3]]:
		var g := _full(emitvp.get_texture(), CanvasItem.TEXTURE_FILTER_LINEAR)
		var gm := ShaderMaterial.new(); gm.shader = load("res://shaders/glow.gdshader")
		gm.set_shader_parameter("radius", rs[0]); gm.set_shader_parameter("strength", rs[1]); g.material = gm
		add_child(g)
	# dust motes: soft, sub-pixel, drifting inside the shaft (Godot CPUParticles2D at full res)
	var d := CPUParticles2D.new(); d.name = "dust"
	var gt := GradientTexture2D.new(); var gg := Gradient.new(); gg.set_color(0, Color(1, 1, 1, 1)); gg.set_color(1, Color(1, 1, 1, 0))
	gt.gradient = gg; gt.fill = GradientTexture2D.FILL_RADIAL; gt.fill_from = Vector2(0.5, 0.5); gt.fill_to = Vector2(1, 0.5); gt.width = 16; gt.height = 16
	d.texture = gt
	var dm := CanvasItemMaterial.new(); dm.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD; d.material = dm
	var ep := PackedVector2Array()
	var rng := RandomNumberGenerator.new(); rng.seed = 7
	while ep.size() < 300:
		var q := Vector2(rng.randf_range(40, 200), rng.randf_range(28, 192)) * S
		if Geometry2D.is_point_in_polygon(q, pts): ep.append(q)
	d.emission_shape = CPUParticles2D.EMISSION_SHAPE_POINTS; d.emission_points = ep
	d.amount = 70; d.lifetime = 7.0; d.preprocess = 7.0; d.randomness = 1.0
	d.direction = Vector2(0.3, -1); d.spread = 180; d.initial_velocity_min = 2; d.initial_velocity_max = 10; d.gravity = Vector2(0, 1.5)
	d.scale_amount_min = 0.15; d.scale_amount_max = 0.38
	var cr := Gradient.new(); cr.set_color(0, Color(1, 0.95, 0.8, 0)); cr.set_color(1, Color(1, 0.95, 0.8, 0)); cr.add_point(0.3, Color(1, 0.95, 0.8, 0.85)); cr.add_point(0.7, Color(1, 0.95, 0.8, 0.6))
	d.color_ramp = cr
	add_child(d)
	var vig := ColorRect.new(); vig.size = Vector2(NW * S, NH * S)
	var vm := ShaderMaterial.new(); vm.shader = load("res://shaders/vignette.gdshader"); vig.material = vm
	add_child(vig)

# ---------------------------------------------------------------- poses
func _set_robot(pos: Vector2, frame: int) -> void:
	robot_root.position = pos.round()
	emitvp.get_node("robot_e_root").position = pos.round()
	robot_a.frame = frame; robot_e.frame = frame

func _pose_still() -> void:
	var o: Dictionary = objects["robot_still"]
	_set_robot(Vector2(o["x"], o["y"]), 7)   # hop tag, "air": tuck legs, tilted head, sparkle eyes, arm up
	shadow_spr.position = Vector2(o["x"] + 2, 191); shadow_spr.scale = Vector2(36 / 128.0, 7 / 128.0)
	robot_a.modulate = Color(1.05, 0.97, 0.86)
	var sp: CPUParticles2D = emitvp.get_node("sparkles")
	sp.position = Vector2(o["x"], o["y"] - 58)

func _build_anim() -> void:
	var home: Dictionary = objects["robot_home"]
	var base := Vector2(home["x"], home["y"])
	var sp: CPUParticles2D = emitvp.get_node("sparkles"); sp.position = base + Vector2(0, -60); sp.amount = 8
	var ap := AnimationPlayer.new(); add_child(ap)
	var an := Animation.new(); an.length = 2.5; an.loop_mode = Animation.LOOP_LINEAR
	# frame track (discrete) on both sheets, pose frames @12 fps from the Aseprite tags
	var keys := [[0.0,0],[0.167,2],[0.333,4],[0.5,6],[0.583,7],[1.0,11],[1.083,12],[1.25,14],[1.417,15],[1.667,18],[1.75,19],[2.0,22],[2.25,24],[2.333,0]]
	for path in ["litvp/robot_root/ra:frame", "emitvp/robot_e_root/re:frame"]:
		pass
	var t1 := an.add_track(Animation.TYPE_METHOD); an.track_set_path(t1, NodePath("."))
	for k in keys: an.track_insert_key(t1, k[0], {"method": "_frame", "args": [k[1]]})
	# hop arc (hip height) + shadow shrink, keyed in native pixels
	var hy := [[0.0,0],[0.333,0],[0.5,-7],[0.583,-14],[0.75,-21],[0.833,-22],[0.917,-20],[1.0,-14],[1.083,-6],[1.167,0],[2.5,0]]
	var t2 := an.add_track(Animation.TYPE_METHOD); an.track_set_path(t2, NodePath("."))
	# sample the arc every 1/24 s so position is integer-snapped per video frame
	var tt := 0.0
	while tt < 2.5:
		var y := 0.0
		for i in range(hy.size() - 1):
			if tt >= hy[i][0] and tt <= hy[i + 1][0]:
				var f: float = (tt - hy[i][0]) / max(0.0001, hy[i + 1][0] - hy[i][0])
				f = f * f * (3.0 - 2.0 * f)
				y = lerp(float(hy[i][1]), float(hy[i + 1][1]), f)
		an.track_insert_key(t2, tt, {"method": "_height", "args": [y]})
		tt += 1.0 / 24.0
	var lib := AnimationLibrary.new(); lib.add_animation("hop", an); ap.add_animation_library("", lib)
	_base = base
	_frame(0); _height(0)
	ap.play("hop")

var _dbg := 0
func _process(_d: float) -> void:
	_dbg += 1
	if _dbg == 5 and mode == "still":
		lightvp.get_texture().get_image().save_png("/tmp/dbg_light.png")
		litvp.get_texture().get_image().save_png("/tmp/dbg_lit.png")
		emitvp.get_texture().get_image().save_png("/tmp/dbg_emit.png")
var _base := Vector2.ZERO
var _cur_frame := 0
func _frame(f: int) -> void:
	_cur_frame = f; _set_robot(_base + Vector2(0, _h), f)
var _h := 0.0
func _height(y: float) -> void:
	_h = y
	_set_robot(_base + Vector2(0, y), _cur_frame)
	var s: float = 1.0 + y / 40.0
	shadow_spr.position = _base + Vector2(2, -4); shadow_spr.scale = Vector2(40 * s / 128.0, 7 * s / 128.0)
