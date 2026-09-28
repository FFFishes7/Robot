extends Node2D
# v04 composer: Tiled map attic05 (image layers from Aseprite + "lights" objects) -> native 384x216 lit viewport
# -> 5x nearest -> smooth overlays (window shafts, emitter glow, dust, vignette). Driven by Movie Maker.
const KIT := "/workspace/robot2d/kit/"
const NW := 384
const NH := 216
const S := 5
var lightvp: SubViewport
var litvp: SubViewport
var emitvp: SubViewport
var O := {}
var poses: Array = []
var eyes_lit: Array = []
var eyes_emit: Array = []
var shadow: Sprite2D
var mode := "still"

func tex(p: String) -> ImageTexture:
	return ImageTexture.create_from_image(Image.load_from_file(p))

func vp(transparent: bool) -> SubViewport:
	var v := SubViewport.new(); v.size = Vector2i(NW, NH); v.transparent_bg = transparent
	v.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	v.snap_2d_transforms_to_pixel = true
	v.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(v); return v

func spr(p: String) -> Sprite2D:
	var s := Sprite2D.new(); s.centered = false; s.texture = tex(p); return s

func pts(o: Dictionary) -> PackedVector2Array:
	var r := PackedVector2Array()
	for q in o["polygon"]: r.append(Vector2(o["x"] + q["x"], o["y"] + q["y"]))
	return r

func prop(o: Dictionary, k: String, d):
	if o.has("properties"):
		for p in o["properties"]:
			if p["name"] == k: return p["value"]
	return d

func add_mat(sub := false) -> CanvasItemMaterial:
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_SUB if sub else CanvasItemMaterial.BLEND_MODE_ADD
	return m

func _ready() -> void:
	var mj = JSON.parse_string(FileAccess.get_file_as_string(KIT + "tiled/attic05.json"))
	for L in mj["layers"]:
		if L.get("type") == "objectgroup":
			for o in L["objects"]: O[o["name"]] = o
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--mode="): mode = a.substr(7)
	_lightmap(); _lit(); _emit(); _screen(); _pose(0)

func _radial(o: Dictionary, parent: Node) -> void:
	var g := Gradient.new(); g.set_color(0, Color(1, 1, 1)); g.set_color(1, Color(0, 0, 0)); g.add_point(0.45, Color(0.6, 0.6, 0.6))
	var t := GradientTexture2D.new(); t.gradient = g; t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5); t.fill_to = Vector2(1.0, 0.5); t.width = 128; t.height = 128
	var s := Sprite2D.new(); s.texture = t
	s.position = Vector2(o["x"] + o["width"] / 2.0, o["y"] + o["height"] / 2.0)
	s.scale = Vector2(o["width"] / 128.0, o["height"] / 128.0)
	var v: float = prop(o, "intensity", 0.3); s.modulate = Color(v, v, v); s.material = add_mat()
	parent.add_child(s)

func _lightmap() -> void:
	lightvp = vp(false)
	var amb := ColorRect.new(); amb.size = Vector2(NW, NH)
	var sh := Shader.new()
	sh.code = """shader_type canvas_item;
void fragment(){
  vec2 p = UV * vec2(384.0, 216.0);
  float v = 0.40 - 0.0008*abs(p.x-190.0) - 0.0008*max(0.0, p.y-120.0);
  if (p.y < 72.0) { v += 0.03; }
  COLOR = vec4(v, 0.0, 0.0, 1.0);
}"""
	var sm := ShaderMaterial.new(); sm.shader = sh; amb.material = sm; lightvp.add_child(amb)
	for n in ["win_glow_1", "win_glow_2", "lamp", "lamp_core", "robot_glow", "candle"]: _radial(O[n], lightvp)
	for n in ["pool_1", "pool_2"]:
		var o: Dictionary = O[n]; var P := pts(o); var v: float = prop(o, "intensity", 0.5)
		var pg := Polygon2D.new(); pg.polygon = P; pg.material = add_mat()
		pg.vertex_colors = PackedColorArray([Color(v, 0, 0), Color(v, 0, 0), Color(v * 0.45, 0, 0), Color(v * 0.45, 0, 0)])
		lightvp.add_child(pg)
		# mullion shadows projected into the pool (vertical bar + horizontal bar)
		var top := (P[0] + P[1]) / 2.0; var bot := (P[3] + P[2]) / 2.0
		var hy := 0.46
		for seg in [[top, bot], [P[0].lerp(P[3], hy), P[1].lerp(P[2], hy)]]:
			var ln := Line2D.new(); ln.points = PackedVector2Array(seg); ln.width = 2.0
			ln.default_color = Color(v * 0.55, 0, 0); ln.material = add_mat(true); lightvp.add_child(ln)

func _lit() -> void:
	var room := vp(false)
	var sm := ShaderMaterial.new(); sm.shader = load("res://shaders/light04.gdshader")
	sm.set_shader_parameter("lightmap", lightvp.get_texture())
	var alb := spr(KIT + "v05/albedo05.png"); alb.material = sm; room.add_child(alb)
	shadow = spr(KIT + "v05/layer_robot_shadow.png"); shadow.modulate = Color(0.08, 0.03, 0.06, 0.4); room.add_child(shadow)
	for n in ["robot05", "layer_robot_sweep1", "layer_robot_sweep2", "layer_robot_sweep3", "layer_robot_sweep4"]:
		var s := spr(KIT + "v05/" + n + ".png"); s.material = sm; room.add_child(s); poses.append(s)
	litvp = vp(false)
	var rs := Sprite2D.new(); rs.centered = false; rs.texture = room.get_texture(); litvp.add_child(rs)
	litvp.add_child(spr(KIT + "v05/emit05.png"))
	for n in ["robot_emit05", "robot_emit05_look_blink", "layer_robot_sweep1_emit", "layer_robot_sweep2_emit", "layer_robot_sweep3_emit", "layer_robot_sweep4_emit", "alarm_ring05"]:
		var s := spr(KIT + "v05/" + n + ".png"); litvp.add_child(s); eyes_lit.append(s)

