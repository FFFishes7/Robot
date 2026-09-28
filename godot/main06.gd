extends Node2D
# v06 composer: Tiled map attic06 (image layers from Aseprite + "lights" objects) -> native 384x216 lit viewport
# -> 5x nearest -> smooth overlays (window shafts, emitter glow, dust, vignette). Driven by Movie Maker.
const KIT := "/workspace/robot2d/kit/"
const NW := 448
const NH := 288
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
	var mj = JSON.parse_string(FileAccess.get_file_as_string(KIT + "tiled/attic06.json"))
	for L in mj["layers"]:
		if L.get("type") == "objectgroup":
			for o in L["objects"]: O[o["name"]] = o
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--mode="): mode = a.substr(7)
		if a.begins_with("--tl="): tl_file = a.substr(5)
	_lightmap(); _lit(); _emit(); _screen(); _pose(0); set_cam(0 if mode == "anim" else 143)

var tl_file := "timeline.json"
var glow_node: Sprite2D
var sun_nodes := []
var sky_dim: Sprite2D
var sky_dim_e: Sprite2D   # sunlight contributions (pools, mullion shadows, window glows): dimmed as the sun sets in the full cut
var glow_base := Vector2.ZERO
func _radial(o: Dictionary, parent: Node) -> void:
	var g := Gradient.new(); g.set_color(0, Color(1, 1, 1)); g.set_color(1, Color(0, 0, 0)); g.add_point(0.45, Color(0.6, 0.6, 0.6))
	var t := GradientTexture2D.new(); t.gradient = g; t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5); t.fill_to = Vector2(1.0, 0.5); t.width = 128; t.height = 128
	var s := Sprite2D.new(); s.texture = t
	s.position = Vector2(o["x"] + o["width"] / 2.0, o["y"] + o["height"] / 2.0)
	s.scale = Vector2(o["width"] / 128.0, o["height"] / 128.0)
	var v: float = prop(o, "intensity", 0.3); s.modulate = Color(v, v, v); s.material = add_mat()
	parent.add_child(s)
	if o["name"] == "robot_glow": glow_node = s; glow_base = s.position
	if o["name"].begins_with("win_glow"): sun_nodes.append(s)

func _lightmap() -> void:
	lightvp = vp(false)
	var amb := ColorRect.new(); amb.size = Vector2(NW, NH)
	var sh := Shader.new()
	sh.code = """shader_type canvas_item;
void fragment(){
  vec2 p = UV * vec2(448.0, 288.0) - vec2(56.0, 26.0);   // back to original room coords
  float v = 0.40 - 0.0008*abs(p.x-190.0) - 0.0008*max(0.0, p.y-120.0);
  if (p.y < 72.0) { v += 0.03; }
  if (p.y < 12.0) { v -= min(0.16, 0.0045*(12.0-p.y)); }   // attic rafters fall off into the dark roof
  COLOR = vec4(v, 0.0, 0.0, 1.0);
}"""
	var sm := ShaderMaterial.new(); sm.shader = sh; amb.material = sm; lightvp.add_child(amb)
	for n in ["win_glow_1", "win_glow_2", "lamp", "lamp_core", "robot_glow", "candle", "floorlamp", "floorlamp_core", "radio", "string_0", "string_1", "string_2", "string_3", "string_4", "string_5", "string_6"]: _radial(O[n], lightvp)
	for n in ["pool_1", "pool_2"]:
		var o: Dictionary = O[n]; var P := pts(o); var v: float = prop(o, "intensity", 0.5)
		var pg := Polygon2D.new(); pg.polygon = P; pg.material = add_mat()
		pg.vertex_colors = PackedColorArray([Color(v, 0, 0), Color(v, 0, 0), Color(v * 0.45, 0, 0), Color(v * 0.45, 0, 0)])
		lightvp.add_child(pg); sun_nodes.append(pg)
		# mullion shadows projected into the pool (vertical bar + horizontal bar)
		var top := (P[0] + P[1]) / 2.0; var bot := (P[3] + P[2]) / 2.0
		var hy := 0.46
		for seg in [[top, bot], [P[0].lerp(P[3], hy), P[1].lerp(P[2], hy)]]:
			var ln := Line2D.new(); ln.points = PackedVector2Array(seg); ln.width = 2.0
			ln.default_color = Color(v * 0.55, 0, 0); ln.material = add_mat(true); lightvp.add_child(ln); sun_nodes.append(ln)

