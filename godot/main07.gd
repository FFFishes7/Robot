extends Node2D
# v07 composer: Tiled map attic07 + per-frame story controls from a timeline JSON (robot drawing, reminder state,
# calendar page, dust stage, sunlight, sky, room lamps, sunbeam length, camera). Native 448x288 lit world ->
# 5x nearest -> smooth overlays (sun shafts, glow, motes, vignette). Rendered with Movie Maker.
const KIT := "/workspace/robot2d/kit/"
const V := KIT + "v07/"
const RF := KIT + "robot07/frames/"
const NW := 448
const NH := 288
const S := 5
var lightvp: SubViewport
var litvp: SubViewport
var emitvp: SubViewport
var O := {}
var mode := "still"
var tl_file := "timeline07.json"
var TL: Dictionary
var texc := {}
var draw_info := {}

func tex(p: String) -> ImageTexture:
	return ImageTexture.create_from_image(Image.load_from_file(p))
func ftex(n: String) -> ImageTexture:
	if not texc.has(n): texc[n] = tex(RF + n + ".png")
	return texc[n]
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
	var mj = JSON.parse_string(FileAccess.get_file_as_string(KIT + "tiled/attic07.json"))
	for L in mj["layers"]:
		if L.get("type") == "objectgroup":
			for o in L["objects"]: O[o["name"]] = o
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--mode="): mode = a.substr(7)
		if a.begins_with("--tl="): tl_file = a.substr(5)
		if a.begins_with("--start="): start_f = int(a.substr(8))
	TL = JSON.parse_string(FileAccess.get_file_as_string(RF + tl_file))
	var dj = JSON.parse_string(FileAccess.get_file_as_string(RF + "drawings.json"))
	for k in dj: draw_info[k] = dj[k]
	_lightmap(); _lit(); _emit(); _screen(); _apply(start_f)

# ---------------------------------------------------------------- lightmap
var glow_node: Sprite2D
var glow_base := Vector2.ZERO
var lamp_nodes := []        # [node, base intensity]
var sun_glows := []
var alarm_glow: Sprite2D
var pools := []             # [Polygon2D, base points, [Line2D, Line2D], intensity]
func _radial(o: Dictionary, parent: Node) -> Sprite2D:
	var g := Gradient.new(); g.set_color(0, Color(1, 1, 1)); g.set_color(1, Color(0, 0, 0)); g.add_point(0.45, Color(0.6, 0.6, 0.6))
	var t := GradientTexture2D.new(); t.gradient = g; t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5); t.fill_to = Vector2(1.0, 0.5); t.width = 128; t.height = 128
	var s := Sprite2D.new(); s.texture = t
	s.position = Vector2(o["x"] + o["width"] / 2.0, o["y"] + o["height"] / 2.0)
	s.scale = Vector2(o["width"] / 128.0, o["height"] / 128.0)
	var v: float = prop(o, "intensity", 0.3); s.modulate = Color(v, v, v); s.material = add_mat()
	parent.add_child(s)
	var nm: String = o["name"]
	if nm == "robot_glow": glow_node = s; glow_base = s.position
	elif nm.begins_with("win_glow"): sun_glows.append([s, v])
	elif nm == "alarm_glow": alarm_glow = s
	else: lamp_nodes.append([s, v])
	return s

func _lightmap() -> void:
	lightvp = vp(false)
	var amb := ColorRect.new(); amb.size = Vector2(NW, NH)
	var sh := Shader.new()
	sh.code = """shader_type canvas_item;
uniform float amb = 1.0;
void fragment(){
  vec2 p = UV * vec2(448.0, 288.0) - vec2(56.0, 26.0);
  float v = 0.40 - 0.0008*abs(p.x-190.0) - 0.0008*max(0.0, p.y-120.0);
  if (p.y < 72.0) { v += 0.03; }
  if (p.y < 12.0) { v -= min(0.16, 0.0045*(12.0-p.y)); }
  COLOR = vec4(v * amb, 0.0, 0.0, 1.0);
}"""
	amb_mat = ShaderMaterial.new(); amb_mat.shader = sh; amb.material = amb_mat; lightvp.add_child(amb)
	for n in ["win_glow_1", "win_glow_2", "lamp", "lamp_core", "robot_glow", "candle", "floorlamp", "floorlamp_core", "radio", "alarm_glow", "string_0", "string_1", "string_2", "string_3", "string_4", "string_5", "string_6"]: _radial(O[n], lightvp)
	for n in ["pool_1", "pool_2"]:
		var o: Dictionary = O[n]; var P := pts(o); var v: float = prop(o, "intensity", 0.5)
		var pg := Polygon2D.new(); pg.polygon = P; pg.material = add_mat()
		pg.vertex_colors = PackedColorArray([Color(v, 0, 0), Color(v, 0, 0), Color(v * 0.45, 0, 0), Color(v * 0.45, 0, 0)])
		lightvp.add_child(pg)
		var lines := []
		for i in range(2):
			var ln := Line2D.new(); ln.width = 2.0; ln.default_color = Color(v * 0.55, 0, 0); ln.material = add_mat(true)
			lightvp.add_child(ln); lines.append(ln)
		pools.append([pg, P, lines, v])