func _emit() -> void:
	emitvp = vp(true)
	var e := spr(KIT + "v05/emit05.png"); e.modulate = Color(0.75, 0.62, 0.55); emitvp.add_child(e)
	for n in ["robot_emit05", "robot_emit05_look_blink", "layer_robot_sweep1_emit", "layer_robot_sweep2_emit", "layer_robot_sweep3_emit", "layer_robot_sweep4_emit", "alarm_ring05"]:
		var s := spr(KIT + "v05/" + n + ".png"); emitvp.add_child(s); eyes_emit.append(s)

func _full(t: Texture2D, filt: int) -> TextureRect:
	var r := TextureRect.new(); r.texture = t; r.size = Vector2(NW * S, NH * S)
	r.stretch_mode = TextureRect.STRETCH_SCALE; r.texture_filter = filt; return r

func _screen() -> void:
	add_child(_full(litvp.get_texture(), CanvasItem.TEXTURE_FILTER_NEAREST))
	var dummy := tex(KIT + "v05/albedo05.png")
	var shaft_pts := []
	for n in ["shaft_1", "shaft_2"]:
		var P := pts(O[n]); var Q := PackedVector2Array()
		for q in P: Q.append(q * S)
		shaft_pts.append(Q)
		var poly := Polygon2D.new(); poly.polygon = Q; poly.texture = dummy
		poly.uv = PackedVector2Array([Vector2(0, 0), Vector2(384, 0), Vector2(384, 216), Vector2(0, 216)])
		var m := ShaderMaterial.new(); m.shader = load("res://shaders/shaft.gdshader")
		m.set_shader_parameter("strength", 0.16); m.set_shader_parameter("tint", Vector3(1.0, 0.72, 0.52))
		poly.material = m; add_child(poly)
	for rs in [[1.2, 0.3], [4.0, 0.35]]:
		var g := _full(emitvp.get_texture(), CanvasItem.TEXTURE_FILTER_LINEAR)
		var gm := ShaderMaterial.new(); gm.shader = load("res://shaders/glow.gdshader")
		gm.set_shader_parameter("radius", rs[0]); gm.set_shader_parameter("strength", rs[1]); g.material = gm
		add_child(g)
	var d := CPUParticles2D.new()
	var gt := GradientTexture2D.new(); var gg := Gradient.new(); gg.set_color(0, Color(1, 1, 1, 1)); gg.set_color(1, Color(1, 1, 1, 0))
	gt.gradient = gg; gt.fill = GradientTexture2D.FILL_RADIAL; gt.fill_from = Vector2(0.5, 0.5); gt.fill_to = Vector2(1, 0.5); gt.width = 16; gt.height = 16
	d.texture = gt; d.material = add_mat()
	var ep := PackedVector2Array(); var rng := RandomNumberGenerator.new(); rng.seed = 11
	while ep.size() < 300:
		var q := Vector2(rng.randf_range(50, 280), rng.randf_range(30, 172)) * S
		if Geometry2D.is_point_in_polygon(q, shaft_pts[0]) or Geometry2D.is_point_in_polygon(q, shaft_pts[1]): ep.append(q)
	d.emission_shape = CPUParticles2D.EMISSION_SHAPE_POINTS; d.emission_points = ep
	d.amount = 60; d.lifetime = 7.0; d.preprocess = 7.0; d.randomness = 1.0
	d.direction = Vector2(0.3, -1); d.spread = 180; d.initial_velocity_min = 2; d.initial_velocity_max = 8; d.gravity = Vector2(0, 1.5)
	d.scale_amount_min = 0.15; d.scale_amount_max = 0.34
	var cr := Gradient.new(); cr.set_color(0, Color(1, 0.85, 0.7, 0)); cr.set_color(1, Color(1, 0.85, 0.7, 0)); cr.add_point(0.3, Color(1, 0.85, 0.7, 0.7)); cr.add_point(0.7, Color(1, 0.85, 0.7, 0.5))
	d.color_ramp = cr; add_child(d)
	var vig := ColorRect.new(); vig.size = Vector2(NW * S, NH * S)
	var vm := ShaderMaterial.new(); vm.shader = load("res://shaders/vignette.gdshader")
	vm.set_shader_parameter("center", Vector2(0.5, 0.5)); vm.set_shader_parameter("amount", 0.28)
	vig.material = vm; add_child(vig)

# story loop, 72 frames @24 fps: sweeping (8 fps) -> sunset stops him, broom upright, looks up; reminder rings
func _pose(f: int) -> void:
	var c := f % 72
	var p := 0; var e := 0; var ring := false
	if c < 32:
		var k: int = (c / 3) % 4
		p = 1 + k; e = 2 + k
	else:
		if c == 50 or c == 51: e = 1
		ring = c >= 44 and ((c / 4) % 2 == 0)
	for i in 5: poses[i].visible = (i == p)
	for i in 6:
		eyes_lit[i].visible = (i == e); eyes_emit[i].visible = (i == e)
	eyes_lit[6].visible = ring; eyes_emit[6].visible = ring

var _n := 0
func _process(_d: float) -> void:
	_n += 1
	if mode == "anim": _pose(_n)
	if _n == 5:
		lightvp.get_texture().get_image().save_png("/tmp/dbg5_light.png")
		litvp.get_texture().get_image().save_png("/tmp/dbg5_lit.png")
		emitvp.get_texture().get_image().save_png("/tmp/dbg5_emit.png")
