shader_type canvas_item;
uniform vec2 center = vec2(0.42, 0.45);
uniform float amount = 0.26;
void fragment() {
	vec2 d = UV - center;
	float v = clamp(amount * (d.x * d.x * 1.3 + d.y * d.y * 1.6) * 3.2, 0.0, 0.6);
	COLOR = vec4(0.05, 0.02, 0.06, v);
}