var amb_mat: ShaderMaterial

func beam_pts(P: PackedVector2Array, L: float) -> PackedVector2Array:
	# sunbeam length: the far edge slides back toward the window as the sun sinks
	return PackedVector2Array([P[0], P[1], P[1].lerp(P[2], L), P[0].lerp(P[3], L)])

# ---------------------------------------------------------------- lit world
var rob: Sprite2D
var rob_sh: Sprite2D
var rob_e1: Sprite2D
var rob_e2: Sprite2D
var rob_occ: Sprite2D
var robmat: ShaderMaterial
var sky_day: Sprite2D
var sky_dim: Sprite2D
var sky_dim_e: Sprite2D
var win_e: Sprite2D
var lamps_e: Sprite2D
var al_lit := {}
var al_emit := {}
var btn: Sprite2D
var cal := {}
var dust := []
func _lit() -> void:
	var room := vp(false)
	var sm := ShaderMaterial.new(); sm.shader = load("res://shaders/light04.gdshader")
	sm.set_shader_parameter("lightmap", lightvp.get_texture())
	var alb := spr(V + "albedo07.png"); alb.material = sm; room.add_child(alb)
	for n in ["12", "13"]:
		var c := spr(V + "cal_" + n + "07.png"); c.material = sm; room.add_child(c); cal[n] = c
	btn = spr(V + "alarm_btn07.png"); btn.material = sm; room.add_child(btn)
	for k in range(8):
		var d := spr(V + "dust%d07.png" % k); d.material = sm; room.add_child(d); dust.append(d)
	rob_sh = Sprite2D.new(); rob_sh.centered = false; rob_sh.modulate = Color(0.08, 0.03, 0.06, 0.42); room.add_child(rob_sh)
	litvp = vp(false)
	var rs := Sprite2D.new(); rs.centered = false; rs.texture = room.get_texture(); litvp.add_child(rs)
	litvp.add_child(spr(V + "emit_win07.png"))
	sky_day = spr(V + "sky_day07.png"); litvp.add_child(sky_day)
	sky_dim = spr(V + "sky_dim07.png"); litvp.add_child(sky_dim)
	litvp.add_child(spr(V + "emit_lamps07.png"))
	for k in ["task", "idle", "ring", "off"]:
		var s := spr(V + "alarm_" + k + "07.png"); litvp.add_child(s); al_lit[k] = s
	robmat = ShaderMaterial.new(); robmat.shader = sm.shader
	robmat.set_shader_parameter("lightmap", lightvp.get_texture()); robmat.set_shader_parameter("maxn", 8.0); robmat.set_shader_parameter("point_mix", 0.75)
	# the robot stands in front of the wall, so it always draws over the window glass
	rob = Sprite2D.new(); rob.centered = false; rob.material = robmat; litvp.add_child(rob)
	rob_e1 = Sprite2D.new(); rob_e1.centered = false; litvp.add_child(rob_e1)

func _emit() -> void:
	emitvp = vp(true)
	win_e = spr(V + "emit_win07.png"); emitvp.add_child(win_e)
	sky_dim_e = spr(V + "sky_dim07.png"); emitvp.add_child(sky_dim_e)
	lamps_e = spr(V + "emit_lamps07.png"); emitvp.add_child(lamps_e)
	for k in ["task", "idle", "ring", "off"]:
		var s := spr(V + "alarm_" + k + "07.png"); emitvp.add_child(s); al_emit[k] = s
	rob_occ = Sprite2D.new(); rob_occ.centered = false; rob_occ.modulate = Color(0, 0, 0, 0.85); emitvp.add_child(rob_occ)
	rob_e2 = Sprite2D.new(); rob_e2.centered = false; emitvp.add_child(rob_e2)

func _full(t: Texture2D, filt: int) -> TextureRect:
	var r := TextureRect.new(); r.texture = t; r.size = Vector2(NW * S, NH * S)
	r.stretch_mode = TextureRect.STRETCH_SCALE; r.texture_filter = filt; return r

var shafts := []            # [Polygon2D, base points (screen px), material]
var motes: CPUParticles2D
var world: Node2D
func _screen() -> void:
	world = Node2D.new(); add_child(world)
	world.add_child(_full(litvp.get_texture(), CanvasItem.TEXTURE_FILTER_NEAREST))
	var dummy := tex(V + "albedo07.png")
	var shaft_pts := []
	for n in ["shaft_1", "shaft_2"]:
		var P := pts(O[n]); var Q := PackedVector2Array()
		for q in P: Q.append(q * S)
		shaft_pts.append(Q)
		var poly := Polygon2D.new(); poly.polygon = Q; poly.texture = dummy
		poly.uv = PackedVector2Array([Vector2(0, 0), Vector2(448, 0), Vector2(448, 288), Vector2(0, 288)])
		var m := ShaderMaterial.new(); m.shader = load("res://shaders/shaft.gdshader")
		m.set_shader_parameter("strength", 0.16); m.set_shader_parameter("tint", Vector3(1.0, 0.72, 0.52))
		poly.material = m; world.add_child(poly); shafts.append([poly, Q, m])
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
	d.color_ramp = cr; world.add_child(d); motes = d
	var vig := ColorRect.new(); vig.size = Vector2(1920, 1080)
	var vm := ShaderMaterial.new(); vm.shader = load("res://shaders/vignette.gdshader")
	vm.set_shader_parameter("center", Vector2(0.5, 0.5)); vm.set_shader_parameter("amount", 0.28)
	vig.material = vm; add_child(vig)

