// Sun shaft: additive soft wedge (UV.x across, UV.y along), smooth edges + faint streaks.
shader_type canvas_item;
render_mode blend_add;
uniform vec3 tint = vec3(1.0, 0.86, 0.58);
uniform float strength = 0.28;
uniform float time_off = 0.0;
uniform sampler2D robmask : filter_nearest;   // robot albedo (world-sized); the haze thins over the robot so it stays readable
uniform vec2 world_px = vec2(2240.0, 1440.0);
varying vec2 wpos;
void vertex() { wpos = VERTEX; }
void fragment() {
	float edge = smoothstep(0.0, 0.35, UV.x) * smoothstep(1.0, 0.65, UV.x);
	float along = (1.0 - 0.45 * UV.y) * smoothstep(0.0, 0.08, UV.y) * smoothstep(1.0, 0.85, UV.y);
	float streak = 0.78 + 0.22 * sin(UV.x * 23.0 + time_off);
	float m = texture(robmask, wpos / world_px).a;
	COLOR = vec4(tint * edge * along * streak * strength * (1.0 - 0.65 * m), 1.0);
}
