// Room lighting on the native grid: light value quantised into bands, 2x2 checker at band transitions.
shader_type canvas_item;
uniform sampler2D lightmap : filter_nearest;
uniform vec3 tints[11];
uniform vec3 adds[11];
void fragment() {
	vec4 a = texture(TEXTURE, UV);
	float L = texture(lightmap, UV).r * 12.0;
	float n = floor(L);
	float f = L - n;
	ivec2 p = ivec2(floor(FRAGCOORD.xy));
	if (f > 0.68) { n += 1.0; }
	else if (f > 0.32 && ((p.x + p.y) % 2 == 0)) { n += 1.0; }
	int i = clamp(int(n), 0, 10);
	COLOR = vec4(a.rgb * tints[i] + adds[i] / 255.0, a.a);
}