const RF := KIT + "robot06/frames/"
var TL: Dictionary
var texc := {}
var rob_a: Sprite2D
var rob_front: Sprite2D
var rob_sh: Sprite2D
var rob_e1: Sprite2D
var rob_e2: Sprite2D
var rob_occ: Sprite2D
var al_lit := {}
var al_emit := {}
var front_names := {}

func ftex(n: String) -> ImageTexture:
	if not texc.has(n): texc[n] = tex(RF + n + ".png")
	return texc[n]

func _lit() -> void:
	TL = JSON.parse_string(FileAccess.get_file_as_string(RF + tl_file))
	var dj = JSON.parse_string(FileAccess.get_file_as_string(RF + "drawings.json"))
	for k in dj: front_names[k] = dj[k]["front"]; draw_info[k] = dj[k]
	var room := vp(false)
	var sm := ShaderMaterial.new(); sm.shader = load("res://shaders/light04.gdshader")
	sm.set_shader_parameter("lightmap", lightvp.get_texture())
	var alb := spr(KIT + "v06/albedo06.png"); alb.material = sm; room.add_child(alb)
	rob_sh = Sprite2D.new(); rob_sh.centered = false; rob_sh.modulate = Color(0.08, 0.03, 0.06, 0.42); room.add_child(rob_sh)
	var smr := ShaderMaterial.new(); smr.shader = sm.shader
	smr.set_shader_parameter("lightmap", lightvp.get_texture()); smr.set_shader_parameter("maxn", 8.0); smr.set_shader_parameter("point_mix", 0.75)
	rob_a = Sprite2D.new(); rob_a.centered = false; rob_a.material = smr; room.add_child(rob_a)
	litvp = vp(false)
	var rs := Sprite2D.new(); rs.centered = false; rs.texture = room.get_texture(); litvp.add_child(rs)
	litvp.add_child(spr(KIT + "v06/emit06_static.png"))
	sky_dim = spr(KIT + "v06/sky_dim06.png"); sky_dim.modulate = Color(1, 1, 1, 0); litvp.add_child(sky_dim)
	for k in ["idle", "ring", "off"]:
		var s := spr(KIT + "v06/alarm_" + k + "06.png"); litvp.add_child(s); al_lit[k] = s
	# robot drawings flagged "front" (sitting on the window seat) draw over the window glass, still lit by the lightmap
	rob_front = Sprite2D.new(); rob_front.centered = false; rob_front.material = rob_a.material; litvp.add_child(rob_front)
	rob_e1 = Sprite2D.new(); rob_e1.centered = false; litvp.add_child(rob_e1)

func _emit() -> void:
	emitvp = vp(true)
	var e := spr(KIT + "v06/emit06_static.png"); e.modulate = Color(0.75, 0.62, 0.55); emitvp.add_child(e)
	sky_dim_e = spr(KIT + "v06/sky_dim06.png"); sky_dim_e.modulate = Color(0, 0, 0, 0); emitvp.add_child(sky_dim_e)
	for k in ["idle", "ring", "off"]:
		var s := spr(KIT + "v06/alarm_" + k + "06.png"); emitvp.add_child(s); al_emit[k] = s
	rob_occ = Sprite2D.new(); rob_occ.centered = false; rob_occ.modulate = Color(0, 0, 0, 0.85); emitvp.add_child(rob_occ)   # robot blocks the glow behind it
	rob_e2 = Sprite2D.new(); rob_e2.centered = false; emitvp.add_child(rob_e2)

