// v04 dusk lighting on the native grid: light value -> 13 quantised bands (2x2 checker at transitions)
// -> ramp from cool dusk purple (shadow) through neutral to warm window/lamp gold.
shader_type canvas_item;
uniform sampler2D lightmap : filter_nearest;
uniform float maxn = 12.0;
uniform vec2 light_uv = vec2(0.5);   // sprites: sample the light at the feet so the whole body is lit as one object
uniform float point_mix = 0.0;   // cap on the light band (the robot uses a lower cap so it reads inside the sun pool)
const int N = 7;
const vec3 T[7] = vec3[](vec3(0.34,0.30,0.50), vec3(0.50,0.44,0.64), vec3(0.66,0.58,0.72), vec3(0.84,0.74,0.76),
                         vec3(1.00,0.86,0.74), vec3(1.14,0.95,0.72), vec3(1.28,1.04,0.74));
const vec3 A[7] = vec3[](vec3(0.0), vec3(0.0), vec3(0.0), vec3(0.0), vec3(6.0,2.0,0.0), vec3(18.0,8.0,0.0), vec3(34.0,18.0,4.0));
void fragment() {
	vec4 a = texture(TEXTURE, UV);
	float L = clamp(mix(texture(lightmap, UV).r, texture(lightmap, light_uv).r, point_mix), 0.0, 1.0) * 12.0;
	float n = floor(L); float f = L - n;
	ivec2 p = ivec2(floor(FRAGCOORD.xy));
	if (f > 0.7) { n += 1.0; } else if (f > 0.3 && ((p.x + p.y) % 2 == 0)) { n += 1.0; }
	float x = clamp(n, 0.0, maxn) / 2.0;
	int i = int(floor(x)); int j = min(i + 1, N - 1); float t = x - float(i);
	vec3 tint = mix(T[i], T[j], t); vec3 add = mix(A[i], A[j], t);
	COLOR = vec4(a.rgb * tint + add / 255.0, a.a);
}