func G(key: String, i: int, d):
	if TL.has(key): return TL[key][clamp(i, 0, TL[key].size() - 1)]
	return d

var start_f := 0
func _apply(i: int) -> void:
	var n: String = G("robot", i, "look4")
	if mode.begins_with("pose:"): n = mode.substr(5)
	var dd: Dictionary = draw_info.get(n, {"cx": 236, "by": 80, "front": false})
	rob.texture = ftex(n + "_a"); rob_sh.texture = ftex(n + "_s")
	rob_e1.texture = ftex(n + "_e"); rob_e2.texture = ftex(n + "_e"); rob_occ.texture = ftex(n + "_a")
	for sh in shafts: sh[2].set_shader_parameter("robmask", ftex(n + "_a"))
	robmat.set_shader_parameter("maxn", 5.0 if dd["front"] else 8.0)
	robmat.set_shader_parameter("light_uv", Vector2((dd["cx"] + 56.0) / NW, (dd["by"] + 26.0 - 3.0) / NH))
	if glow_node: glow_node.position = glow_base + Vector2(dd["cx"] - 236.0, dd["by"] - 80.0)
	# reminder device
	var al: String = G("alarm", i, "idle")
	for k in al_lit: al_lit[k].visible = (k == al); al_emit[k].visible = (k == al)
	btn.visible = G("btn", i, 0) > 0
	var ag: float = {"task": 0.16, "ring": 0.34, "off": 0.06, "idle": 0.05}.get(al, 0.0)
	alarm_glow.modulate = Color(ag, ag * (0.45 if al == "ring" else 0.9), 0) if al != "" else Color(0, 0, 0)
	# calendar page + dust stage
	var c: String = str(G("cal", i, "12"))
	for k in cal: cal[k].visible = (k == c)
	var ds: int = G("dust", i, 0)
	for k in range(dust.size()): dust[k].visible = (k == ds)
	# light: sunlight k, beam length, pale afternoon sky, dusk sky, room lamps
	var k: float = G("sun", i, 1.0); var L: float = G("beam", i, 1.0)
	var day: float = G("day", i, 0.0); var dusk: float = G("dusk", i, 0.0); var lg: float = G("lamps", i, 1.0)
	for p in pools:
		var P: PackedVector2Array = beam_pts(p[1], L); p[0].polygon = P; p[0].modulate = Color(k, k, k)
		var top := (P[0] + P[1]) / 2.0; var bot := (P[3] + P[2]) / 2.0
		p[2][0].points = PackedVector2Array([top, bot]); p[2][1].points = PackedVector2Array([P[0].lerp(P[3], 0.46 / max(L, 0.01) if L > 0.46 else 0.9), P[1].lerp(P[2], 0.46 / max(L, 0.01) if L > 0.46 else 0.9)])
		p[2][0].modulate = Color(k, k, k); p[2][1].modulate = Color(k, k, k)
	for sh in shafts:
		sh[0].polygon = beam_pts(sh[1], 0.35 + 0.65 * L); sh[2].set_shader_parameter("strength", 0.16 * k)
	for s in sun_glows: s[0].modulate = Color(s[1] * (0.5 + 0.5 * k), s[1] * (0.5 + 0.5 * k), s[1] * (0.5 + 0.5 * k))
	for s in lamp_nodes: s[0].modulate = Color(s[1] * lg, s[1] * lg, s[1] * lg)
	lamps_e.modulate = Color(lg, lg, lg) * Color(0.8, 0.66, 0.56)
	win_e.modulate = Color(0.75, 0.62, 0.55) * (0.55 + 0.45 * k)
	sky_day.modulate = Color(1, 1, 1, day); sky_dim.modulate = Color(1, 1, 1, 0.55 * dusk); sky_dim_e.modulate = Color(0, 0, 0, 0.6 * dusk)
	amb_mat.set_shader_parameter("amb", G("amb", i, 1.0))
	motes.modulate = Color(1, 1, 1, clamp(k, 0.0, 1.0))
	# camera
	var cam = G("cam", i, [50, 5])
	var cv := Vector2(clamp(float(cam[0]), 0.0, NW - 384.0), clamp(float(cam[1]), 0.0, NH - 216.0))
	world.position = -(cv * S).round()

const FRAME0 := 4
var _n := 0
func _process(_d: float) -> void:
	_n += 1
	_apply(start_f + max(0, _n - FRAME0) if mode == "anim" else start_f)