func _full(t: Texture2D, filt: int) -> TextureRect:
	var r := TextureRect.new(); r.texture = t; r.size = Vector2(NW * S, NH * S)
	r.stretch_mode = TextureRect.STRETCH_SCALE; r.texture_filter = filt; return r

var shaft_mats := []
var draw_info := {}
func _screen() -> void:
	world = Node2D.new(); add_child(world)
	world.add_child(_full(litvp.get_texture(), CanvasItem.TEXTURE_FILTER_NEAREST))
	var dummy := tex(KIT + "v06/albedo06.png")
	var shaft_pts := []
	for n in ["shaft_1", "shaft_2"]:
		var P := pts(O[n]); var Q := PackedVector2Array()
		for q in P: Q.append(q * S)
		shaft_pts.append(Q)
		var poly := Polygon2D.new(); poly.polygon = Q; poly.texture = dummy
		poly.uv = PackedVector2Array([Vector2(0, 0), Vector2(448, 0), Vector2(448, 288), Vector2(0, 288)])
		var m := ShaderMaterial.new(); m.shader = load("res://shaders/shaft.gdshader")
		m.set_shader_parameter("strength", 0.16); m.set_shader_parameter("tint", Vector3(1.0, 0.72, 0.52))
		poly.material = m; world.add_child(poly); shaft_mats.append(m)
	for rs in [[1.2, 0.3], [4.0, 0.35]]:
		var g := _full(emitvp.get_texture(), CanvasItem.TEXTURE_FILTER_LINEAR)
		var gm := ShaderMaterial.new(); gm.shader = load("res://shaders/glow.gdshader")
		gm.set_shader_parameter("radius", rs[0]); gm.set_shader_parameter("strength", rs[1]); g.material = gm
		world.add_child(g)
	var d := CPUParticles2D.new()
	var gt := GradientTexture2D.new(); var gg := Gradient.new(); gg.set_color(0, Color(1, 1, 1, 1)); gg.set_color(1, Color(1, 1, 1, 0))
	gt.gradient = gg; gt.fill = GradientTexture2D.FILL_RADIAL; gt.fill_from = Vector2(0.5, 0.5); gt.fill_to = Vector2(1, 0.5); gt.width = 16; gt.height = 16
	d.texture = gt; d.material = add_mat()
	var ep := PackedVector2Array(); var rng := RandomNumberGenerator.new(); rng.seed = 11
	while ep.size() < 300:
		var q := Vector2(rng.randf_range(106, 336), rng.randf_range(16, 158)) * S
		if Geometry2D.is_point_in_polygon(q, shaft_pts[0]) or Geometry2D.is_point_in_polygon(q, shaft_pts[1]): ep.append(q)
	d.emission_shape = CPUParticles2D.EMISSION_SHAPE_POINTS; d.emission_points = ep
	d.amount = 60; d.lifetime = 7.0; d.preprocess = 7.0; d.randomness = 1.0
	d.direction = Vector2(0.3, -1); d.spread = 180; d.initial_velocity_min = 2; d.initial_velocity_max = 8; d.gravity = Vector2(0, 1.5)
	d.scale_amount_min = 0.15; d.scale_amount_max = 0.34
	var cr := Gradient.new(); cr.set_color(0, Color(1, 0.85, 0.7, 0)); cr.set_color(1, Color(1, 0.85, 0.7, 0)); cr.add_point(0.3, Color(1, 0.85, 0.7, 0.7)); cr.add_point(0.7, Color(1, 0.85, 0.7, 0.5))
	d.color_ramp = cr; world.add_child(d)
	var vig := ColorRect.new(); vig.size = Vector2(1920, 1080)
	var vm := ShaderMaterial.new(); vm.shader = load("res://shaders/vignette.gdshader")
	vm.set_shader_parameter("center", Vector2(0.5, 0.5)); vm.set_shader_parameter("amount", 0.28)
	vig.material = vm; add_child(vig)

