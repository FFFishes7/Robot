// Emitter glow: soft gaussian of a native-res texture, added on top of the 5x image (off-grid, smooth).
shader_type canvas_item;
render_mode blend_add;
uniform float radius = 2.0;        // in native pixels
uniform float strength = 0.8;
uniform float threshold = 0.0;     // only for the "hot" pass
uniform sampler2D mask : filter_nearest;
uniform bool use_mask = false;
void fragment() {
	vec2 px = 1.0 / vec2(textureSize(TEXTURE, 0));
	vec3 acc = vec3(0.0); float wsum = 0.0;
	for (int y = -4; y <= 4; y++) {
		for (int x = -4; x <= 4; x++) {
			vec2 o = vec2(float(x), float(y)) * radius * 0.5;
			float w = exp(-dot(o, o) / (2.0 * radius * radius));
			vec2 uv = UV + o * px;
			vec4 c = texture(TEXTURE, uv);
			float k = c.a;
			if (use_mask) { k *= step(0.72, texture(mask, uv).r); }
			float lum = dot(c.rgb, vec3(0.299, 0.587, 0.114));
			k *= smoothstep(threshold, threshold + 0.08, lum);
			acc += c.rgb * k * w; wsum += w;
		}
	}
	COLOR = vec4(acc / wsum * strength, 1.0);
}