var world: Node2D
# camera (native px, top-left of the 384x216 window into the 448x288 room); moved per screen pixel like a game camera
const CAM_KEYS := [[0, Vector2(54, 20)], [64, Vector2(60, 10)], [92, Vector2(58, 8)], [128, Vector2(50, 5)], [143, Vector2(50, 5)]]
func cam_at(f: float) -> Vector2:
	if f <= CAM_KEYS[0][0]: return CAM_KEYS[0][1]
	for i in range(CAM_KEYS.size() - 1):
		var a = CAM_KEYS[i]; var b = CAM_KEYS[i + 1]
		if f <= b[0]:
			var t: float = (f - a[0]) / float(b[0] - a[0]); t = t * t * (3.0 - 2.0 * t)
			return a[1].lerp(b[1], t)
	return CAM_KEYS[-1][1]
func set_cam(f: float) -> void:
	var c := cam_at(f)
	if mode == "anim" and TL.has("cam"):
		var i: int = clamp(int(f), 0, TL["cam"].size() - 1)
		c = Vector2(TL["cam"][i][0], TL["cam"][i][1])
	c.x = clamp(c.x, 0.0, NW - 384.0); c.y = clamp(c.y, 0.0, NH - 216.0)
	world.position = -(c * S).round()
var still_name := "look4"
func _pose(f: int) -> void:
	var n: String = still_name
	var al := "idle"
	if mode == "anim":
		var i: int = clamp(f, 0, TL["robot"].size() - 1)
		n = TL["robot"][i]; al = TL["alarm"][i]
		if TL.has("rx") and glow_node: glow_node.position = glow_base + Vector2(TL["rx"][i], TL["ry"][i])
		if TL.has("sun"):
			var k: float = TL["sun"][i]
			for nd in sun_nodes: nd.modulate = Color(k, k, k)
			for m in shaft_mats: m.set_shader_parameter("strength", 0.16 * k)
			var dk: float = (1.0 - k) / 0.6
			sky_dim.modulate = Color(1, 1, 1, 0.55 * dk); sky_dim_e.modulate = Color(0, 0, 0, 0.6 * dk)
	elif mode.begins_with("pose:"):
		n = mode.substr(5)
	var fr: bool = front_names.get(n, false)
	rob_a.texture = null if fr else ftex(n + "_a")
	rob_front.texture = ftex(n + "_a") if fr else null
	rob_sh.texture = ftex(n + "_s")
	rob_e1.texture = ftex(n + "_e"); rob_e2.texture = ftex(n + "_e"); rob_occ.texture = ftex(n + "_a")
	for m in shaft_mats: m.set_shader_parameter("robmask", ftex(n + "_a"))
	var dd: Dictionary = draw_info.get(n, {"cx": 236, "by": 80})
	(rob_a.material as ShaderMaterial).set_shader_parameter("maxn", 5.0 if fr else 8.0)   # backlit against the window when seated
	(rob_a.material as ShaderMaterial).set_shader_parameter("light_uv", Vector2((dd["cx"] + 56.0) / NW, (dd["by"] + 26.0 - 3.0) / NH))
	for k in ["idle", "ring", "off"]:
		al_lit[k].visible = (k == al); al_emit[k].visible = (k == al)

const FRAME0 := 4   # first Movie Maker frames are black while viewports warm up
var _n := 0
func _process(_d: float) -> void:
	_n += 1
	if mode == "anim":
		_pose(_n - FRAME0); set_cam(_n - FRAME0)
	else:
		set_cam(143)
	if _n == 5:
		lightvp.get_texture().get_image().save_png("/tmp/dbg6_light.png")
		litvp.get_texture().get_image().save_png("/tmp/dbg6_lit.png")
		emitvp.get_texture().get_image().save_png("/tmp/dbg6_emit.png")
